
shift = 3
def encrypt(plain_key: bytes, shift=shift) -> bytes:
    midpoint = len(plain_key) // 2
    mixed_plain_key = plain_key[midpoint:] + \
                plain_key[:midpoint]

    encrypted_key = b''
    for char in mixed_plain_key:
        encrypted_key += chr(char + shift).encode()

    return encrypted_key

def decrypt(cipher_key: bytes, shift=shift) -> bytes:
    mixed_cipher_key = b''
    for char in cipher_key:
        mixed_cipher_key += (chr(char - shift)).encode()

    midpoint = len(mixed_cipher_key) // 2
    decrypted_utf8 = mixed_cipher_key[midpoint:] + \
                     mixed_cipher_key[:midpoint]

    return decrypted_utf8


def get_banned_words():
    with open('Server/banned_words.txt', 'rb') as f:
        banned_words = f.read().replace(b'\r' ,b'').split(b'\n')
    return banned_words

def censor_string_words(input_string):
    censored_string = input_string
    banned_words = get_banned_words()

    for word in banned_words:
        print(word)
        censored_string = censored_string.replace(word, b'*' * len(word))
    return censored_string

