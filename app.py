from flask import Flask

app = Flask(__name__)

# The start of bytebite :D
@app.route('/')
def index():
    return '<h1>Hello World</h1>'