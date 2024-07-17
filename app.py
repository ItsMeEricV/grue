from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Docker, what up'

@app.route('/hello')
def whattup() -> str:
    return '<p>Hello hi</p>'