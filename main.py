import os
import threading

from loguru import logger

from api import DiscordApi
from config import get_config
from discord_client import MyClient
from handlers import app

config = get_config()

if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    discord_api = DiscordApi(config["base_url"])
    discord_data = discord_api.get_discord(config["discord_id"])
    if not discord_data:
        logger.error("Discord " + str(config["discord_id"]) + " not found")
        exit(1)

    client = MyClient(discord_data["id"], discord_data["channelId"], discord_data["dmChannelId"], discord_api)

    bot_thread = threading.Thread(target=client.run, args=(discord_data["userToken"],))
    bot_thread.daemon = True
    bot_thread.start()

if __name__ == '__main__':
    app.run(debug=True, port=config["port"])
