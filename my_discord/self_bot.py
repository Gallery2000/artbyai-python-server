from typing import List

import discord
import requests
from loguru import logger

BASE_URL = "http://127.0.0.1:8888"

FIRST_TRIGGER = "FirstTrigger"
GENERATE_END = "GenerateEnd"
GENERATE_EDIT_ERROR = "GenerateEditError"
RICH_Text = "RichText"


def callback_discord(json: dict):
    requests.post(BASE_URL + "/callback/discord", json=json)


def update_discord_ssid(discord_id, session_id):
    response = requests.patch(BASE_URL + "/manage/updateManDiscordSSID", json={
        "id": discord_id,
        "sessionId": session_id
    })
    try:
        response.raise_for_status()
        res = response.json()
        if res["code"] == 0:
            logger.info("update discord ssid success")
        else:
            logger.error("update discord ssid error: %s", res["msg"])
    except requests.HTTPError as e:
        logger.error("update my_discord ssid error: %s", str(e))


def get_all_discord() -> List[dict]:
    response = requests.get(BASE_URL + "/manage/getAllManDiscord")
    try:
        response.raise_for_status()
        res = response.json()
        if res["code"] == 0:
            return res["data"]
        else:
            logger.error("get all discord error: " + res["msg"])
    except requests.HTTPError as e:
        logger.error("update discord ssid error: %s", str(e))


class SelfBot:
    def __init__(self, channel_id: str, user_token: str):
        self.channel_id = int(channel_id)
        self.user_token = user_token

    def run_discord_bot(my_self, discord_id):
        class MyClient(discord.Client):
            async def on_ready(self):
                for i in range(len(self.sessions)):
                    update_discord_ssid(discord_id, self.sessions[i].session_id)
                    break

            async def on_message(self, message):

                if message.author == self.user:
                    return
                if message.channel.id != my_self.channel_id:
                    return
                if "(Waiting to start)" in message.content and "Rerolling **" not in message.content:
                    callback_discord({
                        "type": FIRST_TRIGGER,
                        "content": message.content,
                        "nonce": message.nonce
                    })
                    return

                for i in range(len(message.attachments)):
                    if message.attachments[i].width > 0 and message.attachments[i].height > 0:
                        callback_discord({
                            "type": GENERATE_END,
                            "attachments": [
                                {
                                    "url": attachment.url,
                                    "width": attachment.width,
                                    "height": attachment.height
                                } for attachment in message.attachments
                            ],
                            "content": message.content,
                            "nonce": message.nonce
                        })
                        return

                if "(Stopped)" in message.content:
                    callback_discord({
                        "type": GENERATE_EDIT_ERROR,
                        "content": message.content,
                        "nonce": message.nonce
                    })
                    return

                if len(message.embeds) > 0:
                    if message.embeds[0].type == "rich":
                        callback_discord({
                            "type": RICH_Text,
                            "embeds": message.embeds,
                            "nonce": message.nonce
                        })
                        return

            async def on_raw_message_edit(self, payload):
                try:
                    if payload.data['author']['id'] == self.user.id:
                        return
                    if payload.channel_id != my_self.channel_id:
                        return
                    if len(payload.data['embeds']) > 0:
                        embeds = payload.data['embeds']
                        if embeds[0]['type'] == "rich":
                            nonce = payload.cached_message.nonce
                            callback_discord({
                                "type": RICH_Text,
                                "embeds": embeds,
                                "nonce": nonce
                            })
                            return
                except Exception as e:
                    print(f"Error in on_raw_message_edit: {e}")

        client = MyClient()
        client.run(my_self.user_token)
