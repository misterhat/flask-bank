#!/usr/bin/env python3

from flask import Flask, render_template, redirect
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'ezezez'
app.config['MYSQL_DATABASE_DB'] = 'bank'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

@app.route("/")
def home():
    if True:
        return redirect('/login', 302)
    else:
        return render_template("home.html", page='Home')

@app.route("/login")
def login():
    return render_template("login.html", page="Login")
