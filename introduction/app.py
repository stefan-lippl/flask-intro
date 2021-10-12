from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return f"Hello World \n Options: /hi\n /bye"


@app.route('/hi')
def hi():
    return f"Hi Stef!"


@app.route('/add_two_nums', methods=["POST"])
def add_two_nums():
    data_dict = request.get_json()
    x = data_dict['x']
    y = data_dict['y']

    z = x + y

    ret_json =  {
        "z": z
    }
    return jsonify(ret_json), 200


@app.route('/bye')
def bye():
    ret_json = {
        'name': 'Stef',
        'age': 27,
        'phones': [
            {
                'phone_name': 'iPhone 11 pro',
                'phone_number': +4915123472175
            },
            {
                'phone_name': 'Samsung S11+',
                'phone_number': +49123456789
            }
        ]
    }
    return jsonify(ret_json)


if __name__ == "__main__":
    app.run(debug=True)
