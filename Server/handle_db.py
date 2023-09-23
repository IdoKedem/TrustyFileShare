import sqlite3
from common import hash_text
from typing import Tuple, Generator, Union, Optional


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = hash_text(password)

    def get_login_info(self):
        return self.username, self.password
    def __str__(self):
        return \
            f'Username: {self.username}\nPassword: {self.password}'

class DataBase:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(rf'Server/{db_name}')
        self.cursor = self.connection.cursor()
def run(command):
    db_instance.cursor.execute(command)
    db_instance.connection.commit()

def initialize_db():
    """
    this function initialize the database at the start of the script
    with the permitted users
    only adds users that dont already exist
    :return:
    """
    run(command="""CREATE TABLE IF NOT EXISTS users(
        ID INTEGER PRIMARY KEY, username TEXT, password TEXT)""")
    users = \
        [User('Ido', '123'), User('Kedem', '456')]

    for user in users:
        if not pull_user_value(*user.get_login_info()):  # user doesnt exist
            run(command=f"""INSERT INTO users (username, password) 
                VALUES('{user.username}','{user.password}')""")

db_instance = DataBase('TFS.db')

if __name__ == '__main__':
    initialize_db()

def pull_user_value(username, password) -> Optional[Tuple[int, str, str]]:
    """
    return a database entry corresponding to the info given
    :param db_instance: instance of the database
    :param username: the username
    :param password: the password (hashed)
    :return: the entry itself if exists, none otherwise
    """
    global db_instance
    db_instance.cursor.execute("SELECT * FROM users WHERE "
                   f"username = '{username}' AND password = '{password}'")
    return db_instance.cursor.fetchone()

def is_login_valid(username, password) -> bool:
    return bool(pull_user_value(username=username, password=password))





