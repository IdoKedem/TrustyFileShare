import socket
from threading import Thread
from enums import SocketEnum
from typing import Dict
import time

clients: Dict[socket.socket, str] = {}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def start_server():
    server_socket.bind((SocketEnum.SERVER_IP, SocketEnum.PORT))

def receive_client():
    while True:
        server_socket.listen()
        client, ip = server_socket.accept()
        print('accepted client!')
        clients[client] = ip



if __name__ == '__main__':
    start_server()
    print('server up')
    Thread(target=receive_client).start()
    while True:
        time.sleep(3)
        for client in clients:
            client.send(b'hi')