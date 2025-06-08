import base64
import json
import secrets
import time
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature, InvalidTag
import argon2


class CryptoManagerV2:
    VERSION = 2
    
    def __init__(self, login: str, password: str):
        self.combined_secret = f"{login}::{password}".encode()
        self.backend = default_backend()
        self.kdf_config = {
            "version": self.VERSION,
            "algorithm": "Argon2id",
            "memory_cost": 102400,  # 100 MB
            "time_cost": 3,  # 3 итерации
            "parallelism": 4,
            "salt_size": 32,
            "key_length": 64
        }

    def _derive_keys(self, salt: bytes) -> tuple[bytes, bytes]:
        """Метод получения ключей с Argon2"""
        ph = argon2.PasswordHasher(
            memory_cost=self.kdf_config["memory_cost"],
            time_cost=self.kdf_config["time_cost"],
            parallelism=self.kdf_config["parallelism"],
            hash_len=self.kdf_config["key_length"],
            salt_len=self.kdf_config["salt_size"]
        )
        full_key = ph.hash(self.combined_secret, salt=salt).encode()
        hash_part = full_key.split(b'$')[-1]
        return hash_part[:32], hash_part[32:64]

    def encrypt_data(self, data: dict) -> str:
        # Генерируем соль и nonce
        salt = secrets.token_bytes(self.kdf_config["salt_size"])
        nonce = secrets.token_bytes(12)  # 96 бит для GCM

        # Получаем ключи
        enc_key, auth_key = self._derive_keys(salt)

        # Шифруем данные
        cipher = Cipher(
            algorithms.AES(enc_key),
            modes.GCM(nonce),
            backend=self.backend
        )
        encryptor = cipher.encryptor()

        # Добавляем associated data для дополнительной защиты
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

        # Добавляем HMAC всего сообщения для дополнительной проверки целостности
        h = hmac.HMAC(auth_key, hashes.SHA3_256(), backend=self.backend)
        h.update(json.dumps(result, sort_keys=True).encode())
        result["hmac"] = base64.b64encode(h.finalize()).decode()

        return json.dumps(result)

    def decrypt_data(self, encrypted_data: str) -> dict:
        if not encrypted_data:
            return {"passwords": [], "categories": []}
            
        try:
            data = json.loads(encrypted_data)
            version = data.get("config", {}).get("version", 2)
            
            if version != 2:
                raise ValueError(f"Неподдерживаемая версия формата шифрования: {version}")

            # Декодируем данные
            salt = base64.b64decode(data["salt"])
            nonce = base64.b64decode(data["nonce"])
            tag = base64.b64decode(data["tag"])
            ciphertext = base64.b64decode(data["ciphertext"])
            associated_data = base64.b64decode(data["associated_data"])

            enc_key, auth_key = self._derive_keys(salt)

            # Проверяем HMAC
            h = hmac.HMAC(auth_key, hashes.SHA3_256(), backend=self.backend)
            hmac_data = data.copy()
            stored_hmac = base64.b64decode(hmac_data.pop("hmac"))
            h.update(json.dumps(hmac_data, sort_keys=True).encode())
            try:
                h.verify(stored_hmac)
            except InvalidSignature:
                raise ValueError("Ошибка целостности данных!")

            # Расшифровываем
            cipher = Cipher(algorithms.AES(enc_key), modes.GCM(nonce, tag), backend=self.backend)
            decryptor = cipher.decryptor()
            decryptor.authenticate_additional_data(associated_data)

            try:
                decrypted = decryptor.update(ciphertext) + decryptor.finalize()
                result = json.loads(decrypted.decode())
                if not isinstance(result, dict):
                    raise ValueError("Невалидный формат данных")
                if "passwords" not in result or "categories" not in result:
                    result = {"passwords": [], "categories": []}
                return result
            except InvalidTag:
                raise ValueError("Ошибка аутентификации данных!")
        except json.JSONDecodeError:
            return {"passwords": [], "categories": []}
        except Exception as e:
            print(f"Ошибка расшифровки: {str(e)}")
            return {"passwords": [], "categories": []} 