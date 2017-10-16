from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    port = 3000
    host = '127.0.0.1'
    app.run(host=host, port=port)