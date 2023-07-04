from typing import List

import discord
import requests
from loguru import logger

BASE_URL = "http://127.0.0.1:8888"

FIRST_TRIGGER = "FirstTrigger"
GENERATE_END = "GenerateEnd"
GENERATE_EDIT_ERROR = "GenerateEditError"
RICH_TEXT = "RichText"
DIRECT_MESSAGE = "DirectMessage"


def callback_discord(data: dict) -> None:
    response = requests.post(BASE_URL + "/callback/discord", json=data)
    try:
        response.raise_for_status()
        res = response.json()
        if res["code"] == 0:
            logger.info("Callback Discord success")
        else:
            logger.error("Callback Discord error: " + res["msg"])
    except requests.HTTPError as e:
        logger.error("Callback Discord error: " + str(e))


def update_discord_ssid(discord_id: int, session_id: str) -> None:
    response = requests.patch(BASE_URL + "/manage/updateManDiscordSSID", json={
        "id": discord_id,
        "sessionId": session_id
    })
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
            logger.info("Get all Discord success")
            return res["data"]
        else:
            logger.error("Get all Discord error: " + res["msg"])
    except requests.HTTPError as e:
        logger.error("Get all Discord error: %s", str(e))


class SelfBot(discord.Client):
    def __init__(self, discord_id: int, channel_id: str, dm_channel_id: str):
        super().__init__()
        self.discord_id = int(discord_id)
        self.channel_id = int(channel_id)
        self.dm_channel_id = int(dm_channel_id)

    async def on_ready(self):
        for session in self.sessions:
            update_discord_ssid(self.discord_id, session.session_id)
            return

    async def on_message(self, message):
        if message.author == self.user:
            return
        content = message.content
        msg_id = str(message.id)
        nonce = message.nonce
        created_at = None
        if message.created_at is not None:
            created_at = message.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if message.channel.id == self.dm_channel_id:
            callback_discord({
                "type": DIRECT_MESSAGE,
                "content": content,
                "attachments": [
                    {
                        "url": attachment.url,
                        "width": attachment.width,
                        "height": attachment.height
                    } for attachment in message.attachments
                ],
                "nonce": nonce,
                "msgId": msg_id,
                "createAt": created_at,
            })
            return
        if message.channel.id != self.channel_id:
            return

        if "(Waiting to start)" in content and "Rerolling **" not in content:
            callback_discord({
                "type": FIRST_TRIGGER,
                "content": content,
                "nonce": nonce,
                "msgId": msg_id,
                "createAt": created_at,
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
                    "content": content,
                    "nonce": nonce,
                    "msgId": msg_id,
                    "createAt": created_at,
                })
                return

        if "(Stopped)" in content:
            callback_discord({
                "type": GENERATE_EDIT_ERROR,
                "content": content,
                "nonce": nonce,
                "msgId": msg_id,
                "createAt": created_at,
            })
            return

        if message.embeds:
            if message.embeds[0].type == "rich":
                callback_discord({
                    "type": RICH_TEXT,
                    "embeds": [embed.to_dict() for embed in message.embeds],
                    "nonce": nonce,
                    "msgId": msg_id,
                    "flags": message.flags.value,
                    "createAt": created_at,
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
                        "nonce": nonce,
                        "msgId": str(payload.message_id)
                    })
                    return
        except Exception as e:
            logger.error(f"Error in on_raw_message_edit: {e}")
