#Datenbank erstellen (Falls keine existiert)
import sqlite3

#Verbindung zur Datenbank herstellen
def get_connection():
    connection = sqlite3.connect("schulmanager.db")
    connection.row_factory = sqlite3.Row
    return connection

#Datenbank erstellen
def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            category TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            grade REAL NOT NULL,
            weight INTEGER NOT NULL,
            grade_type TEXT NOT NULL,
            date TEXT,
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    """)

    connection.commit()
    connection.close()