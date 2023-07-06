import threading

from loguru import logger

from .self_bot import SelfBot, update_discord_ssid, get_all_discord

existing_self_bots = []


def reset_self_bots(existing_self_bots):
    current_discord_list = get_all_discord()
    current_ids = [discord_data["id"] for discord_data in current_discord_list]

    # Check for removed Discord accounts
    removed_ids = [self_bot.discord_id for self_bot in existing_self_bots if self_bot.discord_id not in current_ids]
    for removed_id in removed_ids:
        self_bot = next((self_bot for self_bot in existing_self_bots if self_bot.discord_id == removed_id), None)
        if self_bot:
            self_bot.stop()
            existing_self_bots.remove(self_bot)
            logger.warning(f"Self bot for Discord account {removed_id} has been removed.")

    # Check for added or updated Discord accounts
    for discord_data in current_discord_list:
        if discord_data["id"] in current_ids:
            self_bot = next((self_bot for self_bot in existing_self_bots if self_bot.discord_id == discord_data["id"]),
                            None)
            if self_bot:
                if self_bot.channel_id != discord_data["channelId"]:
                    self_bot.channel_id = discord_data["channelId"]
                    logger.warning(f"Channel ID updated for Discord account {self_bot.discord_id}")
                if self_bot.dm_channel_id != discord_data["dmChannelId"]:
                    self_bot.dm_channel_id = discord_data["dmChannelId"]
                    logger.warning(f"DM Channel ID updated for Discord account {self_bot.discord_id}")
                if self_bot.user_token != discord_data["userToken"]:
                    self_bot.user_token = discord_data["userToken"]
                    logger.warning(f"User token updated for Discord account {self_bot.discord_id}")
                    try:
                        my_thread = threading.Thread(target=self_bot.run, args=(self_bot.user_token,))
                        my_thread.start()
                    except Exception as e:
                        logger.error(f"Error while restarting Discord account {self_bot.discord_id}: {e}")
            else:
                self_bot = SelfBot(discord_data["id"], discord_data["channelId"], discord_data["dmChannelId"])
                self_bot.user_token = discord_data["userToken"]
                logger.warning(f"Self bot for Discord account {discord_data['id']} has been added.")
                existing_self_bots.append(self_bot)
                try:
                    my_thread = threading.Thread(target=self_bot.run, args=(self_bot.user_token,))
                    my_thread.start()
                except Exception as e:
                    logger.error(f"Error while restarting Discord account {self_bot.discord_id}: {e}")
