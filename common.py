from typing import List, Any, Tuple, Union
from datetime import datetime
import pickle
from hashlib import md5
import time



class SocketEnum:
    SERVER_IP = '127.0.0.1'
    PORT = 6666

class UserEnum:
    SENDING_LOGIN_INFO = 'Sending Login Info!'
    SENDING_TOTP_TOKEN = 'Sending TOTP Token!'

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
    serialized_obj: bytes = pickle.dumps(obj)
    obj_size = len(serialized_obj)

    client_socket.send(str(obj_size).encode())
    time.sleep(0.1)
    client_socket.send(serialized_obj)

def recv_pickle_obj(client_socket):
    obj_size = int(client_socket.recv(1024).decode())

    serialized_obj = client_socket.recv(1024 + obj_size)
    return pickle.loads(serialized_obj)


class User:
    def __init__(self, username: str, password: str,
                 is_admin: Union[None, bool]=None):
        self.username = encrypt(username.encode())
        self.password = hash_text(password)
        self.is_admin = is_admin

    def get_login_info(self):
        return self.username, self.password
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
    def __init__(self, key: str, qr_img: str):
        ## key and img are encrypted
        self.key = key
        self.qr_img = qr_img



# TODO: REMOVE!!!! IMPORT FROM EXISTING
def encrypt(plain_key: bytes) -> bytes:
    shift = 3
    midpoint = len(plain_key) // 2
    mixed_plain = plain_key[midpoint:] + \
                plain_key[:midpoint]

    encrypted = b''
    for char in mixed_plain:
        encrypted += chr(char + shift).encode()

    return encrypted

def decrypt(cipher_key: bytes) -> bytes:
    shift = 3
    mixed_cipher_key = b''
    for char in cipher_key:
        mixed_cipher_key += (chr(char - shift)).encode()

    midpoint = len(mixed_cipher_key) // 2
    decrypted_utf8 = mixed_cipher_key[midpoint:] + \
                     mixed_cipher_key[:midpoint]

    return decrypted_utf8

def hash_text(text):
    return md5(text.encode()).hexdigest()
# TODO: REMOVE!!!! IMPORT FROM EXISTING


users = \
    [User('Ido', '123', is_admin=True),
     User('Kedem', '456', is_admin=False)]
