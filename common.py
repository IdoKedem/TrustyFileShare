from hashlib import md5

class SocketEnum:
    SERVER_IP = '192.168.56.1'
    PORT = 6666

    SENDING_LOGIN_INFO = 'Sending Login Info!'
    VALID_LOGIN_INFO = 'Valid Login Info!'
    INVALID_LOGIN_INFO = 'Invalid Login Info!'


def hash_text(text):
    return md5(text.encode()).hexdigest()
