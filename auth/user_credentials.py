import hashlib
import base64
import json
import os
import time


class UserCredentials:
    def __init__(self):
        self.credentials_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "app_cache",
            "credentials.json"
        )
        try:
            cache_dir = os.path.dirname(self.credentials_file)
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir, exist_ok=True)
                
            # Проверяем доступность директории для записи
            test_file = os.path.join(cache_dir, '.test')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                print(f"Предупреждение: директория app_cache может быть недоступна для записи: {str(e)}")
                
            # Создаем файл credentials.json если его нет
            if not os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'w') as f:
                    json.dump({"credentials": []}, f)
                    
        except Exception as e:
            print(f"Ошибка инициализации хранилища учетных данных: {str(e)}")
            raise ValueError("Не удалось инициализировать хранилище учетных данных. Проверьте права доступа к папке app_cache.")

    def _hash_pin(self, pin: str) -> str:
        """Хеширует PIN-код"""
        salt = b"fixed_salt_for_pin"  # В реальном приложении следует использовать случайную соль
        return base64.b64encode(
            hashlib.pbkdf2_hmac('sha256', pin.encode(), salt, 100000)
        ).decode()

    def save_credentials(self, username: str, pin: str) -> None:
        """Сохраняет учетные данные"""
        if not username or not pin:
            raise ValueError("Имя пользователя и PIN-код обязательны")
            
        try:
            # Загружаем существующие данные
            data = {"credentials": []}
            if os.path.exists(self.credentials_file):
                try:
                    with open(self.credentials_file, 'r') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Ошибка чтения файла учетных данных: {str(e)}")
                    # Если файл поврежден, создаем новый
                    data = {"credentials": []}

            # Хешируем PIN
            hashed_pin = self._hash_pin(pin)
            
            # Добавляем новые учетные данные
            timestamp = int(time.time())
            new_credentials = {
                "username": username,
                "pin_hash": hashed_pin,
                "timestamp": timestamp
            }
            
            # Обновляем или добавляем учетные данные
            credentials_list = data.get("credentials", [])
            updated = False
            
            for cred in credentials_list:
                if cred["username"] == username:
                    cred.update(new_credentials)
                    updated = True
                    break
            
            if not updated:
                credentials_list.append(new_credentials)
            
            # Сохраняем обновленные данные
            try:
                # Сначала пишем во временный файл
                temp_file = f"{self.credentials_file}.tmp"
                with open(temp_file, 'w') as f:
                    json.dump(data, f, indent=2)
                # Если запись прошла успешно, заменяем основной файл
                os.replace(temp_file, self.credentials_file)
            except Exception as e:
                print(f"Ошибка сохранения учетных данных: {str(e)}")
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                raise ValueError("Не удалось сохранить учетные данные")
                
        except Exception as e:
            print(f"Ошибка сохранения учетных данных: {str(e)}")
            raise ValueError(f"Не удалось сохранить учетные данные: {str(e)}")

    def verify_credentials(self, username: str, pin: str) -> bool:
        """Проверяет учетные данные"""
        try:
            if not os.path.exists(self.credentials_file):
                return False

            with open(self.credentials_file, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    return False

            hashed_pin = self._hash_pin(pin)
            
            for cred in data.get("credentials", []):
                if (cred["username"] == username and 
                    cred["pin_hash"] == hashed_pin):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Ошибка проверки учетных данных: {str(e)}")
            return False

    def clear_old_credentials(self) -> None:
        """Очищает старые учетные данные"""
        try:
            if not os.path.exists(self.credentials_file):
                return

            with open(self.credentials_file, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    return

            # Оставляем только последние учетные данные для каждого пользователя
            unique_users = {}
            for cred in data.get("credentials", []):
                username = cred["username"]
                timestamp = cred.get("timestamp", 0)
                
                if (username not in unique_users or 
                    timestamp > unique_users[username]["timestamp"]):
                    unique_users[username] = cred

            # Сохраняем обновленные данные
            data["credentials"] = list(unique_users.values())
            with open(self.credentials_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Ошибка очистки старых учетных данных: {str(e)}")

    def get_saved_username(self) -> str | None:
        """Возвращает последнее сохраненное имя пользователя"""
        try:
            if not os.path.exists(self.credentials_file):
                return None

            with open(self.credentials_file, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    return None

            # Находим самую последнюю запись
            latest_cred = None
            latest_timestamp = 0
            
            for cred in data.get("credentials", []):
                timestamp = cred.get("timestamp", 0)
                if timestamp > latest_timestamp:
                    latest_timestamp = timestamp
                    latest_cred = cred

            return latest_cred["username"] if latest_cred else None
            
        except Exception as e:
            print(f"Ошибка получения имени пользователя: {str(e)}")
            return None 