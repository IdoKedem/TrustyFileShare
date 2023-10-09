import socket
from threading import Thread
from common import SocketEnum, LoginEnum
from typing import Dict
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
                token = client.recv(1024).decode()
                if is_token_valid(token):
                    client.send(LoginEnum.VALID_TOTP_TOKEN.encode())
                else:
                    client.send(LoginEnum.INVALID_TOTP_TOKEN.encode())

        except ConnectionResetError:
            # Handle client disconnection
            print(f'Client {clients[client]} disconnected.')
            del clients[client]
            break

def check_login(client):
    from handle_db import is_login_valid

    login_info = client.recv(1024).decode()
    _, username, password = login_info.split(',')

    if is_login_valid(username, password):
        client.send(LoginEnum.VALID_LOGIN_INFO.encode())
    else:
        client.send(LoginEnum.INVALID_LOGIN_INFO.encode())


if __name__ == '__main__':
    clients: Dict[socket.socket, str] = {}
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SocketEnum.SERVER_IP, SocketEnum.PORT))
    server_socket.listen()
    print('Server up and running.')
    Thread(target=accept_client).start()
