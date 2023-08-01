import json
import os
import re

import requests

import glovar
import utils
from constant import custom

INTERACTIONS_URL = "https://discord.com/api/v9/interactions"
APPLICATION_ID = "936929561302675456"

REMIX_TYPE = "Remix by"
VARIATIONS_TYPE = "Variations by"
ZOOM_OUT_TYPE = "Zoom Out by"
PAN_LEFT_TYPE = "Pan Left by"
PAN_RIGHT_TYPE = "Pan Right by"
PAN_DOWN_TYPE = "Pan Down by"
PAN_UP_TYPE = "Pan Up by"


def get_data_custom(params):
    if params['variationType'] in [VARIATIONS_TYPE, REMIX_TYPE]:
        data_custom_id = f"MJ::RemixModal::{params['msgHash']}::1"
        com_custom_id = "MJ::RemixModal::new_prompt"
    elif ZOOM_OUT_TYPE in params['variationType']:
        data_custom_id = f"MJ::OutpaintModal::-1::1::{params['msgHash']}"
        com_custom_id = "MJ::OutpaintModal::new_prompt"
    elif PAN_LEFT_TYPE in params['variationType']:
        data_custom_id = f"MJ::PanModal::down::{params['msgHash']}"
        com_custom_id = "MJ::PanModal::prompt"
    elif PAN_RIGHT_TYPE in params['variationType']:
        data_custom_id = f"MJ::PanModal::right::{params['msgHash']}"
        com_custom_id = "MJ::PanModal::prompt"
    elif PAN_DOWN_TYPE in params['variationType']:
        data_custom_id = f"MJ::PanModal::left::{params['msgHash']}"
        com_custom_id = "MJ::PanModal::prompt"
    elif PAN_UP_TYPE in params['variationType']:
        data_custom_id = f"MJ::PanModal::up::{params['msgHash']}"
        com_custom_id = "MJ::PanModal::prompt"
    else:
        data_custom_id = f"MJ::ImagineModal::{params['discordMsgId']}"
        com_custom_id = "MJ::ImagineModal::new_prompt"
    return data_custom_id, com_custom_id


