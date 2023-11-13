import socket
from threading import Thread
from common import SocketEnum, LoginEnum, FileEnum,\
    encapsulate_data, decapsulate_data
from typing import Dict, List, Tuple
from handle_2FA import is_token_valid

def accept_client():
    while True:
        client, ip = server_socket.accept()
        print('Accepted client:', ip)
        clients[client] = ip
        Thread(target=receive_msg, args=(client,)).start()

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

    login_info = client.recv(1024).decode()
    username, password = decapsulate_data(login_info)
    user_data = pull_user_value(username, password)
    if user_data:
        client.send(LoginEnum.VALID_LOGIN_INFO.encode())
        user_data_list = []
        for i, data in enumerate(user_data):
            if i == 0:   # id
                continue
            user_data_list.append(data)

        user_data_string = encapsulate_data(user_data_list)
        client.send(user_data_string.encode())
    else:
        client.send(LoginEnum.INVALID_LOGIN_INFO.encode())

def check_ttop_token(client):
    token = client.recv(1024).decode()
    if is_token_valid(token):
        client.send(LoginEnum.VALID_TOTP_TOKEN.encode())
    else:
        client.send(LoginEnum.INVALID_TOTP_TOKEN.encode())

def receive_file_data(client):
    file_data = client.recv(1024).decode()
    file_name, username, file_content = \
        decapsulate_data(file_data)
    from handle_db import add_file_to_db
    add_file_to_db(file_name=file_name,
                   uploading_user=username,
                   file_content=file_content)

def send_all_files_titles(client):
    from handle_db import pull_files
    all_file_titles: List[Tuple] \
        = pull_files(fields=['filename',
                             'uploaded_by',
                             'upload_time'])
    print(all_file_titles)
    file_count = str(len(all_file_titles))
    client.send(file_count.encode())
    for file_title in all_file_titles:
        client.send(encapsulate_data(file_title).encode())

def send_file_data(client):
    from handle_db import pull_files
    file_ind: str = client.recv(1024).decode()
    file_name, file_content = \
        pull_files(fields=['filename', 'content'],
                   where_dict={'ID': file_ind})[0]
    client.send(file_name.encode())

    print(file_name, file_content)

    bytes_file_size: int = len(file_content.encode())

    client.send(str(bytes_file_size).encode())
    client.send(file_content.encode())


if __name__ == '__main__':
    clients: Dict[socket.socket, str] = {}
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SocketEnum.SERVER_IP, SocketEnum.PORT))
    server_socket.listen()
    print('Server up and running.')
    Thread(target=accept_client).start()
