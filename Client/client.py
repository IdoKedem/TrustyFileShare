import socket
from enums import SocketEnum
from threading import Thread
import tkinter as tk
from typing import Dict, List
from hashlib import md5

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
            frame.pack()
            tk.Label(frame, text=entry_name + ':',
                     font=default_font).pack(side=tk.LEFT)
            entry = tk.Entry(frame, border=2, show=entry_show,
                    font=default_font)
            self.entries.append(entry)
            entry.pack()

        _prepare_info_frame()

    def check_login(self):
        global client_socket
        credentials_string = ''

        entry: tk.Entry
        for index, entry in enumerate(self.entries):
            entry_text = entry.get()
            if index == 1:    # password entry
                entry_text = hash_text(entry_text)

            credentials_string += ',' + entry_text
        client_socket.send(credentials_string.encode())

def hash_text(text: str) -> str:
    return md5(text.encode()).hexdigest()

if __name__ == '__main__':
    client_socket = connect_to_server()

    login_window = LoginWindow(title='Login')
    login_window.mainloop()




