import socket
from threading import Thread
from common import SocketEnum, LoginEnum, FileEnum,\
    encapsulate_data, decapsulate_data, File, User, \
    send_pickle_obj, recv_pickle_obj
from typing import Dict, List, Tuple, Union
from handle_2FA import is_token_valid
import handle_string_manipulation
import time
import os
import pickle


def accept_client():
    while True:
        client, ip = server_socket.accept()
        print('Accepted client:', ip)
        clients[client] = ip
        Thread(target=receive_msg, args=(client,)).start()

def get_banned_words():
    with open('banned_words.txt', 'rb') as f:
        banned_words = f.read().split(b'\n')
    return banned_words

def is_file_rejected(file_content) -> bytes:
    for word in get_banned_words():
        if word in file_content:
            return word
    return b''

def receive_msg(client):
    while True:
        try:
            msg = client.recv(1024).decode()
            if not msg:
                break
            print(f'Received message from {clients[client]}: {msg}')
            if msg == LoginEnum.SENDING_LOGIN_INFO:
                check_login(client)
            elif msg == LoginEnum.SENDING_TOTP_TOKEN:
                check_ttop_token(client)
            elif msg == FileEnum.SENDING_FILE_DATA:
                receive_file_data(client)
            elif msg == FileEnum.REQUESTING_FILE_DATA:
                send_file_data(client)

        except ConnectionResetError:
            # Handle client disconnection
            print(f'Client {clients[client]} disconnected.')
            del clients[client]
            break

def check_login(client):
    from handle_db import pull_user_value

    login_info = client.recv(1024)  # TODO: use pickle
    username, password = decapsulate_data(login_info)
    user: Union[User, None] = pull_user_value(username.decode(), password.decode())
    if user:
        client.send(LoginEnum.VALID_LOGIN_INFO.encode())
        send_pickle_obj(user, client)
    else:
        client.send(LoginEnum.INVALID_LOGIN_INFO.encode())

def check_ttop_token(client):
    token = client.recv(1024).decode()
    if is_token_valid(token):
        client.send(LoginEnum.VALID_TOTP_TOKEN.encode())
    else:
        client.send(LoginEnum.INVALID_TOTP_TOKEN.encode())

def receive_file_data(client):

    file = recv_pickle_obj(client)
    _, file_extension = os.path.splitext(file.name)

    if file_extension in FileEnum.FILE_EXTENSION_TO_CENSOR:
        censored_content = \
            handle_string_manipulation.censor_string_words(file.content)
    else:
        censored_content = file.content

    if censored_content == file.content:
        client.send(FileEnum.FILE_ACCEPTED.encode())
    else:
        client.send(FileEnum.FILE_REJECTED.encode())

    from handle_db import add_file_to_db
    add_file_to_db(file_obj=file)

def send_file_data(client):
    from handle_db import pull_files
    file_ind: str = client.recv(1024).decode()

    where_dict = {}
    if file_ind >= '0':
        where_dict = {'ID': file_ind}
    files: List[File] = \
        pull_files(where_dict=where_dict)
    send_pickle_obj(files, client)


if __name__ == '__main__':
    clients: Dict[socket.socket, str] = {}
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SocketEnum.SERVER_IP, SocketEnum.PORT))
    server_socket.listen()
    print('Server up and running.')
    Thread(target=accept_client).start()
