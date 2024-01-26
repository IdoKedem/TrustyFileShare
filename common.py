from typing import List, Any, Tuple, Union
from datetime import datetime
import pickle
from hashlib import md5
import time
import math



class SocketEnum:
    SERVER_IP = '127.0.0.1'
    PORT = 6666

class UserEnum:
    SENDING_LOGIN_INFO = 'Sending Login Info!'
    SENDING_TOTP_TOKEN = 'Sending TOTP Token!'
    REQUESTING_2FA_OBJECT = 'Sending 2FA Object!'

    CREATE_NEW_USER = 'Create New User!'

    VALID_INFO = 'Valid Info!'
    INVALID_INFO = 'Invalid Info!'


class FileEnum:
    SENDING_FILE_DATA = 'Sending File Data!'
    REQUESTING_FILE_DATA = 'Requesting File Data!'

    REQUESTING_ALL_FILE_TITLES = 'Requesting File Titles!'

    SENDING_FILE_COUNT = 'Sending File Count!'
    SENDING_FILE_SIZE = 'Sending File Size!'

    SUPPORTED_FILE_TYPES = [
        ('All Files', '*.txt;*.jpg;*.jpeg;*.mp4'),
        ('Text Files', '*.txt'),
        ('JPGs', '*.jpg;*.jpeg'),
        ('MP4s', '*.mp4')
    ]

    FILE_EXTENSION_TO_CENSOR = [
        b'.txt'
    ]

    FILE_REJECTED = 'File rejected'
    FILE_ACCEPTED = 'File Accepted!'


def send_pickle_obj(obj, client_socket):
    serialized_obj_encrypted: bytes = \
        encrypt(pickle.dumps(obj))
    obj_size = len(serialized_obj_encrypted)

    print('sending:', serialized_obj_encrypted)

    client_socket.send(str(obj_size).encode())
    time.sleep(0.1)
    client_socket.send(serialized_obj_encrypted)

def recv_pickle_obj(client_socket):
    obj_size = int(client_socket.recv(1024).decode())

    serialized_obj_decrypted = \
        decrypt(client_socket.recv(1024 + obj_size))
    print('got:', serialized_obj_decrypted)

    return pickle.loads(serialized_obj_decrypted)


class User:
    def __init__(self, username: str, password: str,
                 is_admin: Union[None, bool]=None):
        self.username = encrypt(username.encode())
        self.password = hash_text(password)
        self.is_admin = is_admin

    def get_plain_username(self):
        return decrypt(self.username).decode()
    def __str__(self):
        return \
            f'Username: {self.username}\nPassword: {self.password}'


class File:
    def __init__(self, file_name,
                 uploading_user: User, file_content: bytes):
        self.name = file_name
        self.uploading_user = uploading_user
        self.content: bytes = file_content

        cur_time = datetime.now()
        self.upload_time = cur_time.strftime('%d/%m/%y %H:%M:%S')


class TFA:
    def __init__(self, key: str, qr_img: bytes):
        self.key = key   # encrypted
        self.qr_img: bytes = qr_img # not encrypted



def encrypt(plain: bytes) -> bytes:
    shift = 3
    midpoint = len(plain) // 2   # floor
    mixed_plain = plain[midpoint:] + \
                  plain[:midpoint]

    encrypted = b''
    for char in mixed_plain:
        encrypted += bytes.fromhex(format(char + shift, 'x').zfill(2))

    return encrypted

def decrypt(cipher: bytes) -> bytes:
    shift = 3
    mixed_cipher = b''
    for char in cipher:
        mixed_cipher += bytes.fromhex(format(char - shift, 'x').zfill(2))

    midpoint = math.ceil(len(mixed_cipher) / 2)
    decrypted_utf8 = mixed_cipher[midpoint:] + \
                     mixed_cipher[:midpoint]

    return decrypted_utf8

def hash_text(text):
    return md5(text.encode()).hexdigest()


users = \
    [User('Ido', '123', is_admin=True),
     User('Kedem', '456', is_admin=False)]
