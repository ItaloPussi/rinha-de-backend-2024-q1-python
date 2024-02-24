import os
from flask import Flask
from src.routes import client_operations_blueprint
import logging

app = Flask(__name__)
app.register_blueprint(client_operations_blueprint)

logging.getLogger('werkzeug').disabled = True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv("API_PORT"))
