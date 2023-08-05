import os
import threading

from loguru import logger

import glovar
import models
from api import LarkApi
from config import get_config
from discord_client import MyClient
from handlers import app

if not os.path.exists('log'):
    os.makedirs('log')

log_file = os.path.join('log', '{time:YYYY-MM-DD}.log')
logger.add(log_file, rotation="500 MB", compression="zip")

config = get_config()

logger.info('base url: ' + config["base_url"])

if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    glovar.discord_id = config["discord_id"]
    glovar.lark_api = LarkApi(config["base_url"])
    glovar.secret_key = config["secret_key"]
    data = glovar.lark_api.get_discord()
    if data is None:
        logger.error("Discord " + str(config["discord_id"]) + " not found")
        exit(1)
    else:
        glovar.discord = models.Discord(data["userToken"], data["sessionId"], data["channelId"], data["guildId"],
                                        data["dmChannelId"])
    client = MyClient()
    bot_thread = threading.Thread(target=client.run, args=(glovar.discord.user_token,))
    bot_thread.daemon = True
    bot_thread.start()

if __name__ == '__main__':
    app.run(debug=True, port=config["port"])
