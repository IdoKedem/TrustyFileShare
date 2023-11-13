from hashlib import md5
from typing import List, Any, Tuple, Union
from enum import Enum

class SocketEnum:
    SERVER_IP = '172.20.132.151'
    PORT = 6666

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
    SENDING_FILE_SIZE = 'Sending File Size'


    SUPPORTED_FILE_TYPES = [
        ('Text Files', '*.txt'),
        ('JPGs', '*.jpg')
    ]


def hash_text(text):
    return md5(text.encode()).hexdigest()


def encapsulate_data(data_list:
                     Union[Tuple[str], List[str]]) -> str:
    output = ''
    print(data_list)
    for data in data_list:
        output += ',' + data
    return output

def decapsulate_data(data_string: str):
    data = data_string.split(',')
    return tuple(data[1:])


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
users = \
    [User('Ido', '123', is_admin='True'), User('Kedem', '456')]