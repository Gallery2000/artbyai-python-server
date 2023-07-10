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
    def __init__(self, discord_id: int, channel_id: str):
        super().__init__()
        self.discord_id = discord_id
        self.channel_id = channel_id

    async def on_ready(self):
        for session in self.sessions:
            update_discord_ssid(self.discord_id, session.session_id)
            return

    def callback_message(self, message_type, extra):
        """Helper function to construct callback message and execute callback."""
        callback_discord(self.discord_id, {
            **{
                "type": message_type,
            }, **extra
        })

    async def on_message(self, message):
        if message.author == self.user:
            return
        msg_data = {
            "msgId": str(message.id),
            "nonce": message.nonce,
            "content": message.content,
            "createdAt": message.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if message.created_at else None,
            "embeds": [embed.to_dict() for embed in message.embeds],
            "attachments": [
                {
                    "url": attachment.url,
                    "width": attachment.width,
                    "height": attachment.height
                } for attachment in message.attachments
            ],
            "components": [],
            "referMsgId": str(message.reference.message_id) if message.reference else "",
        }

        while len(msg_data["components"]) < len(message.components):
            msg_data["components"].append({})

        for i, component in enumerate(message.components):
            msg_data["components"][i]["children"] = []
            for button in component.children:
                msg_data["components"][i]["children"].append({
                    "emoji": button.emoji.name if button.emoji else None,
                    "label": button.label,
                    "custom_id": button.custom_id,
                })

        if str(message.channel.id) == self.dm_channel_id:
            self.callback_message(DIRECT_MESSAGE, msg_data)
        elif str(message.channel.id) == self.channel_id:
            self.handle_channel_message(message, msg_data)

    def handle_channel_message(self, message, msg_data):
        """Handle messages for a specific channel id."""
        if "(Waiting to start)" in message.content and "Rerolling **" not in message.content:
            self.callback_message(FIRST_TRIGGER, msg_data)
        elif "(Stopped)" in message.content:
            self.callback_message(GENERATE_EDIT_ERROR, msg_data)
        elif "/relax" in message.content or "/fast" in message.content:
            self.callback_message(RICH_TEXT, msg_data)
        elif message.attachments and any(att.width > 0 and att.height > 0 for att in message.attachments):
            self.callback_message(GENERATE_END, msg_data)
        elif message.embeds and message.embeds[0].type == "rich":
            self.callback_message(RICH_TEXT, msg_data)

    async def on_raw_message_edit(self, payload):
        try:
            if payload.data is None:
                return
            if payload.data['author']['id'] == self.user.id:
                return

            msg_data = {
                "msgId": str(payload.message_id),
                "nonce": "" if payload.cached_message is None else payload.cached_message.nonce,
                "content": payload.data["content"],
                "referMsgId": None if payload.cached_message is None or payload.cached_message.reference is None else str(
                    payload.cached_message.reference.message_id),
                "createdAt": None if payload.cached_message is None else payload.cached_message.created_at.strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"),
                "embeds": payload.data['embeds'],
                "attachments": payload.data['attachments'],
                "components": [],
            }

            while len(msg_data["components"]) < len(payload.data["components"]):
                msg_data["components"].append({})

            for i, component in enumerate(payload.data["components"]):
                msg_data["components"][i]["children"] = []
                for button in component["components"]:
                    msg_data["components"][i]["children"].append({
                        "label": button["label"] if "label" in button else "",
                        "emoji": button["emoji"]["name"] if "emoji" in button and button["emoji"] else None,
                        "custom_id": button["custom_id"],
                    })

            if str(payload.channel_id) == self.channel_id:
                self.handle_edit_channel_message(payload, msg_data)

        except Exception as e:
            logger.error(f"Error in on_raw_message_edit: {e}")

    def handle_edit_channel_message(self, payload, msg_data):
        """Handle edited messages for a specific channel id."""
        if "(Waiting to start)" in msg_data["content"] and "Rerolling **" not in msg_data["content"]:
            self.callback_message(FIRST_TRIGGER, msg_data)
        elif "(Stopped)" in msg_data["content"]:
            self.callback_message(GENERATE_EDIT_ERROR, msg_data)
        elif "/relax" in msg_data["content"] or "/fast" in msg_data["content"]:
            self.callback_message(RICH_TEXT, msg_data)
        elif payload.data['attachments']:
            self.callback_message(GENERATING, msg_data)
        elif payload.data['embeds'] and payload.data['embeds'][0]['type'] == "rich":
            self.callback_message(RICH_TEXT, msg_data)
