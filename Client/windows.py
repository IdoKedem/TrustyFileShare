import os.path
from tkinter import messagebox
from common import UserEnum, hash_text, User, FileEnum, \
    File, \
    send_pickle_obj, recv_pickle_obj, UserEnum, TFA
from PIL import Image, ImageTk
from abc import abstractmethod

import common
import tkinter as tk
from tkinter import filedialog
from typing import List, Dict, Optional, Union, Tuple, Any
import socket
import time
import pickle

cur_dir = os.path.join(os.getcwd())
if os.path.basename(cur_dir) != 'Client':
    cur_dir = os.path.join(cur_dir, 'Client')


class BaseWindow(tk.Tk):
    """
    A base class for all windows
    """
    def __init__(self, title: str, client_socket: socket.socket,
                 width: int=600, height: int=600):
        super().__init__()
        self.geometry(f'{width}x{height}')
        self.resizable(False, False)
        self.title(f'TFS - {title}')

        self.default_font = '', 16

        self.client_socket = client_socket


class BaseFrame(tk.Frame):
    """
    A base class for all frames
    """
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
    """
    A base class for all forms
    """

    def __init__(
            self,
             displayed_on: Union[BaseWindow, BaseFrame, 'BaseForm'],
             form_title: str,
             entries_config_dict: Dict[str, Dict[str, Any]],
             frame_args: Optional=None):

        self.form_title = form_title
        self.entries_config_dict = entries_config_dict
        super().__init__(displayed_on, frame_args)

        self.frames = []
        self.entries_dict: Dict[str, tk.Entry] = {}
        self.prepare_form()

    def prepare_form(self):
        """
        prepares the login form, with all its widgets
        :return:
        """
        tk.Label(self, text=self.form_title,
                 font=('', 24)).pack()

        for entry_name, entry_data in self.entries_config_dict.items():
            cur_frame = \
                BaseFrame(self,
                          entry_data['frame_args'])
            self.frames.append(cur_frame)
            self.entries_dict[entry_name] = \
                cur_frame.prepare_form_entry(
                                             entry_name,
                                             entry_data['show'])
        for frame in self.frames:
            frame.pack()

class BaseMenu(BaseFrame):
    def __init__(self,
                 displayed_on: BaseWindow,
                 add_back_btn=True,
                 frame_args: Optional=None):
        super().__init__(displayed_on, frame_args)
        if add_back_btn:
            tk.Button(
                self,
                text='Back',
                font=self.default_font,
                command=self.show_main_menu).pack()

    def hide_menu(self):
        self.pack_forget()
    def show_menu(self, to_hide: 'BaseMenu'):
        to_hide.hide_menu()
        self.pack()
    def show_main_menu(self):
        self.displayed_on.main_menu.show_menu(to_hide=self)

class MainWindow(BaseWindow):
    def __init__(self,
                 client_socket: socket.socket,
                 is_skip_login=False, logged_user: User=None):
        super().__init__(title='Main Menu',
                         client_socket=client_socket)
        self.user = logged_user

        self.login_menu = LoginMenu(self)

        if not is_skip_login:
            self.login_menu.pack()
            return

        self.main_menu = MainMenu(self,
                                  logged_user=self.user)

        self.downloads_menu = DownloadsMenu(self)

        self.create_user_menu = CreateUserMenu(self)
        self.tfa_menu = TFAMenu(self)

        self.main_menu.pack()

    def upload_file_to_db(self):
        """
        opens a file selection dialog and uploads the
        selected file to the db
        :return:
        """
        try:
            file_path = filedialog.askopenfilename(
                title='Select a file to upload',
                filetypes=FileEnum.SUPPORTED_FILE_TYPES)
            with open(file_path, 'rb') as file:
                file_content = file.read()
        except FileNotFoundError:
            file_content = ''

        if not file_content:
            messagebox.showerror(title='Error',
                                 message='Unable to upload an empty file')
            return
        file_name = os.path.basename(file_path)

        uploaded_file = File(file_name=file_name,
                             uploading_user=self.user,
                             file_content=file_content)

        self.client_socket.send(FileEnum.SENDING_FILE_DATA.encode())
        send_pickle_obj(uploaded_file, self.client_socket)

        file_status = self.client_socket.recv(1024)
        if file_status == FileEnum.FILE_REJECTED.encode():
            messagebox.showerror(title='BANNED WORDS DETECTED',
                                 message='SYSTEM CENSORED BANNED WORDS')
        else:
            messagebox.showinfo(title='Success',
                                message='Successfully uploaded')


