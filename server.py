import socket
from threading import Thread
from enums import SocketEnum
from typing import Dict

clients: Dict[socket.socket, str] = {}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SocketEnum.SERVER_IP, SocketEnum.PORT))
server_socket.listen()

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
            forward_message(client, msg)
        except ConnectionResetError:
            # Handle client disconnection
            print(f'Client {clients[client]} disconnected.')
            del clients[client]
            break

def forward_message(sender, message):
    for client, ip in clients.items():
        if client is not sender:
            try:
                client.send(message.encode())
            except:
                print(f'Failed to send message to {ip}')

if __name__ == '__main__':
    print('Server up and running.')
    Thread(target=accept_client).start()
