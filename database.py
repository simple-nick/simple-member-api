from flask import g
import sqlite3


def connect_db():
    db = sqlite3.connect('member_api.db')
    db.row_factory = sqlite3.Row
    return db


def get_db():
    if not hasattr(g, 'sqlite3'):
        g.sqlite3 = connect_db()
    return g.sqlite3
