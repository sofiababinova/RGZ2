from flask import Flask
from rgz import rgz1
from Db import db 
from Db.models import users 
from flask_login import LoginManager


app = Flask(__name__)


app.secret_key = "123"
user_db = "admin_knowledge_base_rgz"
host_ip = "127.0.0.1"
host_port = "5432"
database_name = "knowledge_base_rgz"
password = "123"

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()

login_manager.login_view = "rgz1.login"
login_manager.init_app(app)

@login_manager.user_loader 
def load_users(user_id):
    return users.query.get(int(user_id))

from rgz import rgz1
app.register_blueprint(rgz1)