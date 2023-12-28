import socket
from threading import Thread
from common import SocketEnum, LoginEnum, FileEnum,\
    encapsulate_data, decapsulate_data
from typing import Dict, List, Tuple
from handle_2FA import is_token_valid
import handle_string_manipulation
import time
import os

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
            elif msg == FileEnum.REQUESTING_ALL_FILE_TITLES:
                send_all_files_titles(client)
            elif msg == FileEnum.REQUESTING_FILE_DATA:
                send_file_data(client)

        except ConnectionResetError:
            # Handle client disconnection
            print(f'Client {clients[client]} disconnected.')
            del clients[client]
            break

def check_login(client):
    from handle_db import pull_user_value

    login_info = client.recv(1024)
    username, password = decapsulate_data(login_info)
    user_data = pull_user_value(username.decode(), password.decode())
    if user_data:
        client.send(LoginEnum.VALID_LOGIN_INFO.encode())
        user_data_list = []
        for i, data in enumerate(user_data):
            if i == 0:   # id
                continue
            user_data_list.append(data)

        user_data_string = encapsulate_data(user_data_list)
        client.send(user_data_string)
    else:
        client.send(LoginEnum.INVALID_LOGIN_INFO.encode())

def check_ttop_token(client):
    token = client.recv(1024).decode()
    if is_token_valid(token):
        client.send(LoginEnum.VALID_TOTP_TOKEN.encode())
    else:
        client.send(LoginEnum.INVALID_TOTP_TOKEN.encode())

def receive_file_data(client):
    file_size = int(client.recv(1024).decode())
    #time.sleep(0.2)
    file_data = client.recv(1024 + file_size)
    file_name, username, file_content = \
        decapsulate_data(file_data)

    _, file_extension = os.path.splitext(file_name)

    if file_extension in FileEnum.FILE_EXTENSION_TO_CENSOR:
        censored_content = \
            handle_string_manipulation.censor_string_words(file_content)
    else:
        censored_content = file_content

    if censored_content == file_content:
        client.send(FileEnum.FILE_ACCEPTED.encode())
    else:
        client.send(FileEnum.FILE_REJECTED.encode())

    from handle_db import add_file_to_db
    add_file_to_db(file_name=file_name.decode(),
                   uploading_user=username.decode(),
                   file_content=censored_content)

def send_all_files_titles(client):
    from handle_db import pull_files
    all_file_titles: List[Tuple] \
        = pull_files(fields=['filename',
                             'uploaded_by',
                             'upload_time'])

    file_count = str(len(all_file_titles))
    client.send(file_count.encode())
    for file_title in all_file_titles:
        client.send(encapsulate_data(file_title))
        client.recv(1024)

def send_file_data(client):
    from handle_db import pull_files
    file_ind: str = client.recv(1024).decode()

    file_name, hexa_file_content = \
        pull_files(fields=['filename', 'content'],
                   where_dict={'ID': file_ind})[0]
    client.send(file_name.encode())

    bytes_file_content = bytes.fromhex(hexa_file_content)

    bytes_file_size: int = len(bytes_file_content)

    client.send(str(bytes_file_size).encode())
    time.sleep(0.2)   # prevent client from receiving two message with one recv()
    client.send(bytes_file_content)


if __name__ == '__main__':
    clients: Dict[socket.socket, str] = {}
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SocketEnum.SERVER_IP, SocketEnum.PORT))
    server_socket.listen()
    print('Server up and running.')
    Thread(target=accept_client).start()
