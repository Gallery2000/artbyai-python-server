import os
import re

import requests

APPLICATION_ID = "936929561302675456"

REMIX_TYPE = "Remix by"
VARIATIONS_TYPE = "Variations by"
ZOOM_OUT_TYPE = "Zoom Out by"
PAN_LEFT_TYPE = "Pan Left by"
PAN_RIGHT_TYPE = "Pan Right by"
PAN_DOWN_TYPE = "Pan Down by"
PAN_UP_TYPE = "Pan Up by"


def req_midJourney(data, uri, token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": token,
    }

    try:
        response = requests.post(uri, json=data, headers=headers)
        res = response.json()
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return None, e

    if res.get("message"):
        if res.get("errors") and res["errors"]["data"]["errors"]:
            return None, Exception(res["errors"]["data"]["errors"][0]["message"])
        return None, Exception(res["message"])

    return res, None


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


def req_midjourney(data, token, channel_id):
    headers = {
        "Content-Type": "application/json",
        "Authorization": token,
    }

    uri = f"https://discord.com/api/v9/channels/{channel_id}/messages"

    try:
        response = requests.post(uri, json=data, headers=headers)
        response.raise_for_status()
        res = response.json()
        if res["Message"] != "":
            if res["Errors"]["Data"]["Errors"] is not None:
                raise Exception(res["Errors"]["Data"]["Errors"][0]["Message"])
            raise Exception(res["Message"])
        return response.content, None
    except requests.exceptions.RequestException as e:
        return None, e


