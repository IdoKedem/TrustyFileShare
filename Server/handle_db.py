import sqlite3

import common
from typing import Tuple, Optional, Dict, List, Any
import os

db_name = 'TFS.db'

class DataBase:
    def __init__(self, db_name: str):
        self.db_path = DataBase.get_db_path(db_name)
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    @staticmethod
    def get_db_path(db_name: str) -> str:
        cur_directory = os.getcwd()
        db_path = os.path.join(cur_directory, db_name)
        if os.path.exists(db_path):
            return db_path
        child_directory = cur_directory + r'\Server'
        db_path = os.path.join(child_directory, db_name)
        if os.path.exists(db_path):
            return db_path
        raise ValueError("Database Not Found")
    def close(self):
        self.connection.close()

def run(command, db_instance=None,
        is_close_connection: bool=True):
    if not db_instance:
        db_instance = DataBase(db_name)
    db_instance.cursor.execute(command)
    db_instance.connection.commit()
    if is_close_connection:
        db_instance.close()

def pull_user_value(username, password,
                    db_instance: Optional[DataBase]=None,
                    is_close_connection: bool=True) -> Optional[Tuple[int, str, str]]:
    """
    return a database entry corresponding to the info given
    :param db_instance: instance of the database
    :param username: the username
    :param password: the password (hashed)
    :return: the entry itself if exists, none otherwise
    """
    if not db_instance:
        db_instance = DataBase(db_name)
    db_instance.cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password))
    user_data = db_instance.cursor.fetchone()
    db_instance.close()
    return user_data


def initialize_db(db_instance=None, is_close_connection=True):
    """
    this function initialize the database at the start of the script
    with a table of users, and a table of uploaded files
    only adds users that dont already exist
    :return:
    """
    if db_instance:
        is_close_connection = False
    run(command="""CREATE TABLE IF NOT EXISTS users(
        ID INTEGER PRIMARY KEY, username TEXT UNIQUE, 
        password TEXT, isadmin BOOLEAN)""", db_instance=db_instance,
        is_close_connection=is_close_connection)

    for user in common.users:
        run(command=f"""INSERT OR IGNORE INTO users (username, password, isadmin) 
            VALUES('{user.username}', '{user.password}', '{user.is_admin}')""",
            db_instance=db_instance, is_close_connection=is_close_connection)

    run(command="""CREATE TABLE IF NOT EXISTS files(
                ID INTEGER PRIMARY KEY, filename TEXT, 
                uploaded_by TEXT, content TEXT)""",
        db_instance=db_instance, is_close_connection=is_close_connection)


def add_file_to_db(file_name: str,
                   file_content: str,
                   uploading_user: str):
    run(command=f"""INSERT INTO files(filename, uploaded_by, content)
                VALUES('{file_name}', '{uploading_user}', '{file_content}')""")

def pull_files(db_instance: DataBase=None,
               fields: List[str]=None,
               where_dict: Dict[str, str]=None):
    """
    pulls data about files according to given parameters
    :param db_instance: instance of the db
    :param fields: which fields to pull, as a list of strings
    :param where_dict: a dict of WHERE conditions (fieldname: value)
    :return:
    """
    if not db_instance:
        db_instance = DataBase(db_name)
    if not where_dict:
        where_dict = {}

    query = f"""SELECT {', '.join(fields)} FROM files WHERE true"""

    values = []
    for field_name, value in where_dict.items():
        query += f' AND {field_name} = ?'
        values.append(value)

    db_instance.cursor.execute(query, tuple(values))
    files = db_instance.cursor.fetchall()
    print(files)
    return files


if __name__ == '__main__':
    db_instance = DataBase(db_name)
    pull_files(db_instance,
               fields=['filename', 'content'],
               where_dict={'filename': 'anat.txt',
                           'uploaded_by': 'Ido'})
    #initialize_db(db_instance=db_instance, is_close_connection=False)



