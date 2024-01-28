import pyotp, qrcode
import os
from handle_string_manipulation import \
    encrypt, decrypt
import handle_db
from typing import Optional
from common import TFA

def generate_new_key() -> str:
    """
    generates a new TOTP key
    :return:
    """
    secret_key = pyotp.random_base32()
    encrypted_key = encrypt(secret_key.encode()).hex()

    return encrypted_key


def generate_qr_img(totp) -> bytes:
    totp_uri = totp.provisioning_uri(
        name='user@example.com',
        issuer_name='TFS')
    qrcode.make(totp_uri).save('img.png')

    with open('img.png', 'rb') as f:
        img = f.read()

    os.remove('img.png')

    return img

def create_new_otp():
    """
    creates a new TOTP and inserts it into the db
    :return:
    """
    key = generate_new_key()
    img: bytes = generate_qr_img(get_totp(key))
    tfa_obj = TFA(key=key, qr_img=img)

    handle_db.insert_tfa_data(tfa_obj=tfa_obj)


def is_token_valid(user_input_token):
    totp = get_totp()
    return totp.verify(user_input_token)

def get_totp(key: Optional[str]=None):
    """
    retrieves the TOTP code
    :param key:
    :return:
    """
    if not key:
        key = handle_db.pull_tfa_obj().key
    key = decrypt(bytes.fromhex(key)).decode()

    return pyotp.TOTP(key)


if __name__ == '__main__':
    handle_db.clear_tfa_table()
    create_new_otp()