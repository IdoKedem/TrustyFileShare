import socket
from common import SocketEnum, hash_text
from threading import Thread
import tkinter as tk
from typing import Dict, List
from hashlib import md5
import queue

def connect_to_server() -> socket.socket:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SocketEnum.SERVER_IP, SocketEnum.PORT))

    return client_socket


class BaseWindow(tk.Tk):
    def __init__(self, title: str,
                 width: int=800, height: int=800):
        super().__init__()
        self.geometry(f'{width}x{height}')
        self.resizable(False, False)
        self.title(f'TFS - {title}')


class LoginWindow(BaseWindow):
    def __init__(self, title: str,
                 width: int=800, height: int=600):
        super().__init__(title, width, height)
        self.entries: List[tk.Entry] = []
        self.prepare_window()

    def prepare_window(self):
        """
        prepares the login window, with all its widgets
        :return:
        """
        tk.Label(text="TFS by Ido Kedem", font=('', 30)).pack()

        info_frame = tk.Frame(self)
        info_frame.pack(pady=60)

        default_font = '', 16

        def _prepare_info_frame():
            tk.Label(info_frame, text='Login',
                     font=('', 24)).pack()

            username_frame = \
                tk.Frame(info_frame,
                         width=400, height=100, pady=15)
            _prepare_frame(frame=username_frame,
                           entry_name='Username')
            password_frame = \
                tk.Frame(info_frame,
                         width=400, height=100, pady=5)
            _prepare_frame(frame=password_frame,
                           entry_name='Password', entry_show='*')

            tk.Button(info_frame, text='Submit', height=1,
                      font=default_font, command=self.check_login).pack()

        def _prepare_frame(frame, entry_name, entry_show=None):
            """
            prepares a frame. used with username and password frames
            :param frame: frame to fill with widgets
            :param entry_name: name of the entry, shown in label
            :param entry_show: entry's 'show' param
            :return:
            """
            frame.pack()
            tk.Label(frame, text=entry_name + ':',
                     font=default_font).pack(side=tk.LEFT)
            entry = tk.Entry(frame, border=2, show=entry_show,
                    font=default_font)
            self.entries.append(entry)
            entry.pack()

        _prepare_info_frame()

    def check_login(self):
        """
        validates the inputted credentials with the server
        :return:
        """
        global client_socket
        credentials_string = ''

        entry: tk.Entry
        for index, entry in enumerate(self.entries):
            entry_text = entry.get()
            if index == 1:    # password entry
                entry_text = hash_text(entry_text)

            credentials_string += ',' + entry_text

        client_socket.send(SocketEnum.SENDING_LOGIN_INFO.encode())
        client_socket.send(credentials_string.encode())

        response_queue = queue.Queue()
        get_server_response(response_queue)
        print(response_queue.get())


def get_server_response(response_queue) -> None:
    """
    receives a response from the server and puts it in a queue
    :param response_queue: the queue the response is put in
    :return: Nothing, mutates 'response_queue'
    """
    response = client_socket.recv(1024).decode()
    response_queue.put(response)


if __name__ == '__main__':
    client_socket = connect_to_server()

    login_window = LoginWindow(title='Login')
    login_window.mainloop()




