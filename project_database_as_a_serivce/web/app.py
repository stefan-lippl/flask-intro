"""
export FLASK_APP=app.py
1. Registration of user (costs 0 tokens)
2. Store a sentence in the db for 1 token (each user has 10 tokens)
3. Retriev his sentence for 1 token
"""
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)
client = MongoClient("mongodb://db:27017")
db = client.sentences_database
users = db["users"]

def verify_password(username, password):
    hashed_pw = users.find({
        "username": username
    })[0]['password']

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def count_tokens(username):
    tokens = users.find({
        "username": username
    })[0]['tokens']
    return tokens

class Register(Resource):
    def post(self):
        # Step 1: Get posted data by the user
        posted_data = request.get_json()

        # Step 2: Extract the data
        username = posted_data["username"]
        password = posted_data["password"]

        # Step 3: Hash the password with the lib bcrypt to store it
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        # Step 4: Store username and hashed_pw into database
        users.insert({
            "username": username,
            "password": hashed_pw,
            "sentence": "",
            "tokens": 10
        })

        # Step 5: Return msg to user
        ret_json = {
            "status": 200,
            "msg": "Successful signed up to the API."
        }
        return jsonify(ret_json)

class Store(Resource):
    def post(self):
        # Step 1: Get posted data by the user
        posted_data = request.get_json()

        # Step 2: Extract the data
        username = posted_data["username"]
        password = posted_data["password"]
        sentence = posted_data["sentence"]

        # Step 3: Verfiy username & password match
        correct_pw = verify_password(username, password)

        if not correct_pw:
            ret_json = {
                "status": 302
            }
            return jsonify(ret_json)

        # Step 4: Check users amount of tokens
        num_tokens = count_tokens(username)

        if num_tokens <= 0:
            ret_json = {
                "status": 301
            }
            return jsonify(ret_json)

        # Step 5: Update the db
        users.update({
            "username": username,
        }, {
            "$set": {
                "sentence": sentence,
                "tokens": num_tokens-1
                }
        })

        ret_json = {
            "status": 200,
            "msg": "Sentence saved successful"
        }
        return jsonify(ret_json)

class Get(Resource):
    def post(self):
        # Step 1: Get posted data by the user
        posted_data = request.get_json()

        # Step 2: Extract the data
        username = posted_data["username"]
        password = posted_data["password"]

        # Step 3: Verfiy username & password match
        correct_pw = verify_password(username, password)

        if not correct_pw:
            ret_json = {
                "status": 302
            }
            return jsonify(ret_json)

        # Step 4: Check users amount of tokens
        num_tokens = count_tokens(username)

        if num_tokens <= 0:
            ret_json = {
                "status": 301
            }
            return jsonify(ret_json)

        # Step 5: Charge the user one token
        users.update({
            "username": username,
        }, {
            "$set": {
                "tokens": num_tokens-1
                }
        })

        sentence = users.find({
            "username": username
        })[0]["sentence"]

        ret_json = {
            "status": 200,
            "sentence": sentence
        }
        return jsonify(ret_json)

api.add_resource(Register, "/register")
api.add_resource(Store, "/store")
api.add_resource(Get, "/get")

if __name__ == "__main__":
    app.run(host='0.0.0.0')
