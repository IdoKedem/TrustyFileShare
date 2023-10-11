from common import LoginEnum, hash_text, User, FileEnum
import tkinter as tk
from tkinter import filedialog
from typing import List, Dict
import socket


class BaseWindow(tk.Tk):
    def __init__(self, title: str, client_socket: socket.socket,
                 width: int=800, height: int=800):
        super().__init__()
        self.geometry(f'{width}x{height}')
        self.resizable(False, False)
        self.title(f'TFS - {title}')

        self.default_font = '', 16

        self.client_socket = client_socket


class LoginWindow(BaseWindow):
    def __init__(self, title: str, client_socket: socket.socket):
        super().__init__(title, client_socket)

        self.entries: List[tk.Entry] = []
        self.labels: Dict[str, tk.Label] = {}

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
        credentials_string = ''

        for entry_index, entry in enumerate(self.entries):
            entry_text = entry.get()
            entry.delete(0, tk.END)
            if entry_index == 1:    # password entry
                entry_text = hash_text(entry_text)

            credentials_string += ',' + entry_text

        self.client_socket.send(LoginEnum.SENDING_LOGIN_INFO.encode())
        self.client_socket.send(credentials_string.encode())

        response = self.client_socket.recv(1024).decode()

        if response == LoginEnum.INVALID_LOGIN_INFO:
            self.labels[response].pack()
        elif response == LoginEnum.VALID_LOGIN_INFO:
            user_data = self.client_socket.recv(1024).decode()
            _, username, password, is_admin = user_data.split(',')
            self.user = User(username, password, is_admin)

            self.login_submit_btn.config(state='disabled')
            LoginTopLevel(login_window=self, logged_user=self.user)
            self.withdraw()
class LoginTopLevel(tk.Toplevel):
    def __init__(self, login_window: LoginWindow, logged_user: User):
        super().__init__()
        self.parent = login_window
        self.user = logged_user
        self.client_socket = self.parent.client_socket

        self.protocol('WM_DELETE_WINDOW', self.on_close)
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
        self.parent.login_submit_btn.config(state='normal')
        self.parent.deiconify()
        self.destroy()
    def verify_totp_token(self):
        token = self.token_entry.get()
        self.token_entry.delete(0, tk.END)
        self.client_socket.send(LoginEnum.SENDING_TOTP_TOKEN.encode())
        self.client_socket.send(token.encode())

        response = self.client_socket.recv(1024).decode()
        print(response)
        if response == LoginEnum.VALID_TOTP_TOKEN:
            self.destroy()
            self.parent.destroy()
            MainWindow(title='Main Window',
                       client_socket=self.client_socket,
                       logged_user=self.user).mainloop()


class MainWindow(BaseWindow):
    def __init__(self, title,
                 client_socket: socket.socket, logged_user: User):
        super().__init__(title=title,
                         client_socket=client_socket)
        self.user = logged_user

        tk.Button(text='Upload', command=self.upload_file_to_db,
                  font=self.default_font).pack()
        tk.Button(text='Download',
                  font=self.default_font).pack()

    def upload_file_to_db(self):
        file_path = filedialog.askopenfilename()
        print(file_path)
        print(self.user.username)
        file_details_string = \
            f',{file_path},{self.user.username}'
        self.client_socket.send(FileEnum.SENDING_FILE_DATA.encode())
        self.client_socket.send(file_details_string.encode())





