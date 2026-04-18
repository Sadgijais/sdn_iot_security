from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt(data, key):
    key = key[:32]
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce, ciphertext, tag

def decrypt(nonce, ciphertext, tag, key):
    key = key[:32]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)