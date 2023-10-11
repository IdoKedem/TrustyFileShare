import pyotp, qrcode
import os
from handle_encryption import \
    key_encryption, key_decryption

def generate_new_key():
    secret_key = key_encryption(pyotp.random_base32())
    with open('2FA/key.txt', 'w') as f:
        f.write(secret_key)

def generate_qr_img(totp):
    totp_uri = totp.provisioning_uri(
        name='user@example.com',
        issuer_name='TFS')
    if not os.path.exists('Server/2FA/QR.png'):
        img = qrcode.make(totp_uri)
        img.save('Server/2FA/QR.png')

def create_new_otp():
    generate_new_key()
    generate_qr_img(get_totp())
def is_token_valid(user_input_token):
    #TODO: remove testing token

    totp = get_totp()
    return totp.verify(user_input_token) \
           or user_input_token == '69'

def get_totp():
    if not os.path.isfile('Server/2FA/key.txt'):
        print('No key found')
        return
    with open('Server/2FA/key.txt', 'r') as f:
        key = key_decryption(f.read())
    return pyotp.TOTP(key)
