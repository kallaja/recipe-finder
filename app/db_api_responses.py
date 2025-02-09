import sqlite3
import json
from .config import Config
import requests
import os

db_file = Config.response_db_file
os.makedirs("instance", exist_ok=True)
db_path = os.path.join("instance", db_file)


def init_db() -> None:
    """Initializes the SQLite database for storing API responses."""
    connection = None
    try:
        connection = sqlite3.connect(db_path, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS responses (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL UNIQUE,
                       json TEXT NOT NULL
                       )''')
        connection.commit()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        connection.close()


def pass_response_to_database(unique_name: str, new_json_data: requests.models.Response | dict | list) -> None:
    """Stores or updates an API response in the database."""
    connection = None
    try:
        connection = sqlite3.connect(db_path, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute('''SELECT id, name, json FROM responses''')
        rows = cursor.fetchall()

        names_list = []
        for row in rows:
            name = row[1]
            names_list.append(name)

        if unique_name in names_list:
            # record with this name exists - update it
            cursor.execute('''UPDATE responses SET json = ? WHERE name = ?''',
                           (json.dumps(new_json_data), unique_name))
        else:
            cursor.execute('''INSERT INTO responses (NAME, json) VALUES (?, ?)''',
                           (unique_name, json.dumps(new_json_data)))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Database error while saving response: {e}")
    finally:
        connection.close()


def obtain_response_from_database(unique_name: str) -> requests.models.Response | dict | list | None:
    """Retrieves a stored API response from the database."""
    connection = None
    try:
        connection = sqlite3.connect(db_path, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute('''SELECT name, json FROM responses WHERE name = ?''', (unique_name,))
        row = cursor.fetchone()
        connection.commit()
        connection.close()
        return json.loads(row[1]) if row else None
    except sqlite3.Error as e:
        print(f"Database error while retrieving response: {e}")
        return None
    finally:
        connection.close()
