# contains build encyption logic

# currently not used

# imports
from cryptography.fernet import Fernet

def encrypt(msg, key):
    return Fernet(key).encrypt(msg.encode('utf-8'))

def decrypt(msg, key):
    return Fernet(key).decrypt(msg).decode('utf-8')
