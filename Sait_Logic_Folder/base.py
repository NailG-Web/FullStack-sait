import sqlite3
import os

Data_Folder_Path = os.path.join(os.path.dirname(__file__), '..', 'Data_Folder', 'database.db')

def base():
    conn = sqlite3.connect(Data_Folder_Path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
                login TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                password TEXT NOT NULL,
                task_complated INTEGER NOT NULL DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            text TEXT NOT NULL,
            inputs TEXT NOT NULL,
            outputs TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_tasks (
            login TEXT,
            task_id INTEGER,
            task_status TEXT DEFAULT 'f',
            PRIMARY KEY (login, task_id),
            FOREIGN KEY (login) REFERENCES users(login),
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    ''')

    cursor.execute('''
        INSERT OR IGNORE INTO users (login, name, surname, password)
        VALUES ('adminaccount', 'Наиль', 'Галязутинов', 'pass123')
    ''')

    conn.commit()

if __name__ == '__main__':
    base()