from flask import Flask
import psycopg2
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    # Connect to your postgres DB
    conn = psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        database=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PW'])

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a query
    cur.execute("SELECT * FROM ev_test")

    # Retrieve query results
    records = cur.fetchall()

    return records

@app.route('/hello')
def whattup() -> str:
    return '<p>Hello hi</p>'