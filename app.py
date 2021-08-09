#!/usr/bin/env python3

from flask import Flask, render_template, redirect, request, session
from flask_wtf.csrf import CSRFProtect
from flaskext.mysql import MySQL
from hashlib import scrypt
import base64
import locale
import os
import time

# used to determine the type of log
WITHDRAW = 0
DEPOSIT = 1
TRANSFER = 2

locale.setlocale(locale.LC_ALL, "")

app = Flask(__name__)

# https://owasp.org/www-community/attacks/csrf
csrf = CSRFProtect(app)

# used for session
app.secret_key = b"secret"

mysql = MySQL()

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

transfers_get_stmt = """SELECT `bank_transfers`.*, `bank_users`.`username` AS
`to_username` FROM
`bank_transfers` LEFT JOIN `bank_users` ON `bank_users`.`id` =
`bank_transfers`.`to_user_id` WHERE `user_id` = %s ORDER BY `date` DESC"""

withdraw_user_stmt = """UPDATE `bank_users` SET `balance` = `balance` - %s
WHERE `id` = %s"""

deposit_user_stmt = """UPDATE `bank_users` SET `balance` = `balance` + %s
WHERE `id` = %s """

transfers_add_stmt = """INSERT INTO `bank_transfers` (`user_id`,
`amount`, `balance`, `to_user_id`, `reason`, `type`, `date`) VALUES
(%s, %s, %s, %s, %s, %s, %s)"""

# use this to create new passwords
def hash_password(plain):
    salt = os.urandom(64)
    hashed = scrypt(password, salt=salt, n=2, r=1, p=1)

    return (salt, hashed)

def format_currency(amount):
    return locale.currency(amount, grouping=True)

def format_date(epoch):
    return time.strftime("%b %d, %Y %H:%M", time.localtime(epoch))

def format_type(type):
    if type == WITHDRAW:
        return "Withdraw"

    if type == DEPOSIT:
        return "Deposit"

    if type == TRANSFER:
        return "Transfer"

def get_balance(id):
    balance = 0

    res = cursor.execute(balance_stmt, id)
    res = cursor.fetchone()

    if res:
        balance = res[0]

    return balance

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login", 302)

    activities = []

    res = cursor.execute(transfers_get_stmt, session["user"]["id"])
    res = cursor.fetchall()

    for row in res:
        type = format_type(row[6])
        amount = format_currency(row[2])

        if row[6] == WITHDRAW:
            amount = "-" + amount

        activities.append({
            "type": type,
            "amount": amount,
            "balance": format_currency(row[3]),
            "date": format_date(row[7])
        })

    balance = format_currency(get_balance(session["user"]["id"]))

    return render_template(
        "home.html",
        page="Home",
        user=session["user"],
        balance=balance,
        activities=activities
    )

@app.route("/login", methods=["POST", "GET"])
def login():
    if "user" in session:
        return redirect("/", 302)

    message = None

    if request.method == "POST":
        cursor.execute(login_stmt, request.form["username"])
        res = cursor.fetchone()

        if not res:
            message = "Invalid username or password."
        else:
            id, username, hashed, salt = res
            hashed = base64.b64decode(hashed)
            salt = base64.b64decode(salt)
            password = bytes(request.form["password"], "utf8")

            if hashed == scrypt(password, salt=salt, n=2, r=1, p=1):
                session["user"] = {
                    "id": id,
                    "username": username
                }

                return redirect("/", 302)
            else:
                message = "Invalid username or password."

    return render_template("login.html", page="Login", message=message)

@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user", default=None)

    return redirect("/", 302)

@app.route("/withdraw", methods=["POST", "GET"])
def withdraw():
    if "user" not in session:
        return redirect("/login", 302)

    message = None
    message_type = "danger"
    balance = get_balance(session["user"]["id"])

    if request.method == "POST":
        withdraw_req = float(request.form["amount"])

        if (withdraw_req > balance):
            message = "You don't have that much money!"
        else:
            balance = withdraw_req

            cursor.execute(
                withdraw_user_stmt,
                (
                    withdraw_req,
                    session["user"]["id"]
                )
            )

            cursor.execute(
                transfers_add_stmt,
                (
                    session["user"]["id"],
                    withdraw_req,
                    balance,
                    None,
                    None,
                    WITHDRAW,
                    int(time.time())
                )
            )

            message_type = "success"

            message = (
                "Successfully withdrew " + format_currency(withdraw_req) + "."
            )

    return render_template(
        "withdraw.html",
        page="Withdraw",
        balance=balance,
        balance_formatted=format_currency(balance),
        user=session["user"],
        message_type=message_type,
        message=message
    )

@app.route("/deposit", methods=["POST", "GET"])
def deposit():
    if "user" not in session:
        return redirect("/login", 302)

    message = None
    balance = get_balance(session["user"]["id"])

    if request.method == "POST":
        deposit_req = float(request.form["amount"])
        balance += deposit_req

        cursor.execute(deposit_user_stmt,
            (
                deposit_req,
                session["user"]["id"]
            )
        )

        cursor.execute(
            transfers_add_stmt,
            (
                session["user"]["id"],
                deposit_req,
                balance,
                None,
                None,
                DEPOSIT,
                int(time.time())
            )
        )

        message = (
            "Successfully deposited " + format_currency(deposit_req) + "."
        )

    return render_template(
        "deposit.html",
        page="Deposit",
        balance=balance,
        balance_formatted=format_currency(balance),
        user=session["user"],
        message=message
    )

@app.route("/transfer")
def transfer():
    if "user" not in session:
        return redirect("/login", 302)

    balance = get_balance(session["user"]["id"])

    return render_template(
        "transfer.html",
        page="Transfer",
        balance=balance,
        balance_formatted=format_currency(balance),
        user=session["user"]
    )
