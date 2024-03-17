# contains build encyption logic

# imports
import base64
import sys
print(sys.version)
from cryptography.fernet import Fernet

# global variables
key = b'_v8Jixjz_kPDF9Dqg_7PaWzVDneSC0qcJ1DvEdPCbc0='

# functions

def encrypt(msg):
    return Fernet(key).encrypt(msg.encode('utf-8'))

def decrypt(msg):
    
    return Fernet(key).decrypt(msg).decode("utf-8")
