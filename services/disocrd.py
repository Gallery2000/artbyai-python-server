import json
import os
import re

import requests

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


def req_midjourney(data, token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": token,
    }
    print(json.dumps(data))
    try:
        response = requests.post(INTERACTIONS_URL, json=data, headers=headers)
        response.raise_for_status()
        if response.text:
            data = response.json()  # 解析JSON数据
        else:
            data = {}  # 响应为空，使用空字典表示空数据
        print(data)
        return response.content, None
    except requests.exceptions.RequestException as e:
        return None, e
    except json.JSONDecodeError as e:
        return None, e


class DiscordService:
    def generate_image(self, params):
        request_body = {
            "type": 2,
            "guild_id": params["guildId"],
            "channel_id": params["channelId"],
            "application_id": APPLICATION_ID,
            "session_id": params["sessionId"],
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

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def prefer_remix(self, params):
        request_body = {
            "type": 2,
            "guild_id": params["guildId"],
            "channel_id": params["channelId"],
            "application_id": APPLICATION_ID,
            "session_id": params["sessionId"],
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

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def ask_question(self, params):
        request_body = {
            "type": 2,
            "guild_id": params["guildId"],
            "channel_id": params["channelId"],
            "application_id": APPLICATION_ID,
            "session_id": params["sessionId"],
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

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def view_information(self, params):
        request_body = {
            "type": 2,
            "guild_id": params["guildId"],
            "channel_id": params["channelId"],
            "application_id": APPLICATION_ID,
            "session_id": params["sessionId"],
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

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def switch_to_fast_mode(self, params):
        request_body = {
            "type": 2,
            "guild_id": params["guildId"],
            "channel_id": params["channelId"],
            "application_id": APPLICATION_ID,
            "session_id": params["sessionId"],
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

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def switch_to_relax_mode(self, params):
        request_body = {
            "type": 2,
            "guild_id": params["guildId"],
            "channel_id": params["channelId"],
            "application_id": APPLICATION_ID,
            "session_id": params["sessionId"],
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

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def image_variation(self, params):
        request_body = {
            "type": 3,
            "guild_id": params["guildId"],
            "channel_id": params["channelId"],
            "message_flags": params["msgFlags"],
            "message_id": params["discordMsgId"],
            "application_id": APPLICATION_ID,
            "session_id": params["sessionId"],
            "nonce": params["nonce"],
            "data": {
                "component_type": 2,
                "custom_id": params["customId"]
            }
        }

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def describe_image(self, params):
        filename = os.path.basename(params["prompt"])
        upload_filename = params["prompt"]

        request_body = {
            "type": 2,
            "guild_id": params["guildId"],
            "channel_id": params["channelId"],
            "application_id": APPLICATION_ID,
            "session_id": params["sessionId"],
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
                    "default_permission": True,
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
                    "uploadFilename": upload_filename
                }]
            }
        }

        _, err = req_midjourney(request_body, params["userToken"])
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
        if params["prompt"]:
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
        for i, upload_name in enumerate(params["uploadNames"]):
            filename = os.path.basename(upload_name)
            attachments.append({
                "id": str(i + 1),
                "filename": filename,
                "uploadFilename": upload_name,
            })

        request_body = {
            "type": 2,
            "guild_id": params["guildId"],
            "channel_id": params["channelId"],
            "application_id": APPLICATION_ID,
            "session_id": params["sessionId"],
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

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def image_remix(self, params):

        data_custom_id = ""
        com_custom_id = ""

        if "CustomZoom" in params["customId"]:
            data_custom_id = f"MJ::OutpaintCustomZoomModal::{params['msgHash']}"
            com_custom_id = "MJ::OutpaintCustomZoomModal::prompt"
        elif "Variation" in params["customId"]:
            match = re.search(r"variation::(\d)", params["customId"])
            if match:
                vary = match.group(1)
                data_custom_id = f"MJ::RemixModal::{params['msgHash']}::{vary}::1"
            else:
                data_custom_id, com_custom_id = get_data_custom(params)
        elif "Pan" in params["customId"]:
            re_match = re.search(r"pan_(\w+)", params["customId"])
            if re_match:
                direction = re_match.group(1)
                data_custom_id = f"MJ::PanModal::{direction}::{params['msgHash']}"
                com_custom_id = "MJ::PanModal::prompt"
        elif "PromptAnalyzer" in params["customId"]:
            data_custom_id = f"MJ::ImagineModal::{params['discordMsgId']}"
            com_custom_id = "MJ::ImagineModal::new_prompt"
        elif "PicReader" in params["customId"]:
            re_match = re.search(r"MJ::Job::PicReader::(\d)", params["customId"])
            if re_match:
                pic_reader_id = re_match.group(1)
                data_custom_id = f"MJ::Picreader::Modal::{pic_reader_id}"
                com_custom_id = "MJ::Picreader::Modal::PromptField"
        elif "ReRoll" in params["customId"]:
            data_custom_id, com_custom_id = get_data_custom(params)
        else:
            vary = 1
            if "LowVariation" in params["customId"]:
                vary = 0
            data_custom_id = f"MJ::RemixModal::{params['msgHash']}::1::{vary}"
            com_custom_id = "MJ::RemixModal::new_prompt"

        print("data_custom_id: " + data_custom_id)
        print("com_custom_id: " + com_custom_id)

        request_body = {
            "type": 5,
            "guild_id": params["guildId"],
            "channel_id": params["channelId"],
            "application_id": APPLICATION_ID,
            "session_id": params["sessionId"],
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

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def shorten_prompt(self, params):
        request_body = {
            "type": 2,
            "guild_id": params["guildId"],
            "channel_id": params["channelId"],
            "application_id": APPLICATION_ID,
            "session_id": params["sessionId"],
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

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def show_image(self, params):
        request_body = {
            "type": 2,
            "guild_id": params["guildId"],
            "channel_id": params["channelId"],
            "application_id": APPLICATION_ID,
            "session_id": params["sessionId"],
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

        _, err = req_midjourney(request_body, params["userToken"])
        return err
