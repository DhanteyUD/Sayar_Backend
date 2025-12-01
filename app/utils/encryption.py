import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class EncryptionService:
    def __init__(self, password: str, salt: bytes = None):
        """
        Initialize encryption service

        Args:
            password: A strong password for key derivation
            salt: Optional salt (if None, will generate new one)
        """
        self.password = password.encode()
        self.salt = salt or os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        self.fernet = Fernet(key)

    def encrypt(self, data: str) -> str | None:
        if data is None:
            return None
        encrypted_data = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt(self, encrypted_data: str) -> str | None:
        if encrypted_data is None:
            return None
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.fernet.decrypt(encrypted_bytes)
        return decrypted_data.decode()

    def get_salt(self) -> str:
        return base64.urlsafe_b64encode(self.salt).decode()


def get_encryption_service():
    encryption_password = os.getenv('ENCRYPTION_PASSWORD')
    if not encryption_password:
        raise ValueError("ENCRYPTION_PASSWORD environment variable is required")

    salt = os.getenv('ENCRYPTION_SALT')
    if salt:
        salt = base64.urlsafe_b64decode(salt.encode())

    return EncryptionService(encryption_password, salt)


def get_encryption_service_with_salt(salt: str) -> EncryptionService:
    encryption_password = os.getenv('ENCRYPTION_PASSWORD')
    if not encryption_password:
        raise ValueError("ENCRYPTION_PASSWORD environment variable is required")

    salt_bytes = base64.urlsafe_b64decode(salt.encode())
    return EncryptionService(encryption_password, salt_bytes)
