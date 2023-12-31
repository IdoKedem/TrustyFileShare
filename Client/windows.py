import os.path
from tkinter import messagebox
from common import LoginEnum, hash_text, User, FileEnum, \
    encapsulate_data, decapsulate_data, File, TryLogin
import tkinter as tk
from tkinter import filedialog
from typing import List, Dict, Optional, Union, Tuple, Any
import socket
import time

cur_dir = os.path.join(os.getcwd(),
                       r'TrustyFileShare\Client')


class BaseWindow(tk.Tk):
    def __init__(self, title: str, client_socket: socket.socket,
                 width: int=800, height: int=800):
        super().__init__()
        self.geometry(f'{width}x{height}')
        self.resizable(False, False)
        self.title(f'TFS - {title}')

        self.default_font = '', 16

        self.client_socket = client_socket


class BaseFrame(tk.Frame):
    def __init__(self,
                 displayed_on: Union[BaseWindow, 'BaseFrame'],
                 frame_args: Optional=None):
        if not frame_args:
            frame_args = {}

        super().__init__(master=displayed_on, **frame_args)
        self.displayed_on = displayed_on

        self.default_font = displayed_on.default_font
        self.widgets: Dict['TkWidget', Dict[str, str]] = {}
        self.client_socket = displayed_on.client_socket

    def pack_widgets(self):
        for widget, options in self.widgets.items():
            widget.pack(**options)

    def prepare_form_entry(self, entry_name, entry_show=None):
        """
        prepares a frame as a form.
        :param entry_name: name of the entry, shown in label
        :param entry_show: entry's 'show' param
        :return: the entry, to fetch output
        """
        self.pack()
        tk.Label(self, text=entry_name + ':',
                 font=self.default_font).pack(side=tk.LEFT)
        entry = tk.Entry(self, border=2, show=entry_show,
                         font=self.default_font, cursor='xterm')
        entry.pack()
        return entry




class BaseForm(BaseFrame):
    def __init__(self,
                 displayed_on: Union[BaseWindow, BaseFrame, 'BaseForm'],
                 form_title: str,
                 entries_dict: Dict[str, Dict[str, Any]],
                 frame_args: Optional=None):

        self.form_title = form_title
        self.entries_dict = entries_dict
        super().__init__(displayed_on, frame_args)

        self.frames, self.entries = [], []
        self.prepare_form()

    def prepare_form(self):
        """
        prepares the login form, with all its widgets
        :return:
        """
        tk.Label(self, text=self.form_title,
                 font=('', 24)).pack()

        for entry_name, entry_data in self.entries_dict.items():
            cur_frame = \
                BaseFrame(self,
                          entry_data['frame_args'])
            self.frames.append(cur_frame)
            self.entries.append(cur_frame.prepare_form_entry(
                                          entry_name, entry_data['show']))
        for frame in self.frames:
            frame.pack()



class MainWindow(BaseWindow):
    def __init__(self,
                 client_socket: socket.socket,
                 is_skip_login=False, logged_user: User=None):
        super().__init__(title='Main Menu',
                         client_socket=client_socket)
        self.user = logged_user

        self.login_menu = LoginMenu(self)

        self.main_menu = MainMenu(self,
                                   highlightbackground='blue',
                                   highlightthickness=2)

        self.downloads_menu = DownloadsMenu(self,
                                             highlightbackground='green',
                                             highlightthickness=2)
        self.create_user_menu = CreateUserMenu(self,
                                               highlightbackground='blue',
                                               highlightthickness=2)
        if not is_skip_login:
            self.login_menu.pack()
        else:
            self.main_menu.pack()

    def show_downloads_menu(self):
        self.main_menu.pack_forget()
        self.downloads_menu.file_listbox_frame.show_file_titles()
        self.downloads_menu.pack(fill='x')
    def show_main_menu(self):
        self.downloads_menu.pack_forget()
        self.main_menu.pack()
    def show_create_user_menu(self):
        self.main_menu.pack_forget()
        self.create_user_menu.pack()

    def upload_file_to_db(self):
        file_path = filedialog.askopenfilename(
            title='Select a file to upload',
            filetypes=FileEnum.SUPPORTED_FILE_TYPES)
        with open(file_path, 'rb') as file:
            file_content = file.read()
        if not file_content:
            messagebox.showerror(title='Error',
                                 message='Unable to upload an empty file')
            return
        file_name = os.path.basename(file_path)

        uploaded_file = File(file_name=file_name,
                             uploading_user=self.user,
                             file_content=file_content)

        file_details_string: bytes = \
            encapsulate_data([file_name,
                              self.user.username, file_content])
        file_content_size = len(file_content)

        self.client_socket.send(FileEnum.SENDING_FILE_DATA.encode())
        self.client_socket.send(str(file_content_size).encode())
        time.sleep(0.2)
        self.client_socket.send(file_details_string)

        file_status = self.client_socket.recv(1024)
        if file_status == FileEnum.FILE_REJECTED.encode():
            messagebox.showerror(title='BANNED WORDS DETECTED',
                                 message='SYSTEM CENSORED BANNED WORDS')


