import sqlite3
from datetime import datetime
import common
from common import File, TFA
from typing import Tuple, Optional, Dict, List, Any, Union
import os
import pickle

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
    returns a user object with the given user info
    :param db_instance: instance of the database
    :param username: the username
    :param password: the password (hashed)
    :return: the user object if exists, none otherwise
    """
    if not db_instance:
        db_instance = DataBase(db_name)
    db_instance.cursor.execute("SELECT user_obj FROM users")

    users_data = db_instance.cursor.fetchone()
    db_instance.close()

    users = [pickle.loads(user_data) for user_data in users_data]
    for user in users:
        if user.username == username and \
           user.password == password:
            return user


def initialize_db(db_instance=None):
    """
    this function initialize the database at the start of the script
    with a table of users, and a table of uploaded files
    only adds users that dont already exist
    :return:
    """
    run(command="""CREATE TABLE IF NOT EXISTS users(
        ID INTEGER PRIMARY KEY, user_obj BLOB)""", db_instance=db_instance)

    for user in common.users:
        serialized_user = pickle.dumps(user)
        run(command=f"""INSERT OR IGNORE INTO users (user_obj) 
            VALUES(?)""", insertion_values=(sqlite3.Binary(serialized_user),),
            db_instance=db_instance)

    run(command="""CREATE TABLE IF NOT EXISTS files(
                ID INTEGER PRIMARY KEY,
                file_obj BLOB)""",
        db_instance=db_instance)

    run(command="""CREATE TABLE IF NOT EXISTS TFA(
                    tfa_obj BLOB)""",
        db_instance=db_instance)


def add_file_to_db(file_obj: File):

    serialized_file = pickle.dumps(file_obj)
    run(command=f"""INSERT INTO files(file_obj)
                VALUES(?)""",
        insertion_values=(serialized_file,))

def pull_files(db_instance: DataBase=None,
               where_dict: Dict[str, str]=None) -> List[File]:
    """
    pulls file(s) object(s) according to given parameters
    :param db_instance: instance of the db
    :param where_dict: a dict of WHERE conditions (field_name: value)
    :return: list of all matching file objects
    """
    if not db_instance:
        db_instance = DataBase(db_name)
    if not where_dict:
        where_dict = {}

    query = f"""SELECT file_obj FROM files WHERE true"""

    values = []
    for field_name, value in where_dict.items():
        query += f' AND {field_name} = ?'
        values.append(value)
    db_instance.cursor.execute(query, tuple(values))  # commit query
    serialized_files: List[Tuple[bytes, None]] = db_instance.cursor.fetchall()

    files = [pickle.loads(file_data[0]) for file_data in serialized_files]
    return files

def clear_tfa_table():
    run(command="""DELETE FROM TFA""")

def insert_tfa_data(tfa_obj: TFA):
    serialized_obj = pickle.dumps(tfa_obj)
    run(command="""INSERT INTO TFA(tfa_obj)
                    VALUES(?)""",
        insertion_values=(sqlite3.Binary(serialized_obj),))

def pull_tfa_data(db_instance: DataBase=None) -> TFA:
    if not db_instance:
        db_instance = DataBase(db_name)

    db_instance.cursor.execute('SELECT tfa_obj FROM TFA')
    tfa_data: Tuple[TFA, None] = db_instance.cursor.fetchone()
    tfa_obj = pickle.loads(tfa_data[0])

    db_instance.close()
    return tfa_obj

if __name__ == '__main__':
    db_instance = DataBase(db_name)
    initialize_db(db_instance)


