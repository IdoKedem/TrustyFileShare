import socket
from common import SocketEnum, LoginEnum, hash_text
import tkinter as tk
from typing import List, Dict
from threading import Thread
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
    def __init__(self, title: str):
        super().__init__(title)

        self.entries: List[tk.Entry] = []
        self.labels: Dict[str, tk.Label] = {}
        self.default_font = '', 16

        self.prepare_window()

    def prepare_window(self):
        """
        prepares the login window, with all its widgets
        :return:
        """
        tk.Label(text="TFS by Ido Kedem", font=('', 30)).pack()

        info_frame = tk.Frame(self)
        info_frame.pack(pady=60)
        def _prepare_frame(frame, entry_name, entry_show=None):
            """
            prepares a frame. used with username and password frames
            :param frame: a frame to fill with widgets
            :param entry_name: name of the entry, shown in label
            :param entry_show: entry's 'show' param
            :return:
            """
            frame.pack()
            tk.Label(frame, text=entry_name + ':',
                     font=self.default_font).pack(side=tk.LEFT)
            entry = tk.Entry(frame, border=2, show=entry_show,
                    font=self.default_font, cursor='xterm')
            self.entries.append(entry)
            entry.pack()

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

        self.labels[LoginEnum.INVALID_LOGIN_INFO] = \
            tk.Label(info_frame, text='Try Again',
                     fg='red', font=('', 12))
        self.login_submit_btn = \
            tk.Button(info_frame, text='Submit', command=self.check_login,
            height=1, font=self.default_font, cursor='hand2')
        self.login_submit_btn.pack()

    def check_login(self):
        """
        validates the inputted credentials with the server
        :return:
        """
        global client_socket
        credentials_string = ''

        for index, entry in enumerate(self.entries):
            entry_text = entry.get()
            entry.delete(0, tk.END)
            if index == 1:    # password entry
                entry_text = hash_text(entry_text)

            credentials_string += ',' + entry_text

        client_socket.send(LoginEnum.SENDING_LOGIN_INFO.encode())
        client_socket.send(credentials_string.encode())

        response = client_socket.recv(1024).decode()

        if response == LoginEnum.INVALID_LOGIN_INFO:
            self.labels[response].pack()
        elif response == LoginEnum.VALID_LOGIN_INFO:
            self.login_submit_btn.config(state='disabled')
            self.tfa_toplevel = LoginTopLevel(self.login_submit_btn)
class LoginTopLevel(tk.Toplevel):
    def __init__(self, login_submit_btn):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.login_submit_btn = login_submit_btn
        self.default_font = '', 16

        tk.Label(self, text='Enter TOTP Token',
                 font=self.default_font).pack()
        self.token_entry = tk.Entry(self, justify='center',
                                    font=self.default_font, cursor='xterm')
        self.token_entry.pack()
        tk.Button(self,text='Submit',
                  command=self.verify_totp_token,
                  font=self.default_font, cursor='hand2').pack()
    def on_close(self):
        self.login_submit_btn.config(state='normal')
        self.destroy()
    def verify_totp_token(self):
        token = self.token_entry.get()
        self.token_entry.delete(0, tk.END)
        client_socket.send(LoginEnum.SENDING_TOTP_TOKEN.encode())
        client_socket.send(token.encode())

        response = client_socket.recv(1024).decode()
        print(response)

if __name__ == '__main__':
    client_socket = connect_to_server()

    login_window = LoginWindow(title='Login')
    login_window.mainloop()




