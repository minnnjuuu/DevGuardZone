# app/db_connection.py
import mysql.connector
from flask import current_app, g
from mysql.connector import Error

def get_db():
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=current_app.config['MYSQL_HOST'],
                user=current_app.config['MYSQL_USER'],
                password=current_app.config['MYSQL_PASSWORD'],
                database=current_app.config['MYSQL_DB']
            )
        except Error as e:
            print("Error connecting to database:", e)
            g.db = None
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