class LoginTopLevel(tk.Toplevel):
    def __init__(self,
                 displayed_on: MainWindow, logged_user: User):
        super().__init__()
        self.parent = displayed_on
        self.user = logged_user
        self.client_socket = self.parent.client_socket

        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.default_font = '', 16

        tk.Label(self, text='Enter TOTP Token',
                 font=self.default_font).pack()
        self.token_entry = tk.Entry(self, justify='center',
                                    font=self.default_font, cursor='xterm')
        self.token_entry.pack()
        tk.Button(self, text='Submit',
                  command=self.verify_totp_token,
                  font=self.default_font, cursor='hand2').pack()
    def on_close(self):
        self.parent.deiconify()
        self.destroy()
    def verify_totp_token(self):
        token = self.token_entry.get()
        self.token_entry.delete(0, tk.END)
        if not token:
            return
        self.client_socket.send(LoginEnum.SENDING_TOTP_TOKEN.encode())
        self.client_socket.send(token.encode())

        response = self.client_socket.recv(1024).decode()
        #print(response)
        if response == LoginEnum.VALID_TOTP_TOKEN:
            self.destroy()
            self.parent.destroy()
            MainWindow(client_socket=self.client_socket,
                       logged_user=self.user,
                       is_skip_login=True).mainloop()





class LoginMenu(BaseFrame):
    def __init__(self,
                 displayed_on: MainWindow,
                 **frame_args):
        super().__init__(displayed_on=displayed_on,
                         frame_args=frame_args)
        f_args = \
            {
               'highlightbackground': 'green',
               'highlightthickness': 2
               }

        entries_dict = {
            'Username': {'frame_args': {'width': '400',
                                        'height': '100',
                                        'pady': '15'},
                         'show': None},
            'Password': {'frame_args': {'width': '400',
                                        'height': '100',
                                        'pady': '5'},
                         'show': '*'}
        }
        self.info_form = \
            BaseForm(self,
                     form_title='Login',
                     entries_dict=entries_dict,
                     frame_args=f_args)

        self.try_again_label = \
            tk.Label(self.info_form, text='Try Again',
                     fg='red', font=('', 12))

        self.submit_btn = tk.Button(
            master=self.info_form,
            text='Submit',
            command=self.check_login,
            height=1, font=self.default_font, cursor='hand2'
        )
        self.submit_btn.pack()

        #self.entries = []

        #self.prepare_form()

        self.widgets = {
            tk.Label(text="TFS by Ido Kedem",
                     font=('', 30)): {},
            self.info_form: {'pady': 60}
        }
        self.pack_widgets()

    def check_login(self):
        """
        validates the inputted credentials with the server
        :return:
        """
        credentials_data = []

        for entry_index, entry in enumerate(self.info_form.entries):
            entry_text = entry.get()
            entry.delete(0, tk.END)
            if entry_index == 1:    # password entry
                entry_text = hash_text(entry_text)

            credentials_data.append(entry_text)
        credentials_string = encapsulate_data(credentials_data)

        # try_login_info = TryLogin(username=username,
        #                           password=password)

        self.client_socket.send(LoginEnum.SENDING_LOGIN_INFO.encode())
        self.client_socket.send(credentials_string)

        response = self.client_socket.recv(1024).decode()

        if response == LoginEnum.INVALID_LOGIN_INFO:
            self.try_again_label.pack()

        elif response == LoginEnum.VALID_LOGIN_INFO:
            user_data = self.client_socket.recv(1024)
            username, password, is_admin = decapsulate_data(user_data)
            self.user = User(username.decode(), password.decode(), is_admin.decode())

            LoginTopLevel(displayed_on=self.displayed_on,
                          logged_user=self.user)
            self.displayed_on.withdraw()

class MainMenu(BaseFrame):
    def __init__(self,
                 displayed_on: MainWindow,
                 **frame_args):

        super().__init__(displayed_on=displayed_on,
                         frame_args=frame_args)
        self.widgets = {
            tk.Button(self, text='Upload',
                      command=displayed_on.upload_file_to_db,
                      font=self.default_font): {},
            tk.Button(self, text='Download',
                      command=displayed_on.show_downloads_menu,
                      font=self.default_font): {},
            tk.Button(self, text='Create User',
                      command=displayed_on.show_create_user_menu,
                      font=self.default_font): {},
        }
        self.pack_widgets()



