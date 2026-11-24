"""
D247 Cryptography Module
Implements bidirectional AES-256-CBC encryption and decryption identical to CryptoJS AES.
Compatible with D247 / DiamondExch frontend security protocol.
"""

import base64
import hashlib
import json
import os
from typing import Any, Union
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Default static secret key extracted from D247 production client bundle
DEFAULT_CRYPTO_KEY = "cae7b808-8b1e-4f47-87a5-1a4b6a08030e"


def evp_bytes_to_key(password: bytes, salt: bytes, key_len: int = 32, iv_len: int = 16) -> tuple[bytes, bytes]:
    """
    OpenSSL EVP_BytesToKey algorithm using MD5.
    This matches CryptoJS.AES default key derivation with 8-byte salt.
    """
    derived = b""
    digest_block = b""
    while len(derived) < (key_len + iv_len):
        digest_block = hashlib.md5(digest_block + password + salt).digest()
        derived += digest_block
    return derived[:key_len], derived[key_len:key_len + iv_len]


def decrypt_cryptojs(encrypted_b64: str, key: str = DEFAULT_CRYPTO_KEY) -> Any:
    """
    Decrypts a CryptoJS AES encrypted base64 payload into native Python dict/list/string.
    
    Args:
        encrypted_b64: Base64 string starting with Salted__
        key: Encryption passphrase (default: cae7b808-8b1e-4f47-87a5-1a4b6a08030e)
        
    Returns:
        Decrypted JSON object or plain string
    """
    raw = base64.b64decode(encrypted_b64)
    if not raw.startswith(b"Salted__"):
        raise ValueError("Invalid CryptoJS format: missing 'Salted__' header prefix")
    
    salt = raw[8:16]
    ciphertext = raw[16:]
    
    derived_key, iv = evp_bytes_to_key(key.encode("utf-8"), salt, key_len=32, iv_len=16)
    
    cipher = Cipher(algorithms.AES(derived_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plain = decryptor.update(ciphertext) + decryptor.finalize()
    
    # PKCS7 unpadding
    pad_len = padded_plain[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError(f"Invalid PKCS7 padding length: {pad_len}")
    
    plaintext = padded_plain[:-pad_len].decode("utf-8")
    
    try:
        return json.loads(plaintext)
    except Exception:
        return plaintext


def encrypt_cryptojs(data: Union[dict, list, str, int, float, bool], key: str = DEFAULT_CRYPTO_KEY) -> str:
    """
    Encrypts Python data into a CryptoJS AES compatible Base64 string with random 8-byte salt.
    
    Args:
        data: Python dictionary, list, or primitive to encrypt
        key: Encryption passphrase (default: cae7b808-8b1e-4f47-87a5-1a4b6a08030e)
        
    Returns:
        Base64 encoded string starting with 'U2FsdGVkX1...'
    """
    if isinstance(data, (dict, list, int, float, bool)):
        data_str = json.dumps(data, separators=(",", ":"))
    else:
        data_str = json.dumps(str(data))
        
    plain_bytes = data_str.encode("utf-8")
    salt = os.urandom(8)
    
    derived_key, iv = evp_bytes_to_key(key.encode("utf-8"), salt, key_len=32, iv_len=16)
    
    # PKCS7 padding
    pad_len = 16 - (len(plain_bytes) % 16)
    padded_plain = plain_bytes + bytes([pad_len] * pad_len)
    
    cipher = Cipher(algorithms.AES(derived_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plain) + encryptor.finalize()
    
    encrypted_blob = b"Salted__" + salt + ciphertext
    return base64.b64encode(encrypted_blob).decode("utf-8")


if __name__ == "__main__":
    sample = {"etid": 4, "type": "all"}
    enc = encrypt_cryptojs(sample)
    dec = decrypt_cryptojs(enc)
    assert dec == sample
    print("CryptoJS AES-256 Engine: Test Passed Successfully!")
