
shift = 3
def key_encryption(plain_key):
    midpoint = len(plain_key) // 2
    mixed_plain_key = plain_key[midpoint:] + \
                plain_key[:midpoint]

    encrypted_key = ''
    for char in mixed_plain_key:
        encrypted_key += chr(ord(char) + shift)

    return encrypted_key

def key_decryption(cipher_key):
    mixed_cipher_key = ''
    for char in cipher_key:
        mixed_cipher_key += chr(ord(char) - shift)

    midpoint = len(mixed_cipher_key) // 2
    decrypted_utf8 = mixed_cipher_key[midpoint:] + \
                     mixed_cipher_key[:midpoint]

    return decrypted_utf8





