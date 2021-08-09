#!/usr/bin/env python3

from flask import Flask, render_template, redirect, request, session
from flaskext.mysql import MySQL
from hashlib import scrypt
import base64
import locale

locale.setlocale(locale.LC_ALL, '')

app = Flask(__name__)
mysql = MySQL()

# used for session
app.secret_key = b"secret"

app.config["MYSQL_DATABASE_USER"] = "admin"
app.config["MYSQL_DATABASE_PASSWORD"] = "ezezez"
app.config["MYSQL_DATABASE_DB"] = "bank"
app.config["MYSQL_DATABASE_HOST"] = "localhost"

mysql.init_app(app)
connection = mysql.connect()
connection.autocommit(True)
cursor = connection.cursor()

login_stmt = """SELECT `id`, `username`, `password`, `salt` FROM `bank_users`
WHERE `username` = %s"""

balance_stmt = "SELECT `balance` FROM `bank_users` WHERE `id` = %s"

def format_currency(amount):
    return locale.currency(amount, grouping=True)

def get_balance(id):
    balance = 0

    res = cursor.execute(balance_stmt, id)
    res = cursor.fetchone()

    if res:
        balance = res[0]

    balance = format_currency(balance)

    return balance

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login", 302)

    activity = []

    balance = get_balance(session["user"]["id"])

    return render_template(
        "home.html",
        page="Home",
        user=session["user"],
        balance=balance,
        activity=activity
    )

@app.route("/login", methods = ["POST", "GET"])
def login():
    message = None

    if request.method == 'POST':
        cursor.execute(login_stmt, request.form['username'])
        res = cursor.fetchone()

        if not res:
            message = "Invalid username or password."
        else:
            id, username, hashed, salt = res
            hashed = base64.b64decode(hashed)
            salt = base64.b64decode(salt)
            password = bytes(request.form['password'], 'utf8')

            if hashed == scrypt(password, salt=salt, n=2, r=1, p=1):
                session['user'] = {
                    "id": id,
                    "username": username
                }

                return redirect("/", 302)
            else:
                message = "Invalid username or password."

    return render_template("login.html", page="Login", message=message)

@app.route("/withdraw")
def withdraw():
    if "user" not in session:
        return redirect("/login", 302)

    return render_template("withdraw.html", page="Withdraw")

@app.route("/deposit")
def deposit():
    if "user" not in session:
        return redirect("/login", 302)

    return render_template("deposit.html", page="Deposit")

@app.route("/transfer")
def transfer():
    if "user" not in session:
        return redirect("/login", 302)

    return render_template("transfer.html", page="Transfer")
