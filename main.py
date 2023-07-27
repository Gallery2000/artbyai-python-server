import threading
import time

import discord
from loguru import logger

from config import get_config
from discord_api import DiscordApi

PLAINTEXT = "PlainText"
FIRST_TRIGGER = "FirstTrigger"
GENERATE_END = "GenerateEnd"
GENERATE_EDIT_ERROR = "GenerateEditError"
RICH_TEXT = "RichText"
DIRECT_MESSAGE = "DirectMessage"
GENERATING = "Generating"
INTERACTION_FINISH = "InteractionFinish"

config = get_config()
BASE_URL = config["base_url"]
DISCORD_ID = config["discord_id"]

discord_api = DiscordApi(BASE_URL)
discord_data = discord_api.get_discord(DISCORD_ID)
if not discord_data:
    logger.error("Discord " + str(DISCORD_ID) + " not found")
    exit(1)


def schedule_function(discord_id):
    while True:
        discord_api.trigger_time(discord_id)
        time.sleep(60)


class MyClient(discord.Client):
    def __init__(self, discord_id: int, channel_id: str, dm_channel_id: str):
        super().__init__()
        self.discord_id = discord_id
        self.channel_id = channel_id
        self.dm_channel_id = dm_channel_id

    async def on_ready(self):
        timer_thread = threading.Thread(target=schedule_function, args=(self.discord_id,))
        timer_thread.daemon = True
        timer_thread.start()

        for session in self.sessions:
            discord_api.update_discord_ssid(self.discord_id, session.session_id)
            return

    def callback_message(self, message_type, extra):
        """Helper function to construct callback message and execute callback."""
        discord_api.callback_discord(self.discord_id, {
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
            "discordId": self.discord_id,
            "flags": message.flags.value,
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
            self.callback_message(PLAINTEXT, msg_data)
        elif "/prefer remix" in message.content:
            self.callback_message(PLAINTEXT, msg_data)
        elif message.attachments and any(att.width > 0 and att.height > 0 for att in message.attachments):
            self.callback_message(GENERATE_END, msg_data)
        elif message.embeds and message.embeds[0].type == "rich":
            self.callback_message(RICH_TEXT, msg_data)
        elif message.content:
            self.callback_message(PLAINTEXT, msg_data)

    async def on_raw_message_edit(self, payload):
        try:
            if payload.data is None:
                return
            if payload.data['author'] is None:
                return
            if payload.data['author']['id'] == self.user.id:
                return

            msg_data = {
                "msgId": str(payload.message_id),
                "nonce": "" if payload.cached_message is None else payload.cached_message.nonce,
                "content": payload.data["content"],
                "flags": payload.data["flags"],
                "referMsgId": None if payload.cached_message is None or payload.cached_message.reference is None else str(
                    payload.cached_message.reference.message_id),
                "createdAt": None if payload.cached_message is None else payload.cached_message.created_at.strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"),
                "embeds": payload.data['embeds'],
                "attachments": payload.data['attachments'],
                "components": [],
                "discordId": self.discord_id,
            }

            while len(msg_data["components"]) < len(payload.data["components"]):
                msg_data["components"].append({})

            for i, component in enumerate(payload.data["components"]):
                msg_data["components"][i]["children"] = []
                for button in component["components"]:
                    msg_data["components"][i]["children"].append({
                        "label": button["label"] if "label" in button else "",
                        "emoji": button["emoji"]["name"] if "emoji" in button and button["emoji"] else None,
                        "custom_id": button["custom_id"] if "custom_id" in button else "",
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
            self.callback_message(PLAINTEXT, msg_data)
        elif "/prefer remix" in msg_data["content"]:
            self.callback_message(PLAINTEXT, msg_data)
        elif payload.data['attachments']:
            self.callback_message(GENERATING, msg_data)
        elif payload.data['embeds'] and payload.data['embeds'][0]['type'] == "rich":
            self.callback_message(RICH_TEXT, msg_data)
        elif msg_data["content"]:
            self.callback_message(PLAINTEXT, msg_data)

    async def on_interaction_finish(self, interaction):
        my_thread = threading.Thread(target=self.callback_message, args=(INTERACTION_FINISH, {
            "dataId": str(interaction.id),
            "nonce": interaction.nonce,
            "discordId": self.discord_id,
        }))
        my_thread.start()


client = MyClient(discord_data["id"], discord_data["channelId"], discord_data["dmChannelId"])
client.run(discord_data["userToken"])
