from flask import Flask, render_template, url_for, request, redirect
from flask_login import login_user, logout_user, login_required, current_user
from init import app
from model_user import User
import bcrypt
from utils.db import SALT, USER_PERMS, add_user, set_user, delete_user, get_history
import base64
import utils.str_consts as sconst
import re
import traceback
from utils.perms import get_permission_list

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
        commit_history = get_history(current_user.user_id, lim=20)

        return dict(
            status=sconst.SUCCESS,
            content=dict(
                user_id = current_user.user_id,
                registered_date = current_user.registered_date,
                user_status = current_user.get_user_status(),
                email=current_user.email,
                history=commit_history
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

    @staticmethod
    @app.route("/userpwdcheck", methods=["GET", "POST"])
    @login_required
    def user_pwd_check():
        if request.method == "GET":
            return dict(status=sconst.INVALID_ACCESS)
        
        res = request.get_json()
        user_pwd = base64.decodebytes(res["pwd"].encode()).decode()
        hashed_pw = bcrypt.hashpw(user_pwd.encode(), SALT).decode()
        check_res = int(User.get_user_info(current_user.user_id, hashed_pw)["count"] == 1)
        return dict(status=[sconst.FAILURE, sconst.SUCCESS][check_res])
    

    @staticmethod
    @app.route("/register", methods=['GET', 'POST'])
    def register():
        if request.method == 'GET':
            return dict(status=sconst.INVALID_ACCESS)
        
        res = request.get_json()
        if (register_check(res)):

            register_result = add_user(
                user_id=res["user_id"],
                pwd=base64.decodebytes(res["pwd"].encode()).decode(),
                email=res["email"]
            )
            return dict(status=register_result)
        
        else:
            return dict(status=sconst.UNKNOWN_ERROR)

    @staticmethod
    @app.route("/setuserinfo", methods=["GET", "POST"])
    @login_required
    def set_user_info():
        if request.method == 'GET':
            return dict(status=sconst.INVALID_ACCESS)
        try:
            res = request.get_json()
            user_id = current_user.user_id

            if "email" in res and res["email"] != "":
                set_user(user_id=user_id, email=res["email"])

            if "pwd" in res and res["pwd"] != "":
                set_user(user_id=user_id, pwd=base64.decodebytes(res["pwd"].encode()).decode())

            return dict(status=sconst.SUCCESS)
        except Exception as err:
            traceback.print_exc()
            return dict(status=sconst.UNKNOWN_ERROR)
        
    @staticmethod
    @app.route("/deleteuser", methods=["GET"])
    @login_required
    def delete_user():
        try:
            user_id = current_user.user_id
            logout_user()
            delete_user(user_id)
            return dict(status=sconst.SUCCESS)
        
        except Exception as err:
            traceback.print_exc()
            return dict(status=sconst.UNKNOWN_ERROR)
        
    @staticmethod
    @app.route("/checkmng/<string:perm_target>")
    @login_required
    def check_mng(perm_target):
        ''' 관리자 유형인지 확인 '''
        
        try:
            return get_permission_list(current_user, perm_target)
        

        except Exception as err:
            traceback.print_exc()
            return dict(status=sconst.UNKNOWN_ERROR)
        
        

def register_check(user_info):
    '''
    보내온 user_info가 vaild한지 확인
    '''
    try:
        for key in user_info:
            if user_info[key] == "":
                return False
            
        if User.get_user_info(user_info["user_id"])["count"] != 0:
            return False
        
        if (len(re.findall("\\w+@\\w+\\.\\w+", user_info["email"])) != 1):
            return False
        
        decoded_pwd = base64.decodebytes(user_info["pwd"].encode()).decode()
        
    except Exception as err:
        traceback.print_exc()
        return False
    
    return True