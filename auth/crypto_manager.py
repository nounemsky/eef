import base64
import json
import secrets
import time
import os
from typing import Tuple
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import argon2
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import ctypes


class SecureBytes:
    """Класс для безопасного хранения байтов в памяти"""
    def __init__(self, data: bytes):
        self._size = len(data)
        # Выделяем защищенную память
        self._buf = ctypes.create_string_buffer(self._size)
        self._buf.raw = data
        
    def __del__(self):
        """Безопасно очищаем память при удалении"""
        if hasattr(self, '_buf'):
            # Перезаписываем случайными данными
            self._buf.raw = os.urandom(self._size)
            # Очищаем нулями
            ctypes.memset(self._buf, 0, self._size)
            
    @property
    def value(self) -> bytes:
        """Получить значение"""
        return self._buf.raw
        
    def clear(self):
        """Явная очистка памяти"""
        self.__del__()


class CryptoManagerV2:
    VERSION = 3  # Увеличиваем версию из-за изменений в формате
    
    def __init__(self, login: str, password: str):
        # Генерируем случайную соль для каждого экземпляра
        self._instance_salt = SecureBytes(secrets.token_bytes(32))
        # Создаем ключ для защиты данных в памяти
        self._memory_key = SecureBytes(self._derive_memory_key(login, password))
        # Шифруем комбинацию логина и пароля для хранения в памяти
        self._encrypted_secret = self._encrypt_memory(
            f"{login}::{password}".encode()
        )
        self.backend = default_backend()
        self.kdf_config = {
            "version": self.VERSION,
            "algorithm": "Argon2id",
            "memory_cost": 102400,  # 100 MB
            "time_cost": 3,
            "parallelism": 4,
            "salt_size": 32,
            "key_length": 64
        }

    def _derive_memory_key(self, login: str, password: str) -> bytes:
        """Создает ключ для защиты данных в памяти"""
        kdf = Scrypt(
            salt=self._instance_salt.value,
            length=32,
            n=2**14,
            r=8,
            p=1,
            backend=default_backend()
        )
        return kdf.derive((login + password).encode())

    def _encrypt_memory(self, data: bytes) -> bytes:
        """Шифрует данные для хранения в памяти"""
        aesgcm = AESGCM(self._memory_key.value)
        nonce = secrets.token_bytes(12)
        return nonce + aesgcm.encrypt(nonce, data, None)

    def _decrypt_memory(self, data: bytes) -> bytes:
        """Расшифровывает данные из памяти"""
        aesgcm = AESGCM(self._memory_key.value)
        nonce, ciphertext = data[:12], data[12:]
        return aesgcm.decrypt(nonce, ciphertext, None)

    def _get_secret(self) -> bytes:
        """Безопасно получает секрет из памяти"""
        return self._decrypt_memory(self._encrypted_secret)

    def _derive_keys(self, salt: bytes) -> Tuple[bytes, bytes]:
        """Метод получения ключей с Argon2"""
        ph = argon2.PasswordHasher(
            memory_cost=self.kdf_config["memory_cost"],
            time_cost=self.kdf_config["time_cost"],
            parallelism=self.kdf_config["parallelism"],
            hash_len=self.kdf_config["key_length"],
            salt_len=self.kdf_config["salt_size"]
        )
        # Используем защищенный секрет
        full_key = ph.hash(self._get_secret(), salt=salt).encode()
        hash_part = full_key.split(b'$')[-1]
        # Создаем защищенные копии ключей
        enc_key = SecureBytes(hash_part[:32])
        auth_key = SecureBytes(hash_part[32:64])
        return enc_key.value, auth_key.value

    def encrypt_data(self, data: dict) -> str:
        # Генерируем соль и nonce
        salt = secrets.token_bytes(self.kdf_config["salt_size"])
        nonce = secrets.token_bytes(12)

        # Получаем ключи
        enc_key, auth_key = self._derive_keys(salt)

        try:
            # Шифруем данные
            cipher = Cipher(
                algorithms.AES(enc_key),
                modes.GCM(nonce),
                backend=self.backend
            )
            encryptor = cipher.encryptor()

            # Добавляем associated data
            associated_data = f"v{self.VERSION}:{int(time.time())}".encode()
            encryptor.authenticate_additional_data(associated_data)

            # Шифруем данные
            ciphertext = encryptor.update(json.dumps(data).encode()) + encryptor.finalize()

            # Формируем результат
            result = {
                "config": self.kdf_config,
                "salt": base64.b64encode(salt).decode(),
                "nonce": base64.b64encode(nonce).decode(),
                "tag": base64.b64encode(encryptor.tag).decode(),
                "associated_data": base64.b64encode(associated_data).decode(),
                "ciphertext": base64.b64encode(ciphertext).decode()
            }

            # Добавляем HMAC
            h = hmac.HMAC(auth_key, hashes.SHA3_256(), backend=self.backend)
            h.update(json.dumps(result, sort_keys=True).encode())
            result["hmac"] = base64.b64encode(h.finalize()).decode()

            return json.dumps(result)
        finally:
            # Очищаем ключи из памяти
            del enc_key
            del auth_key

    def decrypt_data(self, encrypted_data: str) -> dict:
        if not encrypted_data:
            return {"passwords": [], "categories": []}
            
        enc_key = None
        auth_key = None
        
        try:
            data = json.loads(encrypted_data)
            version = data.get("config", {}).get("version", 2)
            
            if version < 2:
                raise ValueError(f"Неподдерживаемая версия формата шифрования: {version}")

            # Декодируем данные
            salt = base64.b64decode(data["salt"])
            nonce = base64.b64decode(data["nonce"])
            tag = base64.b64decode(data["tag"])
            ciphertext = base64.b64decode(data["ciphertext"])
            associated_data = base64.b64decode(data["associated_data"])

            # Получаем ключи
            enc_key, auth_key = self._derive_keys(salt)

            try:
                # Проверяем HMAC
                h = hmac.HMAC(auth_key, hashes.SHA3_256(), backend=self.backend)
                hmac_data = data.copy()
                stored_hmac = base64.b64decode(hmac_data.pop("hmac"))
                h.update(json.dumps(hmac_data, sort_keys=True).encode())
                h.verify(stored_hmac)

                # Расшифровываем
                cipher = Cipher(algorithms.AES(enc_key), modes.GCM(nonce, tag), backend=self.backend)
                decryptor = cipher.decryptor()
                decryptor.authenticate_additional_data(associated_data)

                decrypted = decryptor.update(ciphertext) + decryptor.finalize()
                result = json.loads(decrypted.decode())
                
                if not isinstance(result, dict):
                    raise ValueError("Невалидный формат данных")
                if "passwords" not in result or "categories" not in result:
                    result = {"passwords": [], "categories": []}
                    
                return result
                
            except InvalidTag:
                raise ValueError("Ошибка проверки целостности данных")
                
        except Exception as e:
            print(f"Ошибка расшифровки данных: {str(e)}")
            return {"passwords": [], "categories": []}
            
        finally:
            # Очищаем ключи из памяти
            if enc_key:
                del enc_key
            if auth_key:
                del auth_key
            # Принудительно вызываем сборщик мусора
            import gc
            gc.collect()

    def __del__(self):
        """Очищаем все секретные данные при удалении объекта"""
        try:
            if hasattr(self, '_instance_salt'):
                self._instance_salt.clear()
                del self._instance_salt
            if hasattr(self, '_memory_key'):
                self._memory_key.clear()
                del self._memory_key
            if hasattr(self, '_encrypted_secret'):
                # Перезаписываем случайными данными
                self._encrypted_secret = os.urandom(len(self._encrypted_secret))
                del self._encrypted_secret
        except:
            pass
        finally:
            # Принудительно вызываем сборщик мусора
            import gc
            gc.collect() 