class DiscordApi:
    def req_midjourney(self, data):
        headers = {
            "Content-Type": "application/json",
            "Authorization": glovar.discord.user_token,
        }
        print(json.dumps(data))
        try:
            response = requests.post(INTERACTIONS_URL, json=data, headers=headers)
            response.raise_for_status()
            if response.text.strip():
                return ValueError(response.text)
            else:
                return None
        except requests.exceptions.RequestException as e:
            return e
        except json.JSONDecodeError as e:
            return e
        except Exception as e:
            return e

    def upload_file(self, image_file):
        try:
            file_size = len(image_file.read())
            image_file.seek(0)
            attachments_data, err = self.get_filename(image_file.filename, file_size)
            if err is not None:
                return None, err

            if len(attachments_data.get("attachments", [])) == 0:
                return None, ValueError("No attachments found")
            upload_url = attachments_data["attachments"][0]["upload_url"]

            headers = {
                "Content-Type": "image/png"
            }

            response = requests.put(upload_url, data=image_file, headers=headers)
            response.raise_for_status()
            return attachments_data['attachments'][0]['upload_filename'], None
        except Exception as e:
            return None, e

    def get_filename(self, name, size):
        attachments_url = f"https://discord.com/api/v9/channels/{glovar.discord.channel_id}/attachments"
        headers = {
            "Content-Type": "application/json",
            "Authorization": glovar.discord.user_token,
        }
        payload = {
            "files": [
                {
                    "filename": name,
                    "file_size": size,
                    "id": "1",
                }
            ]
        }

        try:
            response = requests.post(attachments_url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            return data, None
        except requests.exceptions.RequestException as e:
            return None, e

    def get_img_url(self, image_file):
        pathname, err = self.upload_file(image_file)
        if err is not None:
            return None, err
        messages_url = f"https://discord.com/api/v9/channels/{glovar.discord.channel_id}/messages"  # 请替换为实际的消息发送URL
        headers = {
            "Content-Type": "application/json",
            "Authorization": glovar.discord.user_token,
        }

        filename = os.path.basename(pathname)
        request_body = {
            "content": "",
            "nonce": utils.generate_nonce(),
            "channel_id": glovar.discord.channel_id,
            "type": 0,
            "sticker_ids": [],
            "attachments": [
                {
                    "id": "0",
                    "filename": filename,
                    "uploaded_filename": pathname,
                }
            ],
        }

        try:
            response = requests.post(messages_url, headers=headers, json=request_body)
            response.raise_for_status()

            data = response.json()
            if not data.get("attachments"):
                return "", ValueError("No attachments found")
            return data["attachments"][0]["url"], None
        except requests.exceptions.RequestException as e:
            return None, e

    def generate_image(self, params):
        request_body = {
            "type": 2,
            "guild_id": glovar.discord.guild_id,
            "channel_id": glovar.discord.channel_id,
            "application_id": APPLICATION_ID,
            "session_id": glovar.discord.session_id,
            "nonce": params["nonce"],
            "data": {
                "version": "1118961510123847772",
                "id": "938956540159881230",
                "name": "imagine",
                "type": 1,
                "options": [{"type": 3, "name": "prompt", "value": params["prompt"]}],
                "application_command": {
                    "id": "938956540159881230",
                    "application_id": APPLICATION_ID,
                    "version": "1118961510123847772",
                    "contexts": [1, 2, 3],
                    "default_permission": True,
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "imagine",
                    "description": "Create images with Midjourney",
                    "dm_permission": True,
                    "options": [
                        {"type": 3, "name": "prompt", "description": "The prompt to imagine", "required": True}
                    ]
                },
                "attachments": []
            }
        }

        err = self.req_midjourney(request_body)
        return err

    def prefer_remix(self, params):
        request_body = {
            "type": 2,
            "guild_id": glovar.discord.guild_id,
            "channel_id": glovar.discord.channel_id,
            "application_id": APPLICATION_ID,
            "session_id": glovar.discord.session_id,
            "nonce": params["nonce"],
            "data": {
                "version": "1121575372539039776",
                "id": "984273800587776053",
                "name": "prefer",
                "type": 1,
                "options": [{"type": 1, "name": "remix", "options": []}],
                "application_command": {
                    "id": "938956540159881230",
                    "application_id": APPLICATION_ID,
                    "version": "1118961510123847772",
                    "contexts": [1, 2, 3],
                    "default_permission": True,
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "prefer",
                    "description": "...",
                    "dm_permission": True,
                    "options": [
                        {"type": 2, "name": "option", "description": "...", "options": [
                            {"type": 1, "name": "set", "description": "Set a custom option.", "options": [
                                {"type": 3, "name": "option", "description": "..."},
                                {"type": 3, "name": "value", "description": "..."}
                            ]},
                            {"type": 1, "name": "list", "description": "View your current custom options.",
                             "options": []}
                        ]},
                        {"type": 1, "name": "auto_dm",
                         "description": "Whether or not to automatically send job results to your DMs."},
                        {"type": 1, "name": "suffix",
                         "description": "Suffix to automatically add to the end of every prompt. Leave empty to remove.",
                         "options": [
                             {"type": 3, "name": "new_value", "description": "..."}
                         ]},
                        {"type": 1, "name": "remix", "description": "Toggle remix mode."},
                        {"type": 1, "name": "variability", "description": "Toggle variability mode."}
                    ],
                },
                "attachments": []
            }
        }

        err = self.req_midjourney(request_body)
        return err

    def ask_question(self, params):
        request_body = {
            "type": 2,
            "guild_id": glovar.discord.guild_id,
            "channel_id": glovar.discord.channel_id,
            "application_id": APPLICATION_ID,
            "session_id": glovar.discord.session_id,
            "nonce": params["nonce"],
            "data": {
                "version": "1118961510123847771",
                "id": "994261739745050684",
                "name": "ask",
                "type": 1,
                "options": [{"type": 3, "name": "question", "value": params["prompt"]}],
                "application_command": {
                    "id": "994261739745050684",
                    "application_id": APPLICATION_ID,
                    "version": "1118961510123847771",
                    "contexts": [0, 1, 2],
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "ask",
                    "description": "Get an answer to a question.",
                    "dm_permission": True,
                    "options": [
                        {"type": 3, "name": "question", "description": "What is the question?", "required": True}
                    ]
                },
                "attachments": []
            }
        }

        err = self.req_midjourney(request_body)
        return err

    def view_information(self, params):
        request_body = {
            "type": 2,
            "guild_id": glovar.discord.guild_id,
            "channel_id": glovar.discord.channel_id,
            "application_id": APPLICATION_ID,
            "session_id": glovar.discord.session_id,
            "nonce": params["nonce"],
            "data": {
                "version": "1118961510123847776",
                "id": "972289487818334209",
                "name": "info",
                "type": 1,
                "options": [],
                "application_command": {
                    "id": "972289487818334209",
                    "application_id": APPLICATION_ID,
                    "version": "1118961510123847776",
                    "contexts": None,
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "info",
                    "description": "View information about your profile.",
                    "dm_permission": True
                },
                "attachments": []
            }
        }

        err = self.req_midjourney(request_body)
        return err

    def switch_to_fast_mode(self, params):
        request_body = {
            "type": 2,
            "guild_id": glovar.discord.guild_id,
            "channel_id": glovar.discord.channel_id,
            "application_id": APPLICATION_ID,
            "session_id": glovar.discord.session_id,
            "nonce": params["nonce"],
            "data": {
                "version": "987795926183731231",
                "id": "972289487818334212",
                "name": "fast",
                "type": 1,
                "options": [],
                "application_command": {
                    "id": "972289487818334209",
                    "application_id": APPLICATION_ID,
                    "version": "987795926183731231",
                    "contexts": None,
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "fast",
                    "description": "Switch to fast mode",
                    "dm_permission": True
                },
                "attachments": []
            }
        }

        err = self.req_midjourney(request_body)
        return err

    def switch_to_relax_mode(self, params):
        request_body = {
            "type": 2,
            "guild_id": glovar.discord.guild_id,
            "channel_id": glovar.discord.channel_id,
            "application_id": APPLICATION_ID,
            "session_id": glovar.discord.session_id,
            "nonce": params["nonce"],
            "data": {
                "version": "987795926183731232",
                "id": "972289487818334213",
                "name": "relax",
                "type": 1,
                "options": [],
                "application_command": {
                    "id": "972289487818334213",
                    "application_id": APPLICATION_ID,
                    "version": "987795926183731232",
                    "contexts": None,
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "relax",
                    "description": "Switch to relax mode",
                    "dm_permission": True
                },
                "attachments": []
            }
        }

        err = self.req_midjourney(request_body)
        return err

    def image_variation(self, params):
        request_body = {
            "type": 3,
            "guild_id": glovar.discord.guild_id,
            "channel_id": glovar.discord.channel_id,
            "message_flags": params["msgFlags"],
            "message_id": params["discordMsgId"],
            "application_id": APPLICATION_ID,
            "session_id": glovar.discord.session_id,
            "nonce": params["nonce"],
            "data": {
                "component_type": 2,
                "custom_id": params["customId"]
            }
        }

        err = self.req_midjourney(request_body)
        return err

    def describe_image(self, params):
        filename = os.path.basename(params["prompt"])
        uploaded_filename = params["prompt"]

        request_body = {
            "type": 2,
            "guild_id": glovar.discord.guild_id,
            "channel_id": glovar.discord.channel_id,
            "application_id": APPLICATION_ID,
            "session_id": glovar.discord.session_id,
            "nonce": params["nonce"],
            "data": {
                "version": "1118961510123847774",
                "id": "1092492867185950852",
                "name": "describe",
                "type": 1,
                "options": [{"type": 11, "name": "image", "value": 0}],
                "application_command": {
                    "id": "1092492867185950852",
                    "application_id": APPLICATION_ID,
                    "version": "1118961510123847774",
                    "contexts": [0, 1, 2],
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "describe",
                    "description": "Writes a prompt based on your image.",
                    "dm_permission": True,
                    "options": [
                        {"type": 11, "name": "image", "description": "The image to describe", "required": True}
                    ]
                },
                "attachments": [{
                    "id": "0",
                    "filename": filename,
                    "uploaded_filename": uploaded_filename
                }]
            }
        }

        err = self.req_midjourney(request_body)
        return err

    def blend_images(self, params):
        options = []
        for i, upload_name in enumerate(params["uploadNames"]):
            options.append({
                "type": 11,
                "name": f"image{i + 1}",
                "value": i + 1,
            })

        choices = [
            {"name": "Portrait", "Value": "--ar 2:3"},
            {"name": "Square", "Value": "--ar 1:1"},
            {"name": "Landscape", "Value": "--ar 3:2"},
        ]
        order_map = ["First", "Second", "Third", "Fourth", "Fifth"]
        command_options = []
        for i in range(len(params["uploadNames"])):
            command_options.append({
                "description": f"{order_map[i]} image to add to the blend",
                "name": f"image{i + 1}",
                "required": True,
                "type": 11,
            })
        if params.get("prompt") is not None:
            options.append({
                "type": 3,
                "name": "dimensions",
                "value": params["prompt"],
            })
        command_options.append({
            "choices": choices,
            "description": "The dimensions of the image. If not specified, the image will be square.",
            "name": "dimensions",
            "type": 3,
        })
        for i in range(len(command_options), 5):
            command_options.append({
                "description": f"{order_map[i]} image to add to the blend (optional)",
                "name": f"image{i + 1}",
                "type": 11,
            })

        attachments = []
        for i, uploaded_filename in enumerate(params["uploadNames"]):
            filename = os.path.basename(uploaded_filename)
            attachments.append({
                "id": str(i + 1),
                "filename": filename,
                "uploaded_filename": uploaded_filename,
            })

        request_body = {
            "type": 2,
            "guild_id": glovar.discord.guild_id,
            "channel_id": glovar.discord.channel_id,
            "application_id": APPLICATION_ID,
            "session_id": glovar.discord.session_id,
            "nonce": params["nonce"],
            "data": {
                "version": "1118961510123847773",
                "id": "1062880104792997970",
                "name": "blend",
                "type": 1,
                "options": options,
                "application_command": {
                    "id": "1062880104792997970",
                    "application_id": APPLICATION_ID,
                    "version": "1118961510123847773",
                    "contexts": [1, 2, 3],
                    "default_permission": True,
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "blend",
                    "description": "Blend images together seamlessly!",
                    "dm_permission": True,
                    "options": command_options
                },
                "attachments": attachments
            }
        }

        err = self.req_midjourney(request_body)
        return err

    def image_remix(self, params):

        data_custom_id = ""
        com_custom_id = ""

        if custom.CUSTOM_ZOOM in params["customId"]:
            data_custom_id = f"MJ::OutpaintCustomZoomModal::{params['msgHash']}"
            com_custom_id = "MJ::OutpaintCustomZoomModal::prompt"
        elif custom.VARIATION in params["customId"]:
            match = re.search(r"variation::(\d)", params["customId"])
            if match is not None:
                vary = match.group(1)
                data_custom_id = f"MJ::RemixModal::{params['msgHash']}::{vary}::1"
                com_custom_id = "MJ::RemixModal::new_prompt"
        elif custom.PAN in params["customId"]:
            re_match = re.search(r"pan_(\w+)", params["customId"])
            if re_match is not None:
                direction = re_match.group(1)
                data_custom_id = f"MJ::PanModal::{direction}::{params['msgHash']}"
                com_custom_id = "MJ::PanModal::prompt"
        elif custom.PROMPT_ANALYZER in params["customId"]:
            data_custom_id = f"MJ::ImagineModal::{params['discordMsgId']}"
            com_custom_id = "MJ::ImagineModal::new_prompt"
        elif custom.PIC_READER in params["customId"]:
            re_match = re.search(r"MJ::Job::PicReader::(\d)", params["customId"])
            if re_match is not None:
                pic_reader_id = re_match.group(1)
                data_custom_id = f"MJ::Picreader::Modal::{pic_reader_id}"
                com_custom_id = "MJ::Picreader::Modal::PromptField"
        elif custom.RE_ROLL in params["customId"]:
            data_custom_id, com_custom_id = get_data_custom(params)
        else:
            vary = 1
            if custom.LOW_VARIATION in params["customId"]:
                vary = 0
            data_custom_id = f"MJ::RemixModal::{params['msgHash']}::1::{vary}"
            com_custom_id = "MJ::RemixModal::new_prompt"

        print("data_custom_id: " + data_custom_id)
        print("com_custom_id: " + com_custom_id)

        request_body = {
            "type": 5,
            "guild_id": glovar.discord.guild_id,
            "channel_id": glovar.discord.channel_id,
            "application_id": APPLICATION_ID,
            "session_id": glovar.discord.session_id,
            "nonce": params["nonce"],
            "data": {
                "id": params["dataId"],
                "custom_id": data_custom_id,
                "components": [{
                    "type": 1,
                    "components": [{
                        "custom_id": com_custom_id,
                        "type": 4,
                        "value": params["prompt"]
                    }]
                }]
            }
        }

        err = self.req_midjourney(request_body)
        return err

    def shorten_prompt(self, params):
        request_body = {
            "type": 2,
            "guild_id": glovar.discord.guild_id,
            "channel_id": glovar.discord.channel_id,
            "application_id": APPLICATION_ID,
            "session_id": glovar.discord.session_id,
            "nonce": params["nonce"],
            "data": {
                "version": "1121575372539039775",
                "id": "1121575372539039774",
                "name": "shorten",
                "type": 1,
                "options": [{"name": "prompt", "type": 3, "value": params["prompt"]}],
                "application_command": {
                    "id": "1121575372539039774",
                    "application_id": APPLICATION_ID,
                    "version": "1121575372539039775",
                    "contexts": None,
                    "default_permission": True,
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "shorten",
                    "description": "Analyzes and shortens a prompt.",
                    "dm_permission": True,
                    "options": [
                        {"name": "prompt", "description": "The prompt to shorten.", "type": 3, "required": True}
                    ]
                },
                "attachments": []
            }
        }

        err = self.req_midjourney(request_body)
        return err

    def show_image(self, params):
        request_body = {
            "type": 2,
            "guild_id": glovar.discord.guild_id,
            "channel_id": glovar.discord.channel_id,
            "application_id": APPLICATION_ID,
            "session_id": glovar.discord.session_id,
            "nonce": params["nonce"],
            "data": {
                "version": "990020489659449405",
                "id": "990020489659449404",
                "name": "show",
                "type": 1,
                "options": [{"name": "job_id", "type": 3, "value": params["prompt"]}],
                "application_command": {
                    "id": "990020489659449404",
                    "application_id": APPLICATION_ID,
                    "version": "990020489659449405",
                    "contexts": None,
                    "default_permission": True,
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "show",
                    "description": "Shows the job view based on job id.",
                    "dm_permission": True,
                    "options": [
                        {"name": "prompt", "description": "The prompt to shorten.", "type": 3, "required": True}
                    ]
                },
                "attachments": []
            }
        }

        err = self.req_midjourney(request_body)
        return err
