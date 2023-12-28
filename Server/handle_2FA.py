import pyotp, qrcode
import os
from handle_string_manipulation import \
    encrypt, decrypt
import handle_db
from typing import Optional

def generate_new_key() -> str:
    secret_key = pyotp.random_base32()

    return encrypt(secret_key.encode()).hex()


def generate_qr_img(totp) -> str:
    totp_uri = totp.provisioning_uri(
        name='user@example.com',
        issuer_name='TFS')
    qrcode.make(totp_uri).save('img.png')
    with open('img.png', 'rb') as f:
        img = f.read()

    # TODO: remove qr img from server
    #os.remove('img.png')

    return encrypt(img).hex()

def create_new_otp():
    key = generate_new_key()
    img = generate_qr_img(get_totp(key))

    handle_db.insert_tfa_data(key, img)


def is_token_valid(user_input_token):
    #TODO: remove testing token

    totp = get_totp()
    return totp.verify(user_input_token) \
           or user_input_token == '69'

def get_totp(key: Optional[str]=None):
    if not key:
        key, _ = handle_db.pull_tfa_data()
    key = decrypt(bytes.fromhex(key)).decode()

    return pyotp.TOTP(key)


if __name__ == '__main__':
    handle_db.clear_tfa_table()
    create_new_otp()