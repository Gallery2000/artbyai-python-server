import os
import threading

from flask import Flask

from my_discord import reset_self_bots, existing_self_bots

app = Flask(__name__)


@app.route('/reset-bots', methods=['POST'])
def reset_bots_route():
    return "Bots reset successfully."


# Start the Flask app
if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        threading.Thread(target=reset_self_bots, args=(existing_self_bots,)).start()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
