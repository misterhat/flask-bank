#!/usr/bin/env python3

from datetime import timedelta
from flask import Flask, render_template, redirect, request, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_wtf.csrf import CSRFProtect
from flaskext.mysql import MySQL
from hashlib import scrypt
import base64
import locale
import math
import os
import time
import timeago

# used to determine the type of log
WITHDRAW = 0
DEPOSIT = 1
TRANSFER = 2

LOGIN = 0
LOGOUT = 1

# amount of transactions to display per page on activities
PER_PAGE = 5

# minutes to allow the user to stay logged in
LOGOUT_TIMEOUT = 2

locale.setlocale(locale.LC_ALL, "")

app = Flask(__name__)

# https://owasp.org/www-community/attacks/csrf
csrf = CSRFProtect(app)

mysql = MySQL()

app.config["MYSQL_DATABASE_USER"] = "admin"
app.config["MYSQL_DATABASE_PASSWORD"] = "ezezez"
app.config["MYSQL_DATABASE_DB"] = "bank"
app.config["MYSQL_DATABASE_HOST"] = "localhost"

# https://blog.paradoxis.nl/defeating-flasks-session-management-65706ba9d3ce
# change this in production:
app.config["SECRET_KEY"] = b"secret"

#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=LOGOUT_TIMEOUT)

mysql.init_app(app)
connection = mysql.connect()
connection.autocommit(True)
cursor = connection.cursor()

socketio = SocketIO(app)

login_stmt = """
SELECT `id`, `username`, `password`, `salt` FROM `bank_users`
WHERE `username` = %s
"""

balance_stmt = "SELECT `balance` FROM `bank_users` WHERE `id` = %s"

transfers_count_stmt = """
SELECT COUNT(1) FROM `bank_transfers` WHERE
`user_id` = %s OR `to_user_id` = %s
"""

transfers_get_stmt = """
SELECT `bank_transfers`.*, `to_users`.`username`, `from_users`.`username`
FROM `bank_transfers`
LEFT JOIN `bank_users` AS `to_users` ON
`to_users`.`id` = `bank_transfers`.`to_user_id`
LEFT JOIN `bank_users` AS `from_users` ON
`from_users`.`id` = `bank_transfers`.`user_id`
WHERE `user_id` = %s OR `to_user_id` = %s
ORDER BY `date` DESC LIMIT %s,%s
"""

withdraw_stmt = """
UPDATE `bank_users` SET `balance` = `balance` - %s
WHERE `id` = %s
"""

deposit_stmt = """
UPDATE `bank_users` SET `balance` = `balance` + %s
WHERE `id` = %s
"""

user_id_stmt = "SELECT `id` FROM `bank_users` WHERE `username` = %s"