class DownloadsMenu(BaseFrame):
    def __init__(self,
                 displayed_on: MainWindow,
                 **frame_args):
        super().__init__(displayed_on, frame_args)

        self.file_listbox_frame = \
            FileListboxFrame(displayed_on=self,
                             highlightbackground='magenta',
                             highlightthickness=2)

        self.widgets = {
            tk.Label(self,
                     text='choose a file to download:',
                     font=self.default_font): {},
            tk.Button(self,
                      text='Back',
                      font=self.default_font,
                      command=self.displayed_on.show_main_menu): {},
            self.file_listbox_frame: {'fill': 'x'},
            tk.Button(self,
                      text='↻',
                      font=('', 16),
                      command=self.file_listbox_frame.show_file_titles,
                      bg='lightgrey',
                      width=2,
                      height=1): {'side': tk.LEFT},
            tk.Button(self,
                      text='Download',
                      font=self.default_font,
                      command=self.request_file): {}
        }
        self.pack_widgets()
    def request_file(self):
        requested_file_ind: int = self.file_listbox_frame.listbox.curselection()[0] + 1
        self.client_socket.send(FileEnum.REQUESTING_FILE_DATA.encode())
        self.client_socket.send(str(requested_file_ind).encode())

        file_name = self.client_socket.recv(1024).decode()
        #print(file_name)
        file_size = int(self.client_socket.recv(1024).decode())
        file_content = self.client_socket.recv(file_size)
        #print(file_content)

        if not os.path.exists(cur_dir + r'\Downloads'):
            os.mkdir(cur_dir + r'\Downloads')
        with open(cur_dir + rf'\Downloads\{file_name}', 'wb') as f:
            f.write(file_content)


class FileListboxFrame(BaseFrame):
    def __init__(self,
                 displayed_on: DownloadsMenu,
                 **frame_args):

        super().__init__(displayed_on, frame_args=frame_args)
        self.client_socket = \
            self.displayed_on.displayed_on.client_socket

        self.scrollbar = tk.Scrollbar(self)
        self.listbox = tk.Listbox(self,
                       selectmode='single',
                       yscrollcommand=self.scrollbar.set,
                       font=self.default_font)

        self.widgets = {
            self.scrollbar: {'side': 'right',
                             'fill': 'y'},
            self.listbox: {'fill': 'x'}
        }
        self.pack_widgets()

    def show_file_titles(self):
        self.listbox.delete(0, tk.END)
        self.client_socket.send(
            FileEnum.REQUESTING_ALL_FILE_TITLES.encode())
        file_count = int(self.client_socket.recv(1024))

        file_titles: List[List[bytes, bytes, bytes]] = []
        for _ in range(file_count):
            file_title: Tuple[bytes, ...] = decapsulate_data(
                self.client_socket.recv(1024))
            file_titles.append([*file_title])
            self.client_socket.send(b'ready')
        print(file_titles)

        for ind, row_data in enumerate(file_titles):
            filename, uploaded_by, upload_time = row_data
            formatted_row = \
                f'{ind + 1}. {filename.decode()} ({uploaded_by.decode()}, {upload_time.decode()})'
            self.listbox.insert(tk.END, formatted_row)


class CreateUserMenu(BaseFrame):
    def __init__(self,
                 displayed_on: MainWindow,
                 **frame_args):
        super().__init__(displayed_on, frame_args)
        self.entries = []

        f_args = \
            {
               'highlightbackground': 'pink',
               'highlightthickness': 2
               }

        entries_dict = {
            'Username': {'show': None,
                         'frame_args': {'width': '400',
                                        'height': '100',
                                        'pady': '15'}},
            'Password': {'show': '*',
                         'frame_args': {'width': '400',
                                        'height': '100',
                                        'pady': '5'}}
        }
        self.info_form = BaseForm(self, form_title='Create New User',
                                  entries_dict=entries_dict,
                                  frame_args=f_args)
        tk.Button(
            master=self.info_form,
            text='Submit',
            command=lambda: print(2),
            height=1, font=self.default_font, cursor='hand2'
        ).pack()

        self.widgets = {
            self.info_form: {}
        }
        self.pack_widgets()

    def prepare_form(self):
        """
        prepares the login form, with all its widgets
        :return:
        """
        tk.Label(self.info_form, text='Create New User',
                 font=('', 24)).pack()
        username_frame = \
            BaseFrame(self.info_form,
                      frame_args={
                          'width': '400',
                          'height': '100',
                          'pady': '15'})
        self.entries.append(
            username_frame.prepare_form_entry('Username'))

        password_frame = \
            BaseFrame(self.info_form,
                      frame_args={
                          'width': '400',
                          'height': '100',
                          'pady': '5'})
        self.entries.append(
            password_frame.prepare_form_entry('Password',
                                              entry_show='*'))

        self.submit_btn = tk.Button(
            master=self.info_form,
            text='Submit',
            command=lambda: 0,
            height=1, font=self.default_font, cursor='hand2'
        )
        username_frame.pack()
        password_frame.pack()
        self.submit_btn.pack()


