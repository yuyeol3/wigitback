import os
import mimetypes
from flask import Flask, render_template, url_for, request, redirect
from flask_login import LoginManager
from model_user import User
import utils.str_consts as sconst

APP_NAME = "WIGIT"

mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")

app = Flask(APP_NAME, static_folder="assets", template_folder="./")

login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))

@login_manager.user_loader
def user_loader(user_id):
    user_info = User.get_user_info(user_id)

    login_info = User(
        user_id=user_info['data']['id'],
        registered_date=user_info['data']['registered_date'],
        user_type=user_info['data']['type_id']
    )

    return login_info

@login_manager.unauthorized_handler
def unauthorized():
    return dict(status=sconst.LOGIN_REQUIRED)