class TFADialog(tk.Toplevel):
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

        self.try_again_label = \
            tk.Label(self, text='Try Again',
                     fg='red', font=('', 12))

    def on_close(self):
        self.parent.deiconify()
        self.destroy()
    def verify_totp_token(self):
        token = self.token_entry.get()
        self.token_entry.delete(0, tk.END)
        if not token:
            return
        self.client_socket.send(UserEnum.SENDING_TOTP_TOKEN.encode())
        self.client_socket.send(token.encode())

        response = self.client_socket.recv(1024).decode()

        if response == UserEnum.VALID_INFO:
            self.destroy()
            self.parent.destroy()
            MainWindow(client_socket=self.client_socket,
                       logged_user=self.user,
                       is_skip_login=True).mainloop()
        else:
            self.try_again_label.pack()

#TODO: fix banned words

class LoginMenu(BaseMenu):
    def __init__(self,
                 displayed_on: MainWindow,
                 **frame_args):
        super().__init__(displayed_on=displayed_on,
                         add_back_btn=False,
                         frame_args=frame_args)
        f_args = \
            {
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

        self.user = None

        self.info_form = \
            BaseForm(self,
                     form_title='Login',
                     entries_config_dict=entries_dict,
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
        username = self.info_form.entries_dict['Username'].get()
        password = self.info_form.entries_dict['Password'].get()

        for entry in self.info_form.entries_dict.values():
            entry.delete(0, tk.END)

        login_try = User(username=username,
                         password=password)

        self.client_socket.send(UserEnum.SENDING_LOGIN_INFO.encode())
        send_pickle_obj(login_try, self.client_socket)

        response = self.client_socket.recv(1024).decode()

        if response == UserEnum.INVALID_INFO:
            self.try_again_label.pack()

        elif response == UserEnum.VALID_INFO:
            self.user = recv_pickle_obj(self.client_socket)

            TFADialog(displayed_on=self.displayed_on,
                      logged_user=self.user)
            self.displayed_on.withdraw()

class MainMenu(BaseMenu):
    def __init__(self,
                 displayed_on: MainWindow,
                 logged_user: User,
                 **frame_args):

        super().__init__(displayed_on=displayed_on,
                         add_back_btn=False,
                         frame_args=frame_args)
        self.widgets = {
            tk.Label(self,
                     text='Hello ' + logged_user.get_plain_username(),
                     font=self.default_font): {}
        }

        self.user_widgets_frame = BaseFrame(self)
        self.add_user_accessible_widgets()

        self.widgets.update(self.user_widgets_frame.widgets)

        if logged_user.is_admin:
            self.admin_widgets_frame = BaseFrame(self)
            self.add_admin_accessible_widgets()

            self.widgets.update(self.admin_widgets_frame.widgets)

        self.pack_widgets()

    def add_user_accessible_widgets(self):
        self.user_widgets_frame.widgets = {
            tk.Button(self, text='Upload',
                      command=self.displayed_on.upload_file_to_db,
                      font=self.default_font): {},
            tk.Button(self, text='Download',
                      font=self.default_font,
                      command=lambda:
                      self.displayed_on.downloads_menu.show_menu(
                          to_hide=self)): {}
        }
        self.user_widgets_frame.pack()

    def add_admin_accessible_widgets(self):
        self.admin_widgets_frame.widgets = {
            tk.Button(self, text='Create User',
                      font=self.default_font,
                      command=lambda:
                      self.displayed_on.create_user_menu.show_menu(
                          to_hide=self)): {},
            tk.Button(self, text='Show 2FA QR',
                      font=self.default_font,
                      command=lambda:
                      self.displayed_on.tfa_menu.show_menu(
                          to_hide=self)): {}}
        self.admin_widgets_frame.pack()


class DownloadsMenu(BaseMenu):
    def __init__(self,
                 displayed_on: MainWindow,
                 **frame_args):
        super().__init__(displayed_on, frame_args=frame_args)

        self.file_listbox_frame = \
            FileListboxFrame(displayed_on=self)

        self.widgets = {
            tk.Label(self,
                     text='Choose a file to download:',
                     font=self.default_font): {},
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

    def show_menu(self, to_hide: 'BaseMenu'):
        to_hide.pack_forget()
        self.file_listbox_frame.show_file_titles()
        self.pack(fill='x')

    def request_file(self):
        """
        request a file object from the server and saves it locally
        :return:
        """
        if not self.file_listbox_frame.listbox.curselection():  # no file selected
            messagebox.showerror(title='Error',
                                 message='Please select a file')
            return

        requested_file_ind: int = self.file_listbox_frame.listbox.curselection()[0] + 1
        self.client_socket.send(FileEnum.REQUESTING_FILE_DATA.encode())
        self.client_socket.send(str(requested_file_ind).encode())

        file: File = recv_pickle_obj(self.client_socket)[0]

        if not os.path.exists(cur_dir + r'\Downloads'):
            os.mkdir(cur_dir + r'\Downloads')
        with open(cur_dir + rf'\Downloads\{file.name}', 'wb') as f:
            f.write(file.content)
        messagebox.showinfo(title='Success',
                            message='Successfully Downloaded')

class FileListboxFrame(BaseFrame):
    def __init__(self,
                 displayed_on: DownloadsMenu,
                 **frame_args):

        super().__init__(displayed_on, frame_args=frame_args)
        self.client_socket = \
            self.displayed_on.displayed_on.client_socket

        self.x_scrollbar = tk.Scrollbar(self, orient='horizontal')
        self.y_scrollbar = tk.Scrollbar(self, orient='vertical')
        self.listbox = tk.Listbox(self,
                       selectmode='single',
                       xscrollcommand=self.x_scrollbar.set,
                       yscrollcommand=self.y_scrollbar.set,
                       font=self.default_font)

        self.widgets = {
            self.x_scrollbar: {'side': 'bottom',
                               'fill': 'x'},
            self.y_scrollbar: {'side': 'right',
                             'fill': 'y'},
            self.listbox: {'fill': 'x'}
        }

        self.x_scrollbar.config(command=self.listbox.xview)
        self.y_scrollbar.config(command=self.listbox.yview)

        self.pack_widgets()

    def show_file_titles(self):
        """
        show details about all files in the database
        :return:
        """
        self.listbox.delete(0, tk.END)
        self.client_socket.send(
            FileEnum.REQUESTING_FILE_DATA.encode())
        self.client_socket.send(b'-1') # get all files

        all_files: List[File] = recv_pickle_obj(self.client_socket)

        for ind, file in enumerate(all_files):
            decrypted_username = \
                common.decrypt(file.uploading_user.username).decode()
            formatted_row = \
                f'{ind + 1}. {file.name} ({decrypted_username},' \
                f' {file.upload_time})'
            self.listbox.insert(tk.END, formatted_row)


class CreateUserMenu(BaseMenu):
    def __init__(self,
                 displayed_on: MainWindow,
                 **frame_args):
        super().__init__(displayed_on, frame_args=frame_args)

        f_args = \
            {
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
                                  entries_config_dict=entries_dict,
                                  frame_args=f_args)
        self.is_admin = tk.IntVar()
        is_admin_btn = \
            tk.Checkbutton(self.info_form, text='Is Admin?',
                       variable=self.is_admin, font=self.default_font)
        is_admin_btn.pack()

        tk.Button(
            master=self.info_form,
            text='Submit',
            command=self.create_user,
            height=1, font=self.default_font, cursor='hand2'
        ).pack()

        self.post_creation_frame = \
            BaseFrame(self, {})


        self.widgets = {
            self.info_form: {},
            self.post_creation_frame: {}
        }
        self.pack_widgets()


    def create_user(self):
        username = self.info_form.entries_dict['Username'].get()
        password = self.info_form.entries_dict['Password'].get()

        if not username:
            messagebox.showerror(title='Error',
                                 message='Must fill in username')
            return
        if not password:
            messagebox.showerror(title='Error',
                                 message='Must fill in password')
            return

        for entry in self.info_form.entries_dict.values():
            entry.delete(0, tk.END)


        new_user = User(username=username,
                        password=password,
                        is_admin=bool(self.is_admin.get()))

        self.client_socket.send(UserEnum.CREATE_NEW_USER.encode())
        send_pickle_obj(new_user, self.client_socket)

        response = self.client_socket.recv(1024).decode()
        if response == UserEnum.INVALID_INFO:
            messagebox.showerror(title='Error',
                                 message='Username already exists')
        elif response == UserEnum.VALID_INFO:
            messagebox.showinfo(title='Success',
                                message='User created successfully')

class TFAMenu(BaseMenu):
    def __init__(self,
                 displayed_on: MainWindow,
                 **frame_args):
        super().__init__(displayed_on, frame_args=frame_args)
        self.tfa_obj: TFA = None
        self.qr_label: tk.Label = None

        self.qr_photo = None

    def show_menu(self, to_hide: BaseMenu):
        to_hide.hide_menu()

        self.client_socket.send(UserEnum.REQUESTING_2FA_OBJECT.encode())
        self.tfa_obj: TFA = recv_pickle_obj(self.client_socket)

        img_path = cur_dir + r'\img.png'
        with open(img_path, 'wb') as f:
            f.write(self.tfa_obj.qr_img)

        image = Image.open(img_path)
        self.qr_photo = ImageTk.PhotoImage(image)

        os.remove(img_path)

        self.qr_label = tk.Label(self, image=self.qr_photo)
        self.qr_label.pack()

        self.pack()

    def hide_menu(self):
        self.qr_label.pack_forget()
        self.pack_forget()


