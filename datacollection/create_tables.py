import sqlite3

db_path = '../frontend/db.sqlite3'

conn = sqlite3.connect(db_path)
conn.execute('PRAGMA foreign_keys = ON;')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    search_query TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    queryid INTEGER NOT NULL,
    publishdate DATE NOT NULL,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    url TEXT NOT NULL,
    FOREIGN KEY (queryid) REFERENCES queries(id) ON DELETE CASCADE
)
''')

conn.commit()