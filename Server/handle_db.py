import sqlite3
import common
from common import File, TFA, User, BannedWords, encrypt, decrypt
from typing import Tuple, Optional, Dict, List, Any, Union
import os
import pickle
from handle_2FA import create_new_otp

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
def pull_user_value(username, password: Optional[str]=None,
                    db_instance: Optional[DataBase]=None) -> Union[User, None]:
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

    users_data: List[Tuple[bytes]] = db_instance.cursor.fetchall()
    db_instance.close()

    all_users: List[User] = [pickle.loads(decrypt(user_data[0])) for user_data in users_data]

    for user in all_users:
        if not user.username == username:
            continue
        if password is None:
            return user
        if user.password == password:
            return user

def insert_user_value(user_obj: User):
    """
    this function gets a user object and inserts it into
    the users table
    :param user_obj: the user object
    :return:
    """
    serialized_user = encrypt(pickle.dumps(user_obj))
    run(command="""INSERT INTO users(user_obj)
                    VALUES (?)""",
        insertion_values=(serialized_user,))


def initialize_db(db_instance=None):
    """
    this function initialize the database at the start of the script
    with a table of users, a table of uploaded files, and a table for 2FA data
    only adds users that don't already exist
    :return:
    """
    run(command="""CREATE TABLE IF NOT EXISTS users(
        ID INTEGER PRIMARY KEY, user_obj BLOB)""", db_instance=db_instance)

    for user in common.users:
        serialized_user = encrypt(pickle.dumps(user))
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


    tfa_object = create_new_otp()
    insert_tfa_data(tfa_object)

    run("""CREATE TABLE IF NOT EXISTS BANNED_WORDS(
            banned_words_obj BLOB)""",
        db_instance=db_instance)

    if os.path.exists('banned_words.txt'):
        obj = BannedWords('banned_words.txt')
        insert_banned_words_obj(obj)


def add_file_to_db(file_obj: File):
    """
    inserts a file object data to the db
    :param file_obj: File type
    :return:
    """
    serialized_file = encrypt(pickle.dumps(file_obj))
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
    files = [pickle.loads(decrypt(file_data[0])) for file_data in serialized_files]
    return files

def clear_tfa_table():
    """
    Deletes all records from the tfa table
    :return:
    """
    run(command="""DELETE FROM TFA""")

def insert_tfa_data(tfa_obj: TFA):
    """
    receives a tfa object and inserts it into the db
    :param tfa_obj: tfa object
    :return:
    """
    serialized_obj = encrypt(pickle.dumps(tfa_obj))
    run(command="""INSERT INTO TFA(tfa_obj)
                    VALUES(?)""",
        insertion_values=(sqlite3.Binary(serialized_obj),))

def pull_tfa_obj(db_instance: DataBase=None) -> TFA:
    """
    pulls the (only) tfa object from the db
    :param db_instance:
    :return:
    """
    if not db_instance:
        db_instance = DataBase(db_name)

    db_instance.cursor.execute('SELECT tfa_obj FROM TFA')
    tfa_data: Tuple[bytes, None] = db_instance.cursor.fetchone()
    tfa_obj = pickle.loads(decrypt(tfa_data[0]))

    db_instance.close()
    return tfa_obj

def insert_banned_words_obj(banned_words_obj: BannedWords):
    """
    receives a banned words object and inserts it into the db
    :param banned_words_obj: banned_words object
    :return:
    """

    serialized_obj = encrypt(pickle.dumps(banned_words_obj))
    run(command="""INSERT INTO BANNED_WORDS(banned_words_obj)
                    VALUES(?)""",
        insertion_values=(sqlite3.Binary(serialized_obj),))

def pull_banned_words_obj(db_instance: DataBase=None) -> BannedWords:
    """
    pulls the (only) banned_words object from the db
    :param db_instance:
    :return:
    """
    if not db_instance:
        db_instance = DataBase(db_name)

    db_instance.cursor.execute('SELECT banned_words_obj FROM BANNED_WORDS')
    banned_words_data: Tuple[bytes, None] = db_instance.cursor.fetchone()
    banned_words = pickle.loads(decrypt(banned_words_data[0]))

    db_instance.close()
    return banned_words


if __name__ == '__main__':
    db_instance = DataBase(db_name)
    initialize_db(db_instance)


