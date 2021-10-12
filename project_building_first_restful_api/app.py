from flask import Flask, jsonify, request
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

@app.route('/')
def hello_msg():
    print("Hello User. You can use several APIs listed below.")


def check_posted_data(posted_data, function_name):
    if function_name == "add" or function_name == "sub" or function_name == "multi":
        if "x" not in posted_data or "y" not in posted_data:
            return 301
        else:
            return 200

    elif function_name == "div":
        if "x" not in posted_data or "y" not in posted_data:
            return 301
        elif posted_data["y"] == 0:
            return 302
        else:
            return 200

class Add(Resource):
    def post(self):
        # Step 1: Get posted data
        posted_data = request.get_json()

        # Step 2: Verify validity of posted data
        status_code = check_posted_data(posted_data, "add")
        if status_code != 200:
            ret_json = {
                "Message": "An error happened!",
                "Status Code": status_code
            }
            return jsonify(ret_json)

        x = posted_data['x']
        y = posted_data['y']
        x = int(x)
        y = int(y)

        # Step 2: Add the posted data
        ret = x + y
        ret_map = {
            'Message': ret,
            'Status Code': 200
        }
        # Step 3: Return the response to the user
        return jsonify(ret_map)


class Subtract(Resource):
    def post(self):
        # Step 1: Get posted data
        posted_data = request.get_json()

        # Step 2: Verify validity of posted data
        status_code = check_posted_data(posted_data, "sub")
        if status_code != 200:
            ret_json = {
                "Message": "An error happened!",
                "Status Code": status_code
            }
            return jsonify(ret_json)

        x = posted_data['x']
        y = posted_data['y']
        x = int(x)
        y = int(y)

        # Step 2: Subtract the posted data
        ret = x - y
        ret_map = {
            'Message': ret,
            'Status Code': 200
        }
        # Step 3: Return the response to the user
        return jsonify(ret_map)

class Multiply(Resource):
    def post(self):
        # Step 1: Get posted data
        posted_data = request.get_json()

        # Step 2: Verify validity of posted data
        status_code = check_posted_data(posted_data, "multi")
        if status_code != 200:
            ret_json = {
                "Message": "An error happened!",
                "Status Code": status_code
            }
            return jsonify(ret_json)

        x = posted_data['x']
        y = posted_data['y']
        x = int(x)
        y = int(y)

        # Step 2: Multiply the posted data
        ret = x * y
        ret_map = {
            'Message': ret,
            'Status Code': 200
        }
        # Step 3: Return the response to the user
        return jsonify(ret_map)

class Divide(Resource):
    def post(self):
        # Step 1: Get posted data
        posted_data = request.get_json()

        # Step 2: Verify validity of posted data
        status_code = check_posted_data(posted_data, "div")
        if status_code != 200:
            ret_json = {
                "Message": "An error happened!",
                "Status Code": status_code
            }
            return jsonify(ret_json)

        x = posted_data['x']
        y = posted_data['y']
        x = int(x)
        y = int(y)

        # Step 2: Divide the posted data
        ret = (x*1.0) / y
        ret_map = {
            'Message': ret,
            'Status Code': 200
        }
        # Step 3: Return the response to the user
        return jsonify(ret_map)


api.add_resource(Add, "/add")
api.add_resource(Subtract, "/sub")
api.add_resource(Multiply, "/multi")
api.add_resource(Divide, "/div")


if __name__ == "__main__":
    app.run(debug=True)
