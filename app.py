#!/usr/bin/env python3

from flask import Flask, render_template, redirect, request, session
from flask_wtf.csrf import CSRFProtect
from flaskext.mysql import MySQL
from hashlib import scrypt
import base64
import locale
import os
import time
import math

# used to determine the type of log
WITHDRAW = 0
DEPOSIT = 1
TRANSFER = 2

# amount of transactions to display per page on activities
PER_PAGE = 5

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

transfers_count_stmt = """SELECT COUNT(1) FROM `bank_transfers` WHERE
`user_id` = %s OR `to_user_id` = %s"""

transfers_get_stmt = """
SELECT `bank_transfers`.*, `to_users`.`username`, `from_users`.`username`
FROM `bank_transfers`
LEFT JOIN `bank_users` AS `to_users` ON
`to_users`.`id` = `bank_transfers`.`to_user_id`
LEFT JOIN `bank_users` AS `from_users` ON
`from_users`.`id` = `bank_transfers`.`user_id`
WHERE `user_id` = %s OR `to_user_id` = %s
ORDER BY `date` DESC LIMIT %s,%s"""

withdraw_stmt = """UPDATE `bank_users` SET `balance` = `balance` - %s
WHERE `id` = %s"""

deposit_stmt = """UPDATE `bank_users` SET `balance` = `balance` + %s
WHERE `id` = %s"""

user_id_stmt = "SELECT `id` FROM `bank_users` WHERE `username` = %s"

transfers_add_stmt = """INSERT INTO `bank_transfers` (`user_id`,
`amount`, `balance`, `to_user_id`, `reason`, `type`, `date`) VALUES
(%s, %s, %s, %s, %s, %s, %s)"""

# use this to create new passwords
def hash_password(plain):
    salt = os.urandom(64)
    hashed = scrypt(bytes(plain, "utf8"), salt=salt, n=2, r=1, p=1)
    salt = base64.b64encode(salt).decode("utf8")
    hashed = base64.b64encode(hashed).decode("utf8")

    return (salt, hashed)

#print("password 'test':")
#print(hash_password("test"))

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

    user_id = session["user"]["id"]
    activities = []

    cursor.execute(transfers_count_stmt, (user_id, user_id))
    count = cursor.fetchone()[0]

    total_pages = math.ceil(count / PER_PAGE)

    page = int(request.args.get('page') or 1) - 1

    if page < 0 or (total_pages > 1 and page >= total_pages):
        return redirect("/", 302)

    offset = page * PER_PAGE

    cursor.execute(transfers_get_stmt, (user_id, user_id, offset, PER_PAGE))
    res = cursor.fetchall()

    for row in res:
        type = format_type(row[6])
        amount = format_currency(row[2])
        to_user_id = row[4]
        reason = row[5]
        transfer_from_us = row[6] == TRANSFER and to_user_id != user_id
        transfer_to_us = row[6] == TRANSFER and to_user_id == user_id

        if row[6] == TRANSFER and not reason:
            reason = "empty reason"

        if transfer_from_us:
            to_username = row[8]
            type = type + " to " + to_username + " (" + reason + ")"
        elif transfer_to_us:
            from_username = row[9]
            type = type + " from " + from_username + " (" + reason + ")"

        if row[6] == WITHDRAW or transfer_from_us:
            amount = "-" + amount

        activities.append({
            "type": type,
            "amount": amount,
            "balance": format_currency(row[3]),
            "date": format_date(row[7])
        })

    balance = format_currency(get_balance(user_id))

    return render_template(
        "home.html",
        page="Home",
        user=session["user"],
        balance=balance,
        activities=activities,
        total_pages=total_pages,
        current_page=page + 1
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

    user_id = session["user"]["id"]
    message = None
    message_type = "danger"
    balance = get_balance(user_id)

    if request.method == "POST":
        withdraw_req = float(request.form["amount"])

        if (withdraw_req > balance):
            message = "You don't have that much money."
        else:
            balance -= withdraw_req

            cursor.execute(withdraw_stmt, (withdraw_req, user_id))

            cursor.execute(
                transfers_add_stmt,
                (
                    user_id,
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

    user_id = session["user"]["id"]
    message = None
    balance = get_balance(user_id)

    if request.method == "POST":
        deposit_req = float(request.form["amount"])
        balance += deposit_req

        cursor.execute(deposit_stmt, (deposit_req, user_id))

        cursor.execute(
            transfers_add_stmt,
            (
                user_id,
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

@app.route("/transfer", methods=["POST", "GET"])
def transfer():
    if "user" not in session:
        return redirect("/login", 302)

    user_id = session["user"]["id"]
    message = None
    message_type = "danger"
    balance = get_balance(user_id)

    if request.method == "POST":
        user_req = request.form["username"].strip().lower()

        if user_req == session["user"]["username"].lower():
            message = "You cannot transfer money to yourself."
        else:
            transfer_req = float(request.form["amount"])

            if (transfer_req > balance):
                message = "You don't have that much money."
            else:
                cursor.execute(user_id_stmt, request.form["username"])
                res = cursor.fetchone()

                if not res:
                    message = "User '" + user_req + "' does not exist."
                else:
                    balance -= transfer_req

                    to_user_id = res[0]

                    cursor.execute(withdraw_stmt, (transfer_req, user_id))
                    cursor.execute(deposit_stmt, (transfer_req, to_user_id))

                    cursor.execute(
                        transfers_add_stmt,
                        (
                            user_id,
                            transfer_req,
                            balance,
                            to_user_id,
                            request.form["reason"].strip(),
                            TRANSFER,
                            int(time.time())
                        )
                    )

                    message_type = "success"

                    message = (
                        "Successfully transferred " +
                        format_currency(transfer_req) +
                        " to " + user_req + "."
                    )

    return render_template(
        "transfer.html",
        page="Transfer",
        balance=balance,
        balance_formatted=format_currency(balance),
        user=session["user"],
        message_type=message_type,
        message=message
    )
