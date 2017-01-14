from flask_bootstrap import Bootstrap
from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__, static_folder="src")
app.config.from_object('config')
mongo = PyMongo(app)
Bootstrap(app)

from app import views