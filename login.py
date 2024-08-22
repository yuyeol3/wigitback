from flask import Flask, render_template, url_for, request, redirect
from flask_login import login_user, logout_user, login_required, current_user
from init import app
from model_user import User
import bcrypt
from utils.db import SALT
import utils.str_consts as sconst

class LoginApi:
    @staticmethod
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
                user_type=user_info['data']['type_id'],
                email=user_info['data']['email']
            )

            login_user(login_info)
            return redirect("/")
        else:
            return redirect('/#login')
    
    @staticmethod
    @app.route("/logout")
    def logout():
        logout_user()
        return redirect("/")
    
    @staticmethod
    @app.route("/userinfo/")
    @login_required
    def userinfo():
        return dict(
            status=sconst.SUCCESS,
            content=dict(
                user_id = current_user.user_id
            )
        )
    
    @staticmethod
    @app.route("/userinfo/detailed")
    @login_required
    def userinfo_detailed():
        return dict(
            status=sconst.SUCCESS,
            content=dict(
                user_id = current_user.user_id,
                registered_date = current_user.registered_date,
                user_status = current_user.get_user_status(),
                email=current_user.email
            )
        )
    
    @staticmethod
    @app.route("/useridcheck", methods=["GET", "POST"])
    def user_id_check():
        if request.method == 'GET':
            return dict(status=sconst.INVALID_ACCESS)

        res = request.get_json()
        user_info = User.get_user_info(user_id=res["user_id"])

        return dict(status=sconst.SUCCESS, content=dict(is_usable=(user_info["count"] == 0) ))

