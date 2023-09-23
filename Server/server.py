import socket
from threading import Thread
from common import SocketEnum
from typing import Dict


def accept_client():
    while True:
        client, ip = server_socket.accept()
        print('Accepted client:', ip)dfh
        clients[client] = ip
        Thread(target=receive_msg, args=(client,)).start()

def check_login(client):
    from handle_db import is_login_valid

    login_info = client.recv(1024).decode()
    _, username, password = login_info.split(',')

    if is_login_valid(username, password):
        client.send(SocketEnum.VALID_LOGIN_INFO.encode())
    else:
        client.send(SocketEnum.INVALID_LOGIN_INFO.encode())

def receive_msg(client):
    while True:
        try:
            msg = client.recv(1024).decode()
            if not msg:
                break
            print(f'Received message from {clients[client]}: {msg}')
            if msg == SocketEnum.SENDING_LOGIN_INFO:
                check_login(client)

        except ConnectionResetError:
            # Handle client disconnection
            print(f'Client {clients[client]} disconnected.')
            del clients[client]
            break



if __name__ == '__main__':
    clients: Dict[socket.socket, str] = {}
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SocketEnum.SERVER_IP, SocketEnum.PORT))
    server_socket.listen()
    print('Server up and running.')
    Thread(target=accept_client).start()
