import sqlite3
import os

UPLOAD_PATH = 'static/uploads'

def reset():
    connection = sqlite3.connect('database.db')


    with open('schema.sql') as f:
        connection.executescript(f.read())

    connection.commit()
    connection.close()

    # clear the static/uploads folder
    for file in os.listdir(UPLOAD_PATH):
        os.remove(os.path.join(UPLOAD_PATH, file))