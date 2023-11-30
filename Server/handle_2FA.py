import pyotp, qrcode
import os
from handle_string_manipulation import \
    encrypt, decrypt

def generate_new_key():
    secret_key = encrypt(pyotp.random_base32().encode())
    with open(path_to_key, 'wb') as f:
        f.write(secret_key)

def generate_qr_img(totp):
    totp_uri = totp.provisioning_uri(
        name='user@example.com',
        issuer_name='TFS')
    if not os.path.exists(path_to_qr):
        img = qrcode.make(totp_uri)
        img.save(path_to_qr)

def create_new_otp():
    generate_new_key()
    generate_qr_img(get_totp())

def is_token_valid(user_input_token):
    #TODO: remove testing token

    totp = get_totp()
    return totp.verify(user_input_token) \
           or user_input_token == '69'

def get_totp():
    assert os.path.isfile(path_to_key), \
            'no key found'
    with open(path_to_key, 'rb') as f:
        key = decrypt(f.read())
    return pyotp.TOTP(key.decode())

path_to_dir = '2FA'
if __name__ != '__main__':
    path_to_dir = 'Server/' + path_to_dir

path_to_key = path_to_dir + '/key.txt'
path_to_qr = path_to_dir + '/QR.png'

if __name__ == '__main__':
    create_new_otp()