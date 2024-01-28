import socket
from threading import Thread
from common import SocketEnum, UserEnum, FileEnum, UserEnum, \
    File, User, \
    send_pickle_obj, recv_pickle_obj
from typing import Dict, List, Tuple, Union
from handle_2FA import is_token_valid
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

            if msg == UserEnum.SENDING_LOGIN_INFO:
                check_login(client)

            elif msg == UserEnum.SENDING_TOTP_TOKEN:
                check_ttop_token(client)

            elif msg == FileEnum.SENDING_FILE_DATA:
                receive_file_data(client)

            elif msg == FileEnum.REQUESTING_FILE_DATA:
                send_file_data(client)

            elif msg == UserEnum.CREATE_NEW_USER:
                create_new_user(client)

            elif msg == UserEnum.REQUESTING_2FA_OBJECT:
                send_tfa_object(client)

        except ConnectionResetError:
            # Handle client disconnection
            print(f'Client {clients[client]} disconnected.')
            del clients[client]
            break

def check_login(client):
    from handle_db import pull_user_value

    login_try: User = recv_pickle_obj(client)
    user: User = pull_user_value(login_try.username, login_try.password)
    if user:
        client.send(UserEnum.VALID_INFO.encode())
        send_pickle_obj(user, client)
    else:
        client.send(UserEnum.INVALID_INFO.encode())

def check_ttop_token(client):
    token = client.recv(1024).decode()
    if is_token_valid(token):
        client.send(UserEnum.VALID_INFO.encode())
    else:
        client.send(UserEnum.INVALID_INFO.encode())

def receive_file_data(client):

    file = recv_pickle_obj(client)
    _, file_extension = os.path.splitext(file.name)

    if file_extension in FileEnum.FILE_EXTENSION_TO_CENSOR:
        censored_content = \
            censor_string_words(file.content)
    else:
        censored_content = file.content

    if censored_content == file.content:
        client.send(FileEnum.FILE_ACCEPTED.encode())
    else:
        client.send(FileEnum.FILE_REJECTED.encode())
        file.content = censored_content

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

def create_new_user(client):
    new_user = recv_pickle_obj(client)

    from handle_db import pull_user_value
    if pull_user_value(username=new_user.username):
        client.send(UserEnum.INVALID_INFO.encode())
        return
    client.send(UserEnum.VALID_INFO.encode())

    from handle_db import insert_user_value
    insert_user_value(new_user)

def send_tfa_object(client):
    from handle_db import pull_tfa_obj
    tfa_obj = pull_tfa_obj()
    send_pickle_obj(tfa_obj, client)

def get_banned_words() -> List[bytes]:
    from handle_db import pull_banned_words_obj
    return pull_banned_words_obj().banned_words

def censor_string_words(input_string):
    censored_string = input_string
    banned_words = get_banned_words()

    for word in banned_words:
        if word in censored_string:
            censored_string = censored_string.replace(word, b'*' * len(word))
    return censored_string


if __name__ == '__main__':
    clients: Dict[socket.socket, str] = {}
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SocketEnum.SERVER_IP, SocketEnum.PORT))
    server_socket.listen()
    print('Server up and running.')
    Thread(target=accept_client).start()