class DiscordService:
    def generate_image(self, params):
        request_body = {
            "Type": 2,
            "GuildID": params["guildId"],
            "ChannelID": params["channelId"],
            "ApplicationId": APPLICATION_ID,
            "SessionId": params["sessionId"],
            "Nonce": params["nonce"],
            "Data": {
                "Version": "1118961510123847772",
                "Id": "938956540159881230",
                "Name": "imagine",
                "Type": 1,
                "Options": [{"Type": 3, "Name": "prompt", "Value": params["prompt"]}],
                "ApplicationCommand": {
                    "Id": "938956540159881230",
                    "ApplicationId": APPLICATION_ID,
                    "Version": "1118961510123847772",
                    "Contexts": [1, 2, 3],
                    "DefaultPermission": True,
                    "DefaultMemberPermissions": None,
                    "Type": 1,
                    "Nsfw": False,
                    "Name": "imagine",
                    "Description": "Create images with Midjourney",
                    "DmPermission": True,
                    "Options": [
                        {"Type": 3, "Name": "prompt", "Description": "The prompt to imagine", "Required": True}],
                },
                "Attachments": [],
            }
        }

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def prefer_remix(self, params):
        request_body = {
            "Type": 2,
            "GuildID": params["guildId"],
            "ChannelID": params["channelId"],
            "ApplicationId": APPLICATION_ID,
            "SessionId": params["sessionId"],
            "Nonce": params["nonce"],
            "Data": {
                "Version": "1121575372539039776",
                "Id": "984273800587776053",
                "Name": "prefer",
                "Type": 1,
                "Options": [{"Type": 1, "Name": "remix", "Options": []}],
                "ApplicationCommand": {
                    "Id": "938956540159881230",
                    "ApplicationId": APPLICATION_ID,
                    "Version": "1118961510123847772",
                    "Contexts": [1, 2, 3],
                    "DefaultPermission": True,
                    "DefaultMemberPermissions": None,
                    "Type": 1,
                    "Nsfw": False,
                    "Name": "prefer",
                    "Description": "...",
                    "DmPermission": True,
                    "Options": [
                        {"Type": 2, "Name": "option", "Description": "...", "Options": [
                            {"Type": 1, "Name": "set", "Description": "Set a custom option.", "Options": [
                                {"Type": 3, "Name": "option", "Description": "..."},
                                {"Type": 3, "Name": "value", "Description": "..."}
                            ]},
                            {"Type": 1, "Name": "list", "Description": "View your current custom options.",
                             "Options": []}
                        ]},
                        {"Type": 1, "Name": "auto_dm",
                         "Description": "Whether or not to automatically send job results to your DMs."},
                        {"Type": 1, "Name": "suffix",
                         "Description": "Suffix to automatically add to the end of every prompt. Leave empty to remove.",
                         "Options": [
                             {"Type": 3, "Name": "new_value", "Description": "..."}
                         ]},
                        {"Type": 1, "Name": "remix", "Description": "Toggle remix mode."},
                        {"Type": 1, "Name": "variability", "Description": "Toggle variability mode."}
                    ],
                },
                "Attachments": []
            }
        }

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def ask_question(self, params):
        request_body = {
            "Type": 2,
            "GuildID": params["guildId"],
            "ChannelID": params["channelId"],
            "ApplicationId": APPLICATION_ID,
            "SessionId": params["sessionId"],
            "Nonce": params["nonce"],
            "Data": {
                "Version": "1118961510123847771",
                "Id": "994261739745050684",
                "Name": "ask",
                "Type": 1,
                "Options": [{"Type": 3, "Name": "question", "Value": params["prompt"]}],
                "ApplicationCommand": {
                    "Id": "994261739745050684",
                    "ApplicationId": APPLICATION_ID,
                    "Version": "1118961510123847771",
                    "Contexts": [0, 1, 2],
                    "DefaultMemberPermissions": None,
                    "Type": 1,
                    "Nsfw": False,
                    "Name": "ask",
                    "Description": "Get an answer to a question.",
                    "DmPermission": True,
                    "Options": [
                        {"Type": 3, "Name": "question", "Description": "What is the question?", "Required": True}],
                },
                "Attachments": []
            }
        }

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def view_information(self, params):
        request_body = {
            "Type": 2,
            "GuildID": params["guildId"],
            "ChannelID": params["channelId"],
            "ApplicationId": APPLICATION_ID,
            "SessionId": params["sessionId"],
            "Nonce": params["nonce"],
            "Data": {
                "Version": "1118961510123847776",
                "Id": "972289487818334209",
                "Name": "info",
                "Type": 1,
                "Options": [],
                "ApplicationCommand": {
                    "Id": "972289487818334209",
                    "ApplicationId": APPLICATION_ID,
                    "Version": "1118961510123847776",
                    "Contexts": None,
                    "DefaultMemberPermissions": None,
                    "Type": 1,
                    "Nsfw": False,
                    "Name": "info",
                    "Description": "View information about your profile.",
                    "DmPermission": True,
                },
                "Attachments": []
            }
        }

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def switch_to_fast_mode(self, params):
        request_body = {
            "Type": 2,
            "GuildID": params["guildId"],
            "ChannelID": params["channelId"],
            "ApplicationId": APPLICATION_ID,
            "SessionId": params["sessionId"],
            "Nonce": params["nonce"],
            "Data": {
                "Version": "987795926183731231",
                "Id": "972289487818334212",
                "Name": "fast",
                "Type": 1,
                "Options": [],
                "ApplicationCommand": {
                    "Id": "972289487818334209",
                    "ApplicationId": APPLICATION_ID,
                    "Version": "987795926183731231",
                    "Contexts": None,
                    "DefaultMemberPermissions": None,
                    "Type": 1,
                    "Nsfw": False,
                    "Name": "fast",
                    "Description": "Switch to fast mode",
                    "DmPermission": True,
                },
                "Attachments": []
            }
        }

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def switch_to_relax_mode(self, params):
        request_body = {
            "Type": 2,
            "GuildID": params["guildId"],
            "ChannelID": params["channelId"],
            "ApplicationId": APPLICATION_ID,
            "SessionId": params["sessionId"],
            "Nonce": params["nonce"],
            "Data": {
                "Version": "987795926183731232",
                "Id": "972289487818334213",
                "Name": "relax",
                "Type": 1,
                "Options": [],
                "ApplicationCommand": {
                    "Id": "972289487818334213",
                    "ApplicationId": APPLICATION_ID,
                    "Version": "987795926183731232",
                    "Contexts": None,
                    "DefaultMemberPermissions": None,
                    "Type": 1,
                    "Nsfw": False,
                    "Name": "relax",
                    "Description": "Switch to relax mode",
                    "DmPermission": True
                },
                "Attachments": []
            }
        }

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def image_variation(self, params):
        request_body = {
            "Type": 3,
            "GuildId": params["guildId"],
            "ChannelId": params["channelId"],
            "MessageFlags": params["msgFlags"],
            "MessageId": params["discordMsgId"],
            "ApplicationId": APPLICATION_ID,
            "SessionId": params["sessionId"],
            "Nonce": params["nonce"],
            "Data": {
                "ComponentType": 2,
                "CustomId": params["customId"],
            }
        }

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def describe_image(self, params):
        filename = os.path.basename(params["prompt"])
        upload_filename = params["prompt"]

        request_body = {
            "Type": 2,
            "GuildID": params["guildId"],
            "ChannelID": params["channelId"],
            "ApplicationId": APPLICATION_ID,
            "SessionId": params["sessionId"],
            "Nonce": params["nonce"],
            "Data": {
                "Version": "1118961510123847774",
                "Id": "1092492867185950852",
                "Name": "describe",
                "Type": 1,
                "Options": [{"Type": 11, "Name": "image", "Value": 0}],
                "ApplicationCommand": {
                    "Id": "1092492867185950852",
                    "ApplicationId": APPLICATION_ID,
                    "Version": "1118961510123847774",
                    "DefaultPermission": True,
                    "DefaultMemberPermissions": None,
                    "Type": 1,
                    "Nsfw": False,
                    "Name": "describe",
                    "Description": "Writes a prompt based on your image.",
                    "DmPermission": True,
                    "Options": [
                        {"Type": 11, "Name": "image", "Description": "The image to describe", "Required": True}],
                },
                "Attachments": [{
                    "Id": "0",
                    "Filename": filename,
                    "UploadFilename": upload_filename,
                }]
            }
        }

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def blend_images(self, params):
        options = []
        for i, upload_name in enumerate(params["uploadNames"]):
            options.append({
                "Type": 11,
                "Name": f"image{i + 1}",
                "Value": i + 1,
            })

        choices = [
            {"Name": "Portrait", "Value": "--ar 2:3"},
            {"Name": "Square", "Value": "--ar 1:1"},
            {"Name": "Landscape", "Value": "--ar 3:2"},
        ]
        order_map = ["First", "Second", "Third", "Fourth", "Fifth"]
        command_options = []
        for i in range(len(params["uploadNames"])):
            command_options.append({
                "Description": f"{order_map[i]} image to add to the blend",
                "Name": f"image{i + 1}",
                "Required": True,
                "Type": 11,
            })
        if params["prompt"]:
            options.append({
                "Type": 3,
                "Name": "dimensions",
                "Value": params["prompt"],
            })
        command_options.append({
            "Choices": choices,
            "Description": "The dimensions of the image. If not specified, the image will be square.",
            "Name": "dimensions",
            "Type": 3,
        })
        for i in range(len(command_options), 5):
            command_options.append({
                "Description": f"{order_map[i]} image to add to the blend (optional)",
                "Name": f"image{i + 1}",
                "Type": 11,
            })

        attachments = []
        for i, upload_name in enumerate(params["uploadNames"]):
            filename = os.path.basename(upload_name)
            attachments.append({
                "Id": str(i + 1),
                "Filename": filename,
                "UploadFilename": upload_name,
            })

        request_body = {
            "Type": 2,
            "GuildID": params["guildId"],
            "ChannelID": params["channelId"],
            "ApplicationId": APPLICATION_ID,
            "SessionId": params["sessionId"],
            "Nonce": params["nonce"],
            "Data": {
                "Version": "1118961510123847773",
                "Id": "1062880104792997970",
                "Name": "blend",
                "Type": 1,
                "Options": options,
                "ApplicationCommand": {
                    "Id": "1062880104792997970",
                    "ApplicationId": APPLICATION_ID,
                    "Version": "1118961510123847773",
                    "Contexts": [1, 2, 3],
                    "DefaultPermission": True,
                    "DefaultMemberPermissions": None,
                    "Type": 1,
                    "Nsfw": False,
                    "Name": "blend",
                    "Description": "Blend images together seamlessly!",
                    "DmPermission": True,
                    "Options": command_options,
                },
                "Attachments": attachments,
            },
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
            "Type": 5,
            "GuildID": params["guildId"],
            "ChannelID": params["channelId"],
            "ApplicationId": APPLICATION_ID,
            "SessionId": params["sessionId"],
            "Nonce": params["nonce"],
            "Data": {
                "Id": params["dataId"],
                "CustomId": data_custom_id,
                "Components": [{
                    "Type": 1,
                    "Components": [{
                        "CustomId": com_custom_id,
                        "Type": 4,
                        "Value": params["prompt"],
                    }],
                }],
            },
        }

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def shorten_prompt(self, params):
        request_body = {
            "Type": 2,
            "GuildID": params["guildId"],
            "ChannelID": params["channelId"],
            "ApplicationId": APPLICATION_ID,
            "SessionId": params["sessionId"],
            "Nonce": params["nonce"],
            "Data": {
                "Version": "1121575372539039775",
                "Id": "1121575372539039774",
                "Name": "shorten",
                "Type": 1,
                "Options": [{"Name": "prompt", "Type": 3, "Value": params["prompt"]}],
                "ApplicationCommand": {
                    "Id": "1121575372539039774",
                    "ApplicationId": APPLICATION_ID,
                    "Version": "1121575372539039775",
                    "Contexts": None,
                    "DefaultPermission": True,
                    "DefaultMemberPermissions": None,
                    "Type": 1,
                    "Nsfw": False,
                    "Name": "shorten",
                    "Description": "Analyzes and shortens a prompt.",
                    "DmPermission": True,
                    "Options": [
                        {"Name": "prompt", "Description": "The prompt to shorten.", "Type": 3, "Required": True}],
                },
                "Attachments": [],
            },
        }

        _, err = req_midjourney(request_body, params["userToken"])
        return err

    def show_image(self, params):
        request_body = {
            "Type": 2,
            "GuildID": params["guildId"],
            "ChannelID": params["channelId"],
            "ApplicationId": APPLICATION_ID,
            "SessionId": params["sessionId"],
            "Nonce": params["nonce"],
            "Data": {
                "Version": "990020489659449405",
                "Id": "990020489659449404",
                "Name": "show",
                "Type": 1,
                "Options": [{"Name": "job_id", "Type": 3, "Value": params["prompt"]}],
                "ApplicationCommand": {
                    "Id": "990020489659449404",
                    "ApplicationId": APPLICATION_ID,
                    "Version": "990020489659449405",
                    "Contexts": None,
                    "DefaultPermission": True,
                    "DefaultMemberPermissions": None,
                    "Type": 1,
                    "Nsfw": False,
                    "Name": "show",
                    "Description": "Shows the job view based on job id.",
                    "DmPermission": True,
                    "Options": [
                        {"Name": "prompt", "Description": "The prompt to shorten.", "Type": 3, "Required": True}],
                },
                "Attachments": [],
            },
        }

        _, err = req_midjourney(request_body, params["userToken"])
        return err
