from flask import Flask

app = Flask(__name__)


@app.route('/reset-bots', methods=['POST'])
def reset_bots_route():
    return "Bots reset successfully."


# Start the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
