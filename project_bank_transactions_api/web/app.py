from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)
client = MongoClient("mongodb://db:27017")
db = client.BankAPI
users = db["users"]

"""
Create some helper functions for later coding
"""


def user_exists(username):
    if users.find({"username": username}).count() == 0:
        return False
    else:
        return True


def set_status_code(status, msg):
    return jsonify({
        'status': status,
        'msg': msg
    })


def verify_password(username, password):
    if not user_exists(username):
        return False
    hashed_pw = users.find({"username": username})[0]["password"]
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False


def cash_with_user(username):
    return users.find({"username": username})[0]["own_money"]


def debt_with_user(username):
    return users.find({"username": username})[0]["debt_money"]


def verify_credentials(username, password):
    if not user_exists(username):
        return set_status_code(301, "Invalid username"), True

    correct_pw = verify_password(username, password)

    if not correct_pw:
        return set_status_code(302, "Invalid password"), False

    return None, False


def update_account(username, balance):
    users.update({
        "username": username
    }, {
        "$set": {
            "own_money": balance
        }
    })


def update_debt(username, balance):
    users.update({
        "username": username
    }, {
        "$set": {
            "debt_money": balance
        }
    })


class Register(Resource):
    def post(self):
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]

        if user_exists(username):
            return set_status_code(301, "Invalid username")

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({
            "username": username,
            "password": hashed_pw,
            "own_money": 0,
            "debt_money": 0
        })

        return set_status_code(200, "Successful signed up for the API")


class Add(Resource):
    def post(self):
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]
        money = posted_data["amount"]

        ret_json, error = verify_credentials(username, password)

        if error:
            return ret_json

        if money <= 0:
            return set_status_code(304, "Money amount must be >0")

        cash = cash_with_user(username)
        money -= 1
        bank_cash = cash_with_user("BANK")
        update_account(username, cash+money)
        update_account("BANK", bank_cash+1)

        return set_status_code(200, "Cash successfully added to account.")


class Transfer(Resource):
    def post(self):
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]
        reciever = posted_data["reciever"]
        money = posted_data["amount"]

        ret_json, error = verify_credentials(username, password)
        if error:
            return ret_json

        cash = cash_with_user(username)
        if cash <= 0:
            return set_status_code(304, "Out of money")

        if not user_exists(reciever):
            return set_status_code(301, "Invalid reciever username")

        cash_from = cash_with_user(username)
        cash_to = cash_with_user(reciever)
        bank_cash = cash_with_user("BANK")

        update_account("BANK", bank_cash + 1)
        update_account(reciever, cash_to + money - 1)
        update_account(username, cash_from - money)

        return set_status_code(200, "Amount successfully transfered")


class Balance(Resource):
    def post(self):
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]

        ret_json, error = verify_credentials(username, password)
        if error:
            return ret_json

        return jsonify({
            "username": username
        }, {
            "_id": 0,
            "password": 0,

        })[0]


class TakeLoan(Resource):
    def post(self):
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]
        money = posted_data["amount"]

        ret_json, error = verify_credentials(username, password)
        if error:
            return ret_json

        cash = cash_with_user(username)
        debt = debt_with_user(username)

        update_account(username, cash + money)
        update_account(username, debt + money)

        return set_status_code(200, "Loan added successful to account")


class PayLoan(Resource):
    def post(self):
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]
        money = posted_data["amount"]

        ret_json, error = verify_credentials(username, password)
        if error:
            return ret_json

        cash = cash_with_user(username)
        if cash <= 0:
            return set_status_code(303, "Not enough money")

        debt = debt_with_user(username)

        update_account(username, cash - money)
        update_account(username, debt - money)

        return set_status_code(200, "Loan successful paid")


api.add_resource(Resource, "/register")
api.add_resource(Add, "/add")
api.add_resource(Transfer, "/transfer")
api.add_resource(Balance, "/balance")
api.add_resource(TakeLoan, "/takeloan")
api.add_resource(PayLoan, "/payloan")


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
