from flask import Flask

app = Flask(__name__)

# Importar las rutas desde el subdirectorio
from api import router