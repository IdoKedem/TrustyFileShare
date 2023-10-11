import sqlite3
from common import User
from typing import Tuple, Optional
import os


class DataBase:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
def run(command, db_instance=None):
    if not db_instance:
        db_instance = DataBase('Server/TFS.db')
    db_instance.cursor.execute(command)
    db_instance.connection.commit()

def pull_user_value(username, password,
                    db_instance: Optional[DataBase]=None) -> Optional[Tuple[int, str, str]]:
    """
    return a database entry corresponding to the info given
    :param db_instance: instance of the database
    :param username: the username
    :param password: the password (hashed)
    :return: the entry itself if exists, none otherwise
    """
    if not db_instance:
        db_instance = DataBase('Server/TFS.db')
    db_instance.cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password))
    return db_instance.cursor.fetchone()


def initialize_db():
    """
    this function initialize the database at the start of the script
    with a table of users, and a table of uploaded files
    only adds users that dont already exist
    :return:
    """
    run(command="""CREATE TABLE IF NOT EXISTS users(
        ID INTEGER PRIMARY KEY, username TEXT, password TEXT, isadmin BOOLEAN)""")
    users = \
        [User('Ido', '123', is_admin=True), User('Kedem', '456')]

    for user in users:
        if not pull_user_value(*user.get_login_info(),
                               db_instance=db_instance):  # user doesnt exist
            run(command=f"""INSERT INTO users (username, password, isadmin) 
                VALUES('{user.username}','{user.password}', '{user.is_admin}')""")

    run(command="""CREATE TABLE IF NOT EXISTS files(
                ID INTEGER PRIMARY KEY, filename TEXT, 
                uploaded_by TEXT, content TEXT)""")


def add_file_to_db(file_path: str, uploading_user):
    file_name = os.path.basename(file_path)
    with open(file_path, 'r') as f:
        file_content = f.read()
    run(command=f"""INSERT INTO files(filename, uploaded_by, content)
                VALUES('{file_name}', '{uploading_user}', '{file_content}')""")

if __name__ == '__main__':
    db_instance = DataBase('TFS.db')
    initialize_db()



