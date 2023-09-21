import socket
from threading import Thread
from enums import SocketEnum
from typing import Dict, List, Optional
import time

clients: Dict[socket.socket, str] = {}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def start_server():
    server_socket.bind((SocketEnum.SERVER_IP, SocketEnum.PORT))

def accept_client():
    while True:
        server_socket.listen()
        client, ip = server_socket.accept()
        print('accepted client!')
        clients[client] = ip

def receive_msg(client, messages: List[Optional[str]]):
    msg = client.recv(1024).decode()
    messages.append(msg)



if __name__ == '__main__':
    start_server()
    print('server up')
    Thread(target=accept_client).start()
    while True:
        messages = []
        threads = []
        for client in clients:
            threads.append(Thread(target=receive_msg, args=(client, messages)))
            threads[-1].start()
        for thr in threads:
            thr.join()
        if messages:
            for client in clients:
                for msg in messages:
                    client.send(msg.encode())