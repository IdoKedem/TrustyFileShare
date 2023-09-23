import socket
from enums import SocketEnum
from threading import Thread
import tkinter as tk





def connect_to_server() -> socket.socket:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SocketEnum.SERVER_IP, SocketEnum.PORT))
    print("connected!")

    def _print_messages():
        while True:
            print(client_socket.recv(1024).decode())
    def _send_message():
        while True:
            client_socket.send(input('enter msg \n').encode())


    Thread(target=_print_messages).start()
    Thread(target=_send_message).start()

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
        self.prepare_window()

    def prepare_window(self):
        tk.Label(text="TFS by Ido Kedem", font=('lucida', 30)).pack()

        info_frame = \
            tk.Frame(self, bd=10,
                     borderwidth=5, relief='ridge')
        info_frame.pack(pady=60)

        def _prepare_info_frame():
            tk.Label(info_frame, text='Login',
                     font=('lucida', 24)).pack()

            username_frame = \
                tk.Frame(info_frame,
                         width=400, height=100)
            _prepare_frame(frame=username_frame,
                           label_text='Username')
            password_frame = \
                tk.Frame(info_frame,
                         width=400, height=100)
            _prepare_frame(frame=password_frame,
                           label_text='Password')

            tk.Button(info_frame, text='Submit', font=('lucida' ,16),
                     height=1).pack()

        def _prepare_frame(frame, label_text):
            frame.pack()
            tk.Label(frame, text=label_text,
                     font=('lucida', 16)).pack(side=tk.LEFT)
            tk.Entry(frame,
                     font=('lucida', 16)).pack(padx=10)

        _prepare_info_frame()

if __name__ == '__main__':
    login_window = LoginWindow(title='Login')
    login_window.mainloop()




