import sqlite3
from flask import g

# helper functions
def connect_db():
    sql = sqlite3.connect('members.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    # check if db is there
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
