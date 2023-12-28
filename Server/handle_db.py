import sqlite3
from datetime import datetime
import common
from typing import Tuple, Optional, Dict, List, Any, Union
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

def run(command: str,
        insertion_values: Optional[Tuple]=tuple(),
        db_instance=None):
    """
    this function executes the given query
    :param command: the query to execute.
    :param insertion_values: values to insert
    :param db_instance: the instance of the db
    :return:
    """
    if not db_instance:
        db_instance = DataBase(db_name)
    db_instance.cursor.execute(command, insertion_values)
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
        db_instance = DataBase(db_name)
    db_instance.cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password))
    user_data = db_instance.cursor.fetchone()
    db_instance.close()
    return user_data


def initialize_db(db_instance=None):
    """
    this function initialize the database at the start of the script
    with a table of users, and a table of uploaded files
    only adds users that dont already exist
    :return:
    """
    run(command="""CREATE TABLE IF NOT EXISTS users(
        ID INTEGER PRIMARY KEY, username TEXT UNIQUE, 
        password TEXT, isadmin BOOLEAN)""", db_instance=db_instance)

    for user in common.users:
        run(command=f"""INSERT OR IGNORE INTO users (username, password, isadmin) 
            VALUES(?, ?, ?)""", insertion_values=(user.username, user.password, user.is_admin),
            db_instance=db_instance)

    run(command="""CREATE TABLE IF NOT EXISTS files(
                ID INTEGER PRIMARY KEY,
                filename TEXT,
                uploaded_by TEXT,
                upload_time TEXT,
                content TEXT)""",
        db_instance=db_instance)

    run(command="""CREATE TABLE IF NOT EXISTS TFA(
                    key TEXT,
                    QR_code TEXT)""",
        db_instance=db_instance)


def add_file_to_db(file_name: str,
                   uploading_user: str,
                   file_content: bytes):
    cur_time = datetime.now()
    upload_time = cur_time.strftime('%d/%m/%y %H:%M:%S')

    run(command=f"""INSERT INTO files(filename,
                                      uploaded_by, upload_time,
                                      content)
                VALUES(?, ?, ?, ?)""",
        insertion_values=(file_name, uploading_user, upload_time,
                          file_content.hex()))

def pull_files(db_instance: DataBase=None,
               fields: List[str]=None,
               where_dict: Dict[str, str]=None) -> List[Tuple]:
    """
    pulls data about files according to given parameters
    :param db_instance: instance of the db
    :param fields: which fields to pull, as a list of strings
    :param where_dict: a dict of WHERE conditions (field_name: value)
    :return: list of tuples, where in each tuple are the requested fields
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
    return files

def clear_tfa_table():
    run(command="""DELETE FROM TFA""")

def insert_tfa_data(key, img_data):
    run(command="""INSERT INTO TFA(key,
                                   QR_code)
                    VALUES(?, ?)""",
        insertion_values=(key, img_data))

def pull_tfa_data(db_instance: DataBase=None):
    if not db_instance:
        db_instance = DataBase(db_name)

    db_instance.cursor.execute('SELECT * FROM TFA')
    tfa_data: Tuple = db_instance.cursor.fetchone()
    db_instance.close()
    return tfa_data

if __name__ == '__main__':
    db_instance = DataBase(db_name)
    initialize_db(db_instance)


