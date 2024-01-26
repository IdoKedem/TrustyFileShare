import socket
from common import SocketEnum
import common
from windows import MainWindow


def connect_to_server() -> socket.socket:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SocketEnum.SERVER_IP, SocketEnum.PORT))
    return client_socket

if __name__ == '__main__':
    client_socket = connect_to_server()

    MainWindow(client_socket=client_socket,
               is_skip_login=False).mainloop()









