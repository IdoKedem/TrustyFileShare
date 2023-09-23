import socket
from enums import SocketEnum
from threading import Thread


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SocketEnum.SERVER_IP, SocketEnum.PORT))

print("connected!")

def print_messages():
    while True:
        print(client_socket.recv(1024).decode())

def send_message():
    while True:
        client_socket.send(input('enter msg \n').encode())


Thread(target=print_messages).start()

Thread(target=send_message).start()


