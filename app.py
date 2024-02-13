from flask import Flask
from src.routes import client_operations_blueprint

app = Flask(__name__)
app.register_blueprint(client_operations_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
