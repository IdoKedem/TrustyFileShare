from hashlib import md5
from enum import Enum

class SocketEnum:
    SERVER_IP = '192.168.56.1'
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
    SUPPORTED_FILE_TYPES = [
        ('Text Files', '*.txt')
    ]


def hash_text(text):
    return md5(text.encode()).hexdigest()


class User:
    def __init__(self, username, password, is_admin=False):
        self.username = username
        self.password = hash_text(password)
        self.is_admin = is_admin

    def get_login_info(self):
        return self.username, self.password
    def __str__(self):
        return \
            f'Username: {self.username}\nPassword: {self.password}'
