import os
from cryptography.fernet import Fernet

class Crypthograph:
    def __init__(self):
        key=os.getenv("FERNET_KEY").encode()
        self.f = Fernet(key)

    def encrypt(self, stringText: str)-> bytes:
        encrypted = self.f.encrypt(stringText.encode())
        return encrypted
    
    def decrypt(self, encryptedStr: bytes):
        decrypted = self.f.decrypt(encryptedStr).decode()
        return decrypted