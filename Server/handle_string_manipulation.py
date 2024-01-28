from hashlib import md5
from handle_db import pull_banned_words_obj
from typing import List
import os

cur_dir = os.path.join(os.getcwd())
if os.path.basename(cur_dir) != 'Server':
    cur_dir = os.path.join(cur_dir, 'Server')


shift = 3
def encrypt(plain_key: bytes, shift=shift) -> bytes:
    midpoint = len(plain_key) // 2
    mixed_plain = plain_key[midpoint:] + \
                plain_key[:midpoint]

    encrypted = b''
    for char in mixed_plain:
        encrypted += chr(char + shift).encode()

    return encrypted

def decrypt(cipher_key: bytes, shift=shift) -> bytes:
    mixed_cipher_key = b''
    for char in cipher_key:
        mixed_cipher_key += (chr(char - shift)).encode()

    midpoint = len(mixed_cipher_key) // 2
    decrypted_utf8 = mixed_cipher_key[midpoint:] + \
                     mixed_cipher_key[:midpoint]

    return decrypted_utf8


# TODO: access through db
def get_banned_words() -> List[bytes]:
    return pull_banned_words_obj().banned_words

def censor_string_words(input_string):
    censored_string = input_string
    banned_words = get_banned_words()

    for word in banned_words:
        if word in censored_string:
            censored_string = censored_string.replace(word, b'*' * len(word))
    return censored_string

def hash_text(text):
    return md5(text.encode()).hexdigest()
