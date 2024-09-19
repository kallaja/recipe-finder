import sqlite3
import json
import os
from .config import Config

db_file = Config.db_file


def init_db():
    # Connect to a .db file (or create it if it doesn't exist)
    connection = sqlite3.connect(db_file, check_same_thread=False)

    # Create a cursor to interact with the database
    cursor = connection.cursor()

    # Create a table (if it doesn't exist)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            json TEXT NOT NULL
        ) 
    ''')
    connection.commit()
    # Close the database connection when operation done
    connection.close()


def pass_response_to_database(unique_name, new_json_data):
    # Connect to a .db file (or create it if it doesn't exist)
    connection = sqlite3.connect(db_file, check_same_thread=False)
    # Create a cursor to interact with the database
    cursor = connection.cursor()
    # Query the database to check if record with this unique key exists
    cursor.execute('''SELECT id, name, json
                           FROM responses''')
    rows = cursor.fetchall()

    names_list = []
    for row in rows:
        # obtain id from the row
        name = row[1]
        # add id to the list
        names_list.append(name)

    if unique_name in names_list:
        # record with this name exists
        # Update the record in the database
        cursor.execute('''
                    UPDATE responses
                    SET json = ?
                    WHERE name = ?
                ''', (json.dumps(new_json_data), unique_name))
    else:
        # record with this name doesn't exist; add it
        cursor.execute('''
                    INSERT INTO responses (NAME, json)
                    VALUES (?, ?)
                ''', (unique_name, json.dumps(new_json_data)))
    connection.commit()
    # Close the database connection when operation done
    connection.close()


def obtain_response_from_database(unique_name):
    # Connect to a .db file (or create it if it doesn't exist)
    connection = sqlite3.connect(db_file, check_same_thread=False)
    # Create a cursor to interact with the database
    cursor = connection.cursor()

    # Look for record with this unique name
    cursor.execute('''SELECT name, json
                      FROM responses
                      WHERE name = ?''', (unique_name,))
    rows = cursor.fetchall()
    connection.commit()
    # Close the database connection when operation done
    connection.close()

    if rows:
        row = rows[0]
        response_json = json.loads(row[1])
        return response_json
    else:
        print("No record found with that unique name.")
        return None


def delete_db():
    # Delete the .db file
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f'{db_file} has been deleted.')
    else:
        print(f'{db_file} does not exist.')
