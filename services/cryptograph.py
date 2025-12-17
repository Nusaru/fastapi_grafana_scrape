import os
from cryptography.fernet import Fernet

class Crypthograph:
    def __init__(self):
        key=os.getenv("PASSWORD_KEY").encode()
        self.f = Fernet(key)

    def encryptPassword(self, password: str)-> bytes:
        encrypted = self.f.encrypt(password.encode())
        return encrypted
    
    def decryptPassword(self, encryptedPassword: bytes):
        password = self.f.decrypt(encryptedPassword).decode()
        return password