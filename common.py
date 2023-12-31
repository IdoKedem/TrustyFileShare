from hashlib import md5
from typing import List, Any, Tuple, Union
from datetime import datetime
import pickle
from enum import Enum
import time

class SocketEnum:
    SERVER_IP = '127.0.0.1'
    PORT = 6666
    SPLIT_TEXT = '!@#$%^&*()'

class LoginEnum:
    SENDING_LOGIN_INFO = 'Sending Login Info!'
    VALID_LOGIN_INFO = 'Valid Login Info!'
    INVALID_LOGIN_INFO = 'Invalid Login Info!'

    SENDING_TOTP_TOKEN = 'Sending TOTP Token!'
    VALID_TOTP_TOKEN = 'Valid TOTP Token!'
    INVALID_TOTP_TOKEN = 'Invalid TOTP Token'

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




def hash_text(text):
    return md5(text.encode()).hexdigest()


def encapsulate_data(data_list:
                     Union[Tuple[Union[str, bytes], ...],
                           List[Union[str, bytes]]]) -> bytes:
    output = b''
    #print(data_list)
    for data in data_list:
        if isinstance(data, str):
            data = data.encode()
        output += SocketEnum.SPLIT_TEXT.encode() + data
    return output

def decapsulate_data(data_string: bytes) -> Tuple[bytes, ...]:
    data = data_string.split(SocketEnum.SPLIT_TEXT.encode())
    return tuple(data[1:])

def send_pickle_obj(obj, client_socket):
    serialized_obj: bytes = pickle.dumps(obj)
    obj_size = len(serialized_obj)

    client_socket.send(str(obj_size).encode())
    #time.sleep(0.2)
    client_socket.send(serialized_obj)

def recv_pickle_obj(client_socket):
    obj_size = int(client_socket.recv(1024).decode())
    #obj_size = client_socket.recv(1024)

    serialized_obj = client_socket.recv(1024 + obj_size)
    #serialized_obj = client_socket.recv(1024 + int(obj_size.decode()))
    return pickle.loads(serialized_obj)


class User:
    def __init__(self, username: str, password: str, is_admin: str='False'):
        self.username = username
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

class TryLogin:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class TFA:
    def __init__(self, key: str, qr_img: str):
        ## key and img are encrypted
        self.key = key
        self.qr_img = qr_img


users = \
    [User('Ido', '123', is_admin='True'), User('Kedem', '456')]