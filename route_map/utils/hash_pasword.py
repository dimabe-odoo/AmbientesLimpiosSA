from cryptography.fernet import Fernet
import os


def create_password(password):
    pwd = password.encode()
    key = get_key()
    f = Fernet(key)
    encrypted = f.encrypt(pwd)
    return encrypted


def decrypt_password(password):
    key = get_key()
    f = Fernet(key)
    decrypt_password = f.decrypt(password)
    return decrypt_password


def get_key():
    try:
        if os.path.isfile('key.key'):
            file = open('key.key', 'rb')
            key = file.read()
            file.close()
        else:
            key = Fernet.generate_key()
            file = open('key.key', 'wb')
            file.write(key)
            file.close()
        return key
    except:
        print("Cago")
