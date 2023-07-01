from typing import List

import discord
import requests
from loguru import logger

BASE_URL = "http://127.0.0.1:8888"

FIRST_TRIGGER = "FirstTrigger"
GENERATE_END = "GenerateEnd"
GENERATE_EDIT_ERROR = "GenerateEditError"
RICH_TEXT = "RichText"


def callback_discord(data: dict) -> None:
    requests.post(BASE_URL + "/callback/discord", json=data)


def update_discord_ssid(discord_id: int, session_id: str) -> None:
    data = {
        "id": discord_id,
        "sessionId": session_id
    }
    response = requests.patch(BASE_URL + "/manage/updateManDiscordSSID", json=data)
    try:
        response.raise_for_status()
        res = response.json()
        if res["code"] == 0:
            logger.info("Update Discord SSID success")
        else:
            logger.error("Update Discord SSID error: %s", res["msg"])
    except requests.HTTPError as e:
        logger.error("Update Discord SSID error: %s", str(e))


def get_all_discord() -> List[dict]:
    response = requests.get(BASE_URL + "/manage/getAllManDiscord")
    try:
        response.raise_for_status()
        res = response.json()
        if res["code"] == 0:
            return res["data"]
        else:
            logger.error("Get all Discord error: " + res["msg"])
    except requests.HTTPError as e:
        logger.error("Get all Discord error: %s", str(e))


class SelfBot(discord.Client):
    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id

    async def on_ready(self):
        for session in self.sessions:
            update_discord_ssid(self.channel_id, session.session_id)
            return

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.channel.id != self.channel_id:
            return

        if "(Waiting to start)" in message.content and "Rerolling **" not in message.content:
            callback_discord({
                "type": FIRST_TRIGGER,
                "content": message.content,
                "nonce": message.nonce
            })
            return

        for attachment in message.attachments:
            if attachment.width > 0 and attachment.height > 0:
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

        if message.embeds:
            if message.embeds[0].type == "rich":
                callback_discord({
                    "type": RICH_TEXT,
                    "embeds": message.embeds,
                    "nonce": message.nonce
                })
                return

    async def on_raw_message_edit(self, payload):
        try:
            if payload.data['author']['id'] == self.user.id:
                return
            if payload.channel_id != self.channel_id:
                return
            if payload.data['embeds']:
                embeds = payload.data['embeds']
                if embeds[0]['type'] == "rich":
                    nonce = payload.cached_message.nonce
                    callback_discord({
                        "type": RICH_TEXT,
                        "embeds": embeds,
                        "nonce": nonce
                    })
                    return
        except Exception as e:
            logger.error(f"Error in on_raw_message_edit: {e}")
