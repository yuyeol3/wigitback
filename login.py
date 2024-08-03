from flask import Flask, render_template, url_for, request, redirect
from flask_login import login_user, logout_user
from init import app
from model_user import User
import bcrypt
from utils.db import SALT

@app.route("/login", methods=["GET", "POST"])
def login():
    
    user_id = request.form.get('userID')
    user_pw = request.form.get('userPW')

    
    if (user_id is None or user_pw is None):
        return redirect('/')
    hashed_pw = bcrypt.hashpw(user_pw.encode("utf-8"), SALT)
    user_info = User.get_user_info(user_id, hashed_pw.decode("utf-8"))

    if user_info['result'] != "fail" and user_info['count'] != 0:
        login_info = User(
            user_id=user_info['data']['id'],
            registered_date=user_info['data']['registered_date'],
            user_type=user_info['data']['type_id']
        )

        login_user(login_info)
        return redirect("/")
    else:
        return redirect('/#login')
    
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")