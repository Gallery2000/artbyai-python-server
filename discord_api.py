import requests
from loguru import logger


class DiscordApi:
    def __init__(self, base_url):
        self.base_url = base_url

    def callback_discord(self, discord_id: int, data: dict) -> None:
        try:
            response = requests.post(self.base_url + "/callback/discord", json=data)
            response.raise_for_status()
            res = response.json()
            if res["code"] == 0:
                logger.info("Callback Discord " + str(discord_id) + " success")
            else:
                logger.error("Callback Discord " + str(discord_id) + " error: " + res["msg"])
        except requests.HTTPError as e:
            logger.error("Callback Discord " + str(discord_id) + " error: " + str(e))

    def update_discord_ssid(self, discord_id: int, session_id: str) -> None:
        try:
            response = requests.patch(self.base_url + "/manage/updateManDiscordSSID", json={
                "id": discord_id,
                "sessionId": session_id
            })
            response.raise_for_status()
            res = response.json()
            if res["code"] == 0:
                logger.info("Update Discord " + str(discord_id) + " SSID success")
            else:
                logger.error("Update Discord " + str(discord_id) + " SSID error: %s", res["msg"])
        except requests.HTTPError as e:
            logger.error("Update Discord SSID " + str(discord_id) + " error: %s", str(e))

    def get_discord(self, discord_id: int) -> dict:
        try:
            response = requests.get(self.base_url + "/manage/getManDiscord", params={
                "id": discord_id
            })
            response.raise_for_status()
            res = response.json()
            if res["code"] == 0:
                logger.info("Get Discord " + str(discord_id) + " success")
                return res["data"]
            else:
                logger.error("Get Discord " + str(discord_id) + " error: " + res["msg"])
        except requests.HTTPError as e:
            logger.error("Get Discord " + str(discord_id) + " error: " + str(e))
