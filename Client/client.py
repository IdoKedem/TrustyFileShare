import socket
from common import SocketEnum
from windows import LoginWindow, MainWindow


def connect_to_server() -> socket.socket:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SocketEnum.SERVER_IP, SocketEnum.PORT))
    return client_socket

if __name__ == '__main__':
    client_socket = connect_to_server()

    LoginWindow(title='Login',
               client_socket=client_socket).mainloop()

    # MainWindow(title='Main Window',
    #            client_socket=client_socket).mainloop()







