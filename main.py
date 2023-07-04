import threading

from flask import Flask
from loguru import logger

from my_discord import SelfBot, get_all_discord

app = Flask(__name__)
existing_self_bots = []
reset_lock = threading.Lock()


def reset_self_bots(existing_self_bots):
    current_discord_list = get_all_discord()
    current_ids = [discord_data["id"] for discord_data in current_discord_list]

    # Check for removed Discord accounts
    removed_ids = [self_bot.id for self_bot in existing_self_bots if self_bot.id not in current_ids]
    for removed_id in removed_ids:
        self_bot = next((self_bot for self_bot in existing_self_bots if self_bot.id == removed_id), None)
        if self_bot:
            self_bot.stop()
            existing_self_bots.remove(self_bot)
            logger.warning(f"Self bot for Discord account {removed_id} has been removed.")

    # Check for added or updated Discord accounts
    for discord_data in current_discord_list:
        if discord_data["id"] in current_ids:
            self_bot = next((self_bot for self_bot in existing_self_bots if self_bot.id == discord_data["id"]), None)
            if self_bot:
                if self_bot.channel_id != discord_data["channelId"]:
                    self_bot.channel_id = discord_data["channelId"]
                    logger.warning(f"Channel ID updated for Discord account {self_bot.id}")
                if self_bot.dm_channel_id != discord_data["dmChannelId"]:
                    self_bot.dm_channel_id = discord_data["dmChannelId"]
                    logger.warning(f"DM Channel ID updated for Discord account {self_bot.id}")
                if self_bot.user_token != discord_data["userToken"]:
                    self_bot.user_token = discord_data["userToken"]
                    logger.warning(f"User token updated for Discord account {self_bot.id}")
                    self_bot.stop()
                    self_bot.run(self_bot.user_token)
            else:
                self_bot = SelfBot(discord_data["id"], discord_data["channelId"], discord_data["dmChannelId"])
                self_bot.user_token = discord_data["userToken"]
                self_bot.run(self_bot.user_token)
                existing_self_bots.append(self_bot)
                logger.warning(f"Self bot for Discord account {discord_data['id']} has been added.")


def reset_bots():
    with reset_lock:
        reset_self_bots(existing_self_bots)


# Call reset_self_bots initially
reset_bots()


@app.route('/reset-bots', methods=['POST'])
def reset_bots_route():
    logger.info("Received reset-bots request")
    thread = threading.Thread(target=reset_bots)
    thread.start()
    return "Bots reset successfully."


# Start the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
