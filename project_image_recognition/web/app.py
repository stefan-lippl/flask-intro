from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import requests
import subprocess
import json

from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
import requests
import PIL
import cv2


app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.ImageRecognition
users = db["Users"]


def user_exists(username):
    if users.find({"username": username}).count() == 0:
        return False
    else:
        return True

def gen_status(status, msg):
    return jsonify({
        "status": status,
        "msg": msg
    })

class Register(Resource):
    def post(self):
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]

        if user_exists(username):
            return gen_status(301, "Invalid user")


        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({
            "username": username,
            "password": hashed_pw,
            "tokens": 4
        })
        return gen_status(200, "Successful signed up for the API")

def verify_password(username, password):
    if not user_exists(username):
        return False

    hashed_pw = users.find({
        "username": username
    })[0]['password']

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False


def verify_credentials(username, password):
    if not user_exists(username):
        return gen_status(301, "Invalid Username"), True

    correct_pw = verify_password(username, password)
    if not correct_pw:
        return gen_status(302, "Invalid Password"), True

    return None, False


class Classification(Resource):
    def post(self):
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]
        url = posted_data["url"]

        # Check credentials
        ret_json, error = verify_credentials(username, password)
        if error:
            return gen_status(301, "Invalid user.")

        # Check amount tokens
        tokens = users.find({
            "username":username
        })[0]["tokens"]

        if tokens <= 0:
            return gen_status(302, "Not engough tokens. Refill.")


        r = requests.get(url)
        with open("temp.jpg", "wb") as f:
            f.write(r.content)

        img_path = './temp.jpg'

        model = ResNet50(weights='imagenet')

        r = requests.get(url)
        with open("tmp.jpg", "wb") as f:
            f.write(r.content)

        img_path = 'tmp.jpg'
        img = cv2.imread(img_path)
        size = (224,224)
        img = cv2.resize(img, size)
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        preds = model.predict(x)
        # decode the results into a list of tuples (class, description, probability)
        # (one such list for each sample in the batch)
        object = decode_predictions(preds, top=1)[0][0][1]
        acc = int(decode_predictions(preds, top=1)[0][0][2] * 100)

        users.update({
            "username": username
        }, {
            "$set": {
                "tokens": tokens-1
            }
        })

        return jsonify({
            "object": object,
            "acc": acc
        })

class Refill(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["admin_pw"]
        refill_amount = posted_data["refill"]

        if not user_exists(username):
            return gen_status(301, "User not exists")

        correct_pw = 1234

        if not password == correct_pw:
            return gen_status(304, "Invalid administrator password")

        curr_tokens = count_tokens(username)
        users.update({
            "username": username
        }, {
            "$set": {
                "tokens" : curr_tokens + refill_amount
            }
        })

        return gen_status(200, "Refill successful")



api.add_resource(Register, "/register")
api.add_resource(Classification, "/classify")
api.add_resource(Refill, "/refill")

if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug=True)
