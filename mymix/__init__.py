from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, static_folder='public', template_folder='views')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

#an sqlalchemy database instance
db = SQLAlchemy(app) 

from mymix import routes