transfers_add_stmt = """
INSERT INTO `bank_transfers` (`user_id`,
`amount`, `balance`, `to_balance`, `to_user_id`, `reason`, `type`, `date`)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

activity_update_stmt = """
UPDATE `bank_users` SET `last_activity` = %s WHERE `id` = %s
"""

log_stmt = """
INSERT INTO `bank_log` (`user_id`, `type`, `date`) VALUES (%s, %s, %s)
"""

signed_in_stmt = """
SELECT `username`, `last_activity` FROM `bank_users`
WHERE `last_activity` > %s
"""

signed_out_stmt = """
SELECT `id` FROM `bank_users`
WHERE `last_activity` < %s AND `last_activity` > 0
"""

group_ids_stmt = """
SELECT `g`.`id` FROM `bank_chat_group_users` AS `gu`
JOIN `bank_chat_groups` AS `g` ON `gu`.`group_id` = `g`.`id`
WHERE `gu`.`user_id` = %s
"""

group_users_stmt = """
SELECT `u`.`username`
FROM `bank_chat_group_users` AS `gu`
JOIN `bank_users` AS `u` ON `u`.`id` = `gu`.`user_id`
WHERE `group_id` = %s AND `user_id` != %s
"""

group_messages_stmt = """
SELECT `bank_users`.`username`, `message`, `date`
FROM `bank_chat_messages`
LEFT JOIN `bank_users` ON `bank_users`.`id` = `bank_chat_messages`.`user_id`
WHERE `group_id` = %s
"""

add_message_stmt = """
INSERT INTO `bank_chat_messages` (`group_id`, `user_id`, `message`, `date`)
VALUES (%s, %s, %s, %s)
"""

add_group_stmt = "INSERT INTO `bank_chat_groups` (`date`) VALUES (%s)"

add_group_user_stmt = """
INSERT INTO `bank_chat_group_users` (`group_id`, `user_id`, `is_owner`)
VALUES (%s, %s, %s)
"""

leave_group_user_stmt = """
DELETE FROM `bank_chat_group_users` WHERE `group_id` = %s AND `user_id` = %s
"""

count_group_user_stmt = """
SELECT `user_id` FROM `bank_chat_group_users` WHERE `group_id` = %s LIMIT 2
"""

delete_group_stmt = "DELETE FROM `bank_chat_groups` WHERE `id` = %s"

delete_messages_stmt = "DELETE FROM `bank_chat_messages` WHERE `group_id` = %s"

update_read_stmt = """
UPDATE `bank_chat_group_users`
SET `last_message_read` = %s
WHERE `user_id` = %s AND `group_id` = %s
"""

inc_read_stmt = """
UPDATE `bank_chat_group_users`
SET `last_message_read` = `last_message_read` + 1
WHERE `user_id` = %s AND `group_id` = %s
"""

total_msg_stmt = """
SELECT COUNT(1) FROM `bank_chat_messages` WHERE `group_id` = %s
"""

unread_msg_stmt = """
SELECT (""" + total_msg_stmt + """) - `last_message_read`
FROM `bank_chat_group_users`
WHERE `group_id` = %s AND `user_id` = %s
"""

is_owner_stmt = """
SELECT `is_owner` FROM `bank_chat_group_users`
WHERE `user_id` = %s AND `group_id` = %s
"""

last_global_update = 0

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

def format_date(secs):
    return time.strftime("%b %d, %Y %H:%M", time.localtime(secs))

def format_type(type):
    if type == WITHDRAW:
        return "Withdraw"

    if type == DEPOSIT:
        return "Deposit"

    if type == TRANSFER:
        return "Transfer"

def get_balance(user_id):
    balance = 0

    cursor.execute(balance_stmt, user_id)
    res = cursor.fetchone()

    if res:
        balance = res[0]

    return balance

def get_group_ids(user_id):
    cursor.execute(group_ids_stmt, user_id)
    res = cursor.fetchall()
    ids = []

    for row in res:
        ids.append(row[0])

    return ids

def get_group_users(group_id, user_id):
    cursor.execute(group_users_stmt, (group_id, user_id))
    res = cursor.fetchall()
    users = []

    for row in res:
        users.append(row[0])

    return users

def get_group_messages(group_id):
    cursor.execute(group_messages_stmt, group_id)
    res = cursor.fetchall()
    messages = []

    for row in res:
        messages.append({
            "user": row[0],
            "message": row[1],
            "date": row[2]
        })

    return messages

@app.before_request
def before_request():
    global last_global_update

    now = int(time.time())

    # sync the database in case users log in and don't load any more pages
    if now - last_global_update > (LOGOUT_TIMEOUT / 2) * 60:
        cursor.execute(signed_out_stmt, now - (LOGOUT_TIMEOUT * 60))

        for row in cursor.fetchall():
            user_id = row[0]
            cursor.execute(log_stmt, (user_id, LOGOUT, now))
            cursor.execute(activity_update_stmt, (0, user_id))

        last_global_update = now

    if "user" in session:
        user_id = session["user"]["id"]
        last_activity = session["user"]["last_activity"]

        if now - last_activity > LOGOUT_TIMEOUT * 60:
            cursor.execute(log_stmt, (user_id, LOGOUT, now))
            cursor.execute(activity_update_stmt, (0, user_id))
            session.pop("user", default=None)
        else:
            cursor.execute(activity_update_stmt, (now, user_id))
            session["user"]["last_activity"] = now

@app.route("/signed-in")
def signed_in():
    if "user" in session:
        cursor.execute(signed_in_stmt, int(time.time()) - LOGOUT_TIMEOUT * 60)
        signed_in_users = []

        for row in cursor.fetchall():
            last_activity = row[1]

            if int(time.time()) - last_activity <= 60:
                last_activity = "less than a minute ago"
            else:
                last_activity = timeago.format(row[1])

            signed_in_users.append({
                "username": row[0],
                "last_activity": last_activity
            })

        return render_template(
            "signed-in.html",
            signed_in_users=signed_in_users
        )
    else:
        return render_template(
            "signed-in.html",
            signed_in_users=[]
        )

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login", 302)

    user_id = session["user"]["id"]
    activities = []

    cursor.execute(transfers_count_stmt, (user_id, user_id))
    count = cursor.fetchone()[0]

    total_pages = math.ceil(count / PER_PAGE)

    page = int(request.args.get("page") or 1) - 1

    if page < 0 or (total_pages > 1 and page >= total_pages):
        return redirect("/", 302)

    offset = page * PER_PAGE

    cursor.execute(transfers_get_stmt, (user_id, user_id, offset, PER_PAGE))
    res = cursor.fetchall()

    for row in res:
        type = format_type(row[7])
        amount = format_currency(row[2])
        to_user_id = row[5]
        reason = row[6]
        transfer_from_us = row[7] == TRANSFER and to_user_id != user_id
        transfer_to_us = row[7] == TRANSFER and to_user_id == user_id
        balance = format_currency(row[3])

        if row[7] == TRANSFER and not reason:
            reason = "empty reason"

        if transfer_from_us:
            to_username = row[9]
            type = type + " to " + to_username + " (" + reason + ")"
        elif transfer_to_us:
            balance = format_currency(row[4])
            from_username = row[10]
            type = type + " from " + from_username + " (" + reason + ")"

        if row[7] == WITHDRAW or transfer_from_us:
            amount = "-" + amount

        activities.append({
            "type": type,
            "amount": amount,
            "balance": balance,
            "date": format_date(row[8])
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
                cursor.execute(log_stmt, (id, LOGIN, int(time.time())))

                session["user"] = {
                    "id": id,
                    "username": username,
                    "last_activity": int(time.time())
                }

                session.permanent = True

                return redirect("/", 302)
            else:
                message = "Invalid username or password."

    return render_template("login.html", page="Login", message=message)

@app.route("/logout")
def logout():
    if "user" in session:
        user_id = session["user"]["id"]
        cursor.execute(log_stmt, (user_id, LOGOUT, int(time.time())))
        cursor.execute(activity_update_stmt, (0, user_id))
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
                    to_balance = get_balance(to_user_id)
                    to_balance += transfer_req

                    cursor.execute(withdraw_stmt, (transfer_req, user_id))
                    cursor.execute(deposit_stmt, (transfer_req, to_user_id))

                    cursor.execute(
                        transfers_add_stmt,
                        (
                            user_id,
                            transfer_req,
                            balance,
                            to_balance,
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

@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect("/login", 302)

    return render_template(
        "chat.html",
        page="Chat",
        user=session["user"]
    )

@socketio.on('connect')
def on_connect():
    if "user" not in session:
        return

    for group_id in get_group_ids(session["user"]["id"]):
        join_room("group-" + str(group_id))

def emit_chat_groups(session):
    user_id = session["user"]["id"]
    chat_groups = []

    for group_id in get_group_ids(user_id):
        cursor.execute(unread_msg_stmt, (group_id, group_id, user_id))
        unread = cursor.fetchone()[0]

        join_room("group-" + str(group_id))

        chat_groups.append({
            "id": group_id,
            "users": get_group_users(group_id, user_id),
            "unread": unread
        })

    emit("chat-groups", chat_groups)

@socketio.on('get-chat-groups')
def on_get_chat_groups(json):
    if "user" not in session:
        return

    emit_chat_groups(session)

@socketio.on('get-chat-messages')
def on_get_chat_messages(json):
    if "user" not in session:
        return

    user_id = session["user"]["id"]
    group_id = json["group_id"]

    cursor.execute(total_msg_stmt, group_id)
    total_msgs = cursor.fetchone()[0]

    cursor.execute(update_read_stmt, (total_msgs, user_id, group_id))

    emit("chat-messages", get_group_messages(group_id))

@socketio.on('send-message')
def on_send_chat_messages(json):
    if "user" not in session:
        return

    group_id = json["group_id"]
    user_id = session["user"]["id"]

    # trying to send message to a group they aren't in
    if group_id not in get_group_ids(user_id):
        return

    message = json["message"].strip()
    now = int(time.time())

    cursor.execute(
        add_message_stmt,
        (group_id, user_id, message, now)
    )

    emit(
        "chat-message",
        {
            "group_id": group_id,
            "user": session["user"]["username"],
            "message": message,
            "date": now
        },
        to="group-" + str(group_id)
    )

@socketio.on('create-group')
def on_create_group(json):
    if "user" not in session:
        return

    message = None

    username = json["username"].strip()

    cursor.execute(user_id_stmt, username)
    res = cursor.fetchone()

    if not res:
        emit("error-message", "User '" + username + "' does not exist.")
        return

    user_id = session["user"]["id"]
    other_user_id = res[0]

    if other_user_id == user_id:
        emit("error-message", "Cannot start a conversation with yourself.")
        return

    now = int(time.time())

    cursor.execute(add_group_stmt, now)
    cursor.execute("SELECT LAST_INSERT_ID();")
    group_id = cursor.fetchone()[0]

    cursor.execute(add_group_user_stmt, (group_id, user_id, 1))
    cursor.execute(add_group_user_stmt, (group_id, other_user_id, 0))

    cursor.execute(
        add_message_stmt,
        (group_id, None, "Created new conversation.", now)
    )

    join_room("group-" + str(group_id))
    emit("redirect", "/chat#group-" + str(group_id))
    emit("refresh-chat-groups", other_user_id, broadcast=True)

@socketio.on('leave-group')
def on_leave_group(json):
    if "user" not in session:
        return

    group_id = json["group_id"]
    user_id = session["user"]["id"]

    if group_id not in get_group_ids(user_id):
        return

    leave_room("group-" + str(group_id))

    cursor.execute(leave_group_user_stmt, (group_id, user_id))

    cursor.execute(count_group_user_stmt, (group_id))
    res = cursor.fetchall()

    if len(res) == 1:
        other_user_id = res[0][0]
        cursor.execute(leave_group_user_stmt, (group_id, other_user_id))
        cursor.execute(delete_group_stmt, group_id)
        cursor.execute(delete_messages_stmt, group_id)
    else:
        username = session["user"]["username"]
        message = username + " has left the room."
        now = int(time.time())

        cursor.execute(
            add_message_stmt,
            (group_id, None, message, now)
        )

        emit(
            "chat-message",
            {
                "group_id": group_id,
                "user": None,
                "message": message,
                "date": now
            },
            to="group-" + str(group_id)
        )

    emit("redirect", "/chat")
    emit("refresh-chat-groups", broadcast=True)

@socketio.on('invite-group')
def on_invite_group(json):
    if "user" not in session:
        return

    group_id = json["group_id"]
    user_id = session["user"]["id"]

    if group_id not in get_group_ids(user_id):
        return

    username = json["username"].strip()

    cursor.execute(user_id_stmt, username)
    res = cursor.fetchone()

    if not res:
        emit("error-message", "User '" + username + "' does not exist.")
        return

    other_user_id = res[0]

    if other_user_id == user_id:
        emit("error-message", "Cannot invite yourself to a room.")
        return

    cursor.execute(add_group_user_stmt, (group_id, other_user_id, 0))

    message = "Added " + username + " to the room."
    now = int(time.time())

    cursor.execute(
        add_message_stmt,
        (group_id, None, message, now)
    )

    emit(
        "chat-message",
        {
            "group_id": group_id,
            "user": None,
            "message": message,
            "date": now
        },
        to="group-" + str(group_id)
    )

    emit("refresh-chat-groups", to="group-" + str(group_id))
    emit("refresh-chat-groups", other_user_id, broadcast=True)

@socketio.on('get-total-unread')
def on_total_unread(json):
    if "user" not in session:
        return

    user_id = session["user"]["id"]
    total_unread = 0

    for group_id in get_group_ids(user_id):
        cursor.execute(unread_msg_stmt, (group_id, group_id, user_id))
        total_unread += cursor.fetchone()[0]

    emit('total-unread', total_unread)

@socketio.on('inc-unread')
def on_inc_read(json):
    if "user" not in session:
        return

    group_id = json["group_id"]
    user_id = session["user"]["id"]

    if group_id not in get_group_ids(user_id):
        return

    cursor.execute(inc_read_stmt, (user_id, group_id))

@socketio.on('kick-group')
def on_kick_group(json):
    if "user" not in session:
        return

    user_id = session["user"]["id"]
    group_id = json["group_id"]

    cursor.execute(is_owner_stmt, (user_id, group_id))
    is_owner = cursor.fetchone()[0]

    if is_owner == 0:
        emit("error-message", "You are not the owner of this chatroom.")
        return

    users = get_group_users(group_id, user_id)

    if len(users) == 1:
        emit(
            "error-message",
            "Only two users left - leave the room instead."
        )
        return

    username = json["user"]

    if username not in users:
        return

    cursor.execute(user_id_stmt, username)
    res = cursor.fetchone()

    other_user_id = res[0]
    cursor.execute(leave_group_user_stmt, (group_id, other_user_id))

    message = username + " has been kicked."
    now = int(time.time())

    cursor.execute(
        add_message_stmt,
        (group_id, None, message, now)
    )

    emit(
        "chat-message",
        {
            "group_id": group_id,
            "user": None,
            "message": message,
            "date": now
        },
        to="group-" + str(group_id)
    )

    emit("refresh-chat-groups", broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
