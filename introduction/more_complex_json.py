from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return f"Hello World \n Options: /hi\n /bye"

@app.route('/hi')
def hi():
    return f"Hi Stef!"

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
