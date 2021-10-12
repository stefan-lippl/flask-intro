from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SimilarityDB
users = db["Users"]

def user_exists(username):
    if users.find({"username": username}).count() == 0:
        return False
    else:
        return True

class Register(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]

        if user_exists(username):
            return jsonify({
                "status": 301,
                "msg": "Invalid username - username already exists"
            })

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({
            "username": username,
            "password": hashed_pw,
            "tokens": 6
        })

        return jsonify({
            "status": 200,
            "msg": "Successful signed up for the API"
        })

def verify_password(username, password):
    if not user_exists(username):
        return False

    hashed_pw = users.find({
        "username": username
    })[0]["password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def count_tokens(username):
    tokens = users.find({
        "username": username
    })[0]["tokens"]
    return tokens


class Detect(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        text1 = posted_data["text1"]
        text2 = posted_data["text2"]

        if not user_exists(username):
            return jsonify({
                "status": 301,
                "msg": "User not exists"
            })

        correct_pw = verify_password(username, password)
        if not correct_pw:
            return jsonify({
                "status": 302,
                "msg": "Incorrect password. Try again."
            })

        num_tokens = count_tokens(username)
        if num_tokens <= 0:
            return jsonify({
                "status": 303,
                "msg": "Out of tokens. Refill tokens to use API again."
            })

        # Claculate Similarity
        # https://github.com/explosion/spacy-models/releases?q=en_core
        nlp = spacy.load('en_core_web_sm')

        text1 = nlp(text1)
        text2 = nlp(text2)

        ratio = text1.similarity(text2)

        curr_tokens = count_tokens(username)
        users.update({
                "username": username
            }, {
                "$set": {
                    "tokens" : curr_tokens-1
                }
            })

        return jsonify({
            "status": 200,
            "similarity": ratio,
            "msg": "Sim scory successful calculated"
        })


class Refill(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["admin_pw"]
        refill_amount = posted_data["refill"]

        if not user_exists(username):
            return jsonify({
                "status": 301,
                "msg": "User not exists"
            })

        correct_pw = 1234

        if not password == correct_pw:
            return jsonify({
                "status": 304,
                "msg": "Invalid admin password"
            })

        curr_tokens = count_tokens(username)
        users.update({
            "username": username
        }, {
            "$set": {
                "tokens" : curr_tokens + refill_amount
            }
        })

        return jsonify({
            "status": 200,
            "msg": "Refilled successfully"
        })



api.add_resource(Register, "/register")
api.add_resource(Detect, "/detect")
api.add_resource(Refill, "/refill")

if __name__ == "__main__":
    app.run(host = "0.0.0.0")
