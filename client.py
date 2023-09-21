import socket
from enums import SocketEnum


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SocketEnum.SERVER_IP, SocketEnum.PORT))

print("connected!")

while True:
    msg = client_socket.recv(1024).decode()
    print(msg)