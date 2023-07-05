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
GENERATING = "Generating"


def callback_discord(discord_id: int, data: dict) -> None:
    response = requests.post(BASE_URL + "/callback/discord", json=data)
    try:
        response.raise_for_status()
        res = response.json()
        if res["code"] == 0:
            logger.info("Callback Discord " + str(discord_id) + " success")
        else:
            logger.error("Callback Discord " + str(discord_id) + " error: " + res["msg"])
    except requests.HTTPError as e:
        logger.error("Callback Discord " + str(discord_id) + " error: " + str(e))


def update_discord_ssid(discord_id: int, session_id: str) -> None:
    response = requests.patch(BASE_URL + "/manage/updateManDiscordSSID", json={
        "id": discord_id,
        "sessionId": session_id
    })
    try:
        response.raise_for_status()
        res = response.json()
        if res["code"] == 0:
            logger.info("Update Discord " + str(discord_id) + " SSID success")
        else:
            logger.error("Update Discord " + str(discord_id) + " SSID error: %s", res["msg"])
    except requests.HTTPError as e:
        logger.error("Update Discord SSID " + str(discord_id) + " error: %s", str(e))


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
        self.discord_id = discord_id
        self.channel_id = channel_id
        self.dm_channel_id = dm_channel_id

    async def on_ready(self):
        for session in self.sessions:
            update_discord_ssid(self.discord_id, session.session_id)
            return

    def callback_message(self, message_type, message_id, nonce, content, created_at, extra):
        """Helper function to construct callback message and execute callback."""
        callback_discord(self.discord_id, {
            **{
                "type": message_type,
                "content": content,
                "nonce": nonce,
                "msgId": message_id,
                "createAt": created_at,
            }, **extra
        })

    async def on_message(self, message):
        if message.author == self.user:
            return

        message_id = str(message.id)
        nonce = message.nonce
        content = message.content
        created_at = message.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if message.created_at else None

        if str(message.channel.id) == self.dm_channel_id:
            self.callback_message(DIRECT_MESSAGE, message_id, nonce, content, created_at, {
                "attachments": [
                    {
                        "url": attachment.url,
                        "width": attachment.width,
                        "height": attachment.height
                    } for attachment in message.attachments
                ],
            })
        elif str(message.channel.id) == self.channel_id:
            self.handle_channel_message(message, message_id, nonce, content, created_at)

    def handle_channel_message(self, message, msgId, nonce, content, createdAt):
        """Handle messages for a specific channel id."""
        if "(Waiting to start)" in content and "Rerolling **" not in content:
            self.callback_message(FIRST_TRIGGER, msgId, nonce, content, createdAt, {})
        elif "(Stopped)" in content:
            self.callback_message(GENERATE_EDIT_ERROR, msgId, nonce, content, createdAt, {})
        elif "/(`/fast`|`/relax`)" in content:
            self.callback_message(RICH_TEXT, msgId, nonce, content, createdAt, {})
        elif message.attachments and any(att.width > 0 and att.height > 0 for att in message.attachments):
            self.callback_message(GENERATE_END, msgId, nonce, content, createdAt, {
                "attachments": [
                    {
                        "url": attachment.url,
                        "width": attachment.width,
                        "height": attachment.height
                    } for attachment in message.attachments
                ]
            })
        elif message.embeds and message.embeds[0].type == "rich":
            self.callback_message(RICH_TEXT, msgId, nonce, content, createdAt, {
                "embeds": [embed.to_dict() for embed in message.embeds],
                "flags": message.flags.value
            })

    async def on_raw_message_edit(self, payload):
        try:
            if payload.data['author']['id'] == self.user.id:
                return

            message_id = str(payload.message_id)
            nonce = "" if payload.cached_message is None else payload.cached_message.nonce
            content = payload.data["content"]
            created_at = None if payload.cached_message is None else payload.cached_message.created_at.strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ")

            if str(payload.channel_id) == self.channel_id:
                self.handle_edit_channel_message(payload, message_id, nonce, content, created_at)

        except Exception as e:
            logger.error(f"Error in on_raw_message_edit: {e}")

    def handle_edit_channel_message(self, payload, message_id, nonce, content, created_at):
        """Handle edited messages for a specific channel id."""
        if "(Waiting to start)" in content and "Rerolling **" not in content:
            self.callback_message(FIRST_TRIGGER, message_id, nonce, content, created_at, {})
        elif "(Stopped)" in content:
            self.callback_message(GENERATE_EDIT_ERROR, message_id, nonce, content, created_at, {})
        elif "/(`/fast`|`/relax`)" in content:
            self.callback_message(RICH_TEXT, message_id, nonce, content, created_at, {})
        elif payload.data['attachments']:
            self.callback_message(GENERATING, message_id, nonce, content, created_at, {
                "attachments": payload.data['attachments'],
            })
        elif payload.data['embeds'] and payload.data['embeds'][0]['type'] == "rich":
            self.callback_message(RICH_TEXT, message_id, nonce, content, created_at, {
                "embeds": payload.data['embeds'],
            })
