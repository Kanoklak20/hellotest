import os
from flask import Flask
from werkzeug.debug import DebuggedApplication
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth


app = Flask(__name__, static_folder='static')
app.url_map.strict_slashes = False

app.jinja_options = app.jinja_options.copy()
app.jinja_options.update({
    'trim_blocks': True,
    'lstrip_blocks': True
})

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = \
    'e3570366fef9b9aa5446952fc18e06eb20d832bc8103f08f'
app.config['JSON_AS_ASCII'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['GOOGLE_CLIENT_ID'] = os.getenv("GOOGLE_CLIENT_ID", None)
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv("GOOGLE_CLIENT_SECRET", None)
app.config['GOOGLE_DISCOVERY_URL'] = os.getenv("GOOGLE_DISCOVERY_URL", None)

# app.config['FACEBOOK_CLIENT_ID'] = os.getenv("FACEBOOK_CLIENT_ID", None)
# app.config['FACEBOOK_CLIENT_SECRET'] = os.getenv("FACEBOOK_CLIENT_SECRET", None)

app.config['GITHUB_CLIENT_ID']=os.getenv("GITHUB_CLIENT_ID", None)
app.config['GITHUB_CLIENT_SECRET']=os.getenv("GITHUB_CLIENT_SECRET", None)


if app.debug:
    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)
  
# Creating an SQLAlchemy instance
db = SQLAlchemy(app)
oauth = OAuth(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

from app import views  # noqa