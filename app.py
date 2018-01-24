#!/usr/bin/env python
# coding: utf-8


from flask import Flask,Response, request, session, g, redirect, url_for, \
    abort, render_template, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from contextlib import closing
import requests
from datetime import datetime, timedelta
import sqlite3
import os
from werkzeug.utils import secure_filename
import json
import numpy as np
import sys
import importlib
from flask.ext.login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user ,current_user
#import coffee_twitter.py as ct



# Create application instance
app = Flask(__name__)
app.secret_key = 'woretachi'  # Change this!
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login" # login_viewのrouteを設定
# Load configuration
# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)
app.config.from_pyfile('config.py')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/coffee_manage.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'coffee_user2'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    twitter = db.Column(db.String(80))

    def __init__(self, username, password, twitter):
        self.username = username
        self.password = password
        self.twitter = twitter

    def __repr__(self):
        return '<User %r>' % self.username

class Coffee_Count(db.Model):
    __tablename__ = 'coffee_count2'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    timestamp = db.Column(db.DATETIME, nullable=True)
    check = db.Column(db.Boolean)

    def __init__(self, user_id, timestamp, check):
        self.user_id = user_id
        self.timestamp = timestamp
        self.check = check



class Login_User(UserMixin):

    def __init__(self, id):
        self.id = id
        user = db.session.query(User).filter_by(id=id).first()
        self.name = user.username
        self.password = user.password
        self.twitter = user.twitter

    def __repr__(self):
        return "%d/%s/%s/%d/%s" % (int(self.id), self.name, self.password, self.twitter)



# Placeholder: View function
@app.route('/')
@login_required
def index():
    print(current_user.name)
    print(current_user.password)
    title = "ようこそ"
    coffee_num = {}
    check = {}
    for i in range(db.session.query(User).count()):
        coffee_num[i+1] = db.session.query(Coffee_Count).filter_by(user_id=i+1).count()
        check[i+1] = db.session.query(Coffee_Count).filter_by(user_id=i+1, check=False).count()
    print(coffee_num)
    users = User.query.all()
    return render_template('index.html',
                        title=title, users=users, coffee_num=coffee_num, check=check)

@app.route('/post', methods=['GET', 'POST'])
def post():
    title = "こんにちは"
    if request.method == 'POST':
        name = request.form['name']
        user = User(name, 0)
        db.session.add(user)
        db.session.commit()
        users = User.query.all()
        return render_template('index.html',
                               name=name, title=title, users=users)
    else:
        return redirect(url_for('index'))

@app.route('/line_post', methods=['GET', 'POST'])
def line_post():
    url = "https://notify-api.line.me/api/notify"
    token = "a6C0ofjqzEp40YiKnJuaZY4fpSRUTA9eHixZIm75tLL"
    headers = {"Authorization" : "Bearer "+ token}
    message = ""
    coffee_num = {}
    for i in range(db.session.query(User).count()):
        coffee_num[i+1] = db.session.query(Coffee_Count).filter_by(user_id=i+1).count()
    user = db.session.query(User).filter_by(username=current_user.name).first()
    message += user.__dict__.values()[0] + "さんが飲んどるのは" + str(coffee_num[user.id]) + "杯やで"

    payload = {"message" :  message}
    r = requests.post(url ,headers = headers ,params=payload)
    return redirect('/')


# add_user メソッドを追加し、ユーザ登録に関する処理を行う
@app.route("/add_user", methods=['POST','GET'])
def add_user():
    # フォームから渡ってきた username を取得
    username = request.form.get('username')
    password = request.form.get('password')
    twitter = request.form.get('twitter')

    if username:
        # 前回、手動で対応した処理と同じ
        user = User(username,password,twitter)
        db.session.add(user)
        db.session.commit()
    else:
        return render_template('add_user.html')
    # ユーザ登録後は、元ページへリダイレクト
    return redirect(url_for('index'))

@app.route('/increment',methods=['POST'])
def increment():
    if request.method == 'POST':
        cofee_name = request.form["form1"]
        user = db.session.query(User).filter_by(username=cofee_name).first()
        timestamp = datetime.now()
        coffee = Coffee_Count(user.id, timestamp, False)
        db.session.add(coffee)
        db.session.commit()
        coffee_num = {}
        check = {}
        for i in range(db.session.query(User).count()):
            coffee_num[i+1] = db.session.query(Coffee_Count).filter_by(user_id=i+1).count()
            check[i+1] = db.session.query(Coffee_Count).filter_by(user_id=i+1, check=False).count()
        print(coffee_num)
        users = User.query.all()
        return render_template('index.html',  users=users, coffee_num=coffee_num, check=check)

@app.route('/decrement',methods=['POST'])
def decrement():
    if request.method == 'POST':
        cofee_name = request.form["form3"]
        user = db.session.query(User).filter_by(username=cofee_name).first()
        record = db.session.query(Coffee_Count).filter_by(user_id=user.id).order_by( " id desc " ).first()
        db.session.delete(record)
        db.session.commit()
        coffee_num = {}
        check = {}
        for i in range(db.session.query(User).count()):
            coffee_num[i+1] = db.session.query(Coffee_Count).filter_by(user_id=i+1).count()
            check[i+1] = db.session.query(Coffee_Count).filter_by(user_id=i+1, check=False).count()
        print(coffee_num)
        users = User.query.all()
        return render_template('index.html',  users=users, coffee_num=coffee_num, check=check)

@app.route('/delete',methods=['POST'])
def delete():
    if request.method == 'POST':
        cofee_name = request.form["form2"]
        user = db.session.query(User).filter_by(username=cofee_name).first()
        db.session.delete(user)
        db.session.commit()
        users = User.query.all()
        return render_template('index.html',  users=users)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        loguser = db.session.query(User).filter_by(username=username).first()
        try:
            if password == loguser.password:
                user = Login_User(loguser.id)
                login_user(user)
                return redirect('/')
            else:
                return abort(401)
        except:
            return redirect('/')
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        <a href="/add_user">ユーザー登録</a>
        ''')


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    print(current_user)
    return redirect('/login')
# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return redirect('http://yahoo.co.jp')

# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return Login_User(userid)
# Start application
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=2000)
