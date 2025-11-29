import os
from logger_config import get_logger

logger = get_logger(__name__)
import json
from cryptography.fernet import Fernet

class SecretManager:
    def __init__(self, key_file="master.key", secrets_file="secrets.enc"):
        self.key_file = key_file
        self.secrets_file = secrets_file
        self.key = self._load_or_generate_key()

    def _load_or_generate_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            return key

    def _get_fernet(self):
        return Fernet(self.key)

    def save_secrets(self, secrets: dict):
        f = self._get_fernet()
        data = json.dumps(secrets).encode()
        encrypted = f.encrypt(data)
        with open(self.secrets_file, "wb") as file:
            file.write(encrypted)

    def load_secrets(self) -> dict:
        if not os.path.exists(self.secrets_file):
            return {}
        
        f = self._get_fernet()
        try:
            with open(self.secrets_file, "rb") as file:
                encrypted = file.read()
            decrypted = f.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error("Error loading secrets", extra={'extra_data': {'error': str(e)}}, exc_info=True)
            return {}

    def get_secret(self, key: str):
        secrets = self.load_secrets()
        return secrets.get(key)

    def set_secret(self, key: str, value: str):
        secrets = self.load_secrets()
        secrets[key] = value
        self.save_secrets(secrets)
