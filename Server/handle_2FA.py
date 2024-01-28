import pyotp, qrcode
import os
from typing import Optional
from common import TFA, encrypt, decrypt

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
    return TFA(key=key, qr_img=img)



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
        import handle_db
        key = handle_db.pull_tfa_obj().key
    key = decrypt(bytes.fromhex(key)).decode()

    return pyotp.TOTP(key)


if __name__ == '__main__':
    import handle_db
    handle_db.clear_tfa_table()
    tfa_obj = create_new_otp()
    handle_db.insert_tfa_data(tfa_obj=tfa_obj)
