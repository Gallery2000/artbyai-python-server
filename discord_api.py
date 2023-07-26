import requests
from loguru import logger

TIME_OUT_SECONDS = 10


class DiscordApi:
    def __init__(self, base_url):
        self.base_url = base_url

    def trigger_time(self, discord_id: int) -> None:
        try:
            response = requests.post(self.base_url + "/manage/updateTriggerTime", json={
                "id": discord_id,
            }, timeout=TIME_OUT_SECONDS)
            response.raise_for_status()
            res = response.json()
            if res["code"] == 0:
                logger.info("Trigger Discord " + str(discord_id) + " success")
            else:
                logger.error("Trigger Discord " + str(discord_id) + " error: " + res["msg"])
        except requests.HTTPError as e:
            logger.error("Trigger Discord " + str(discord_id) + " error: " + str(e))
        except requests.exceptions.RequestException as e:
            print("Error during request:" + str(e))
        except Exception as e:
            logger.error("Trigger Discord " + str(discord_id) + " error: " + str(e))

    def callback_discord(self, discord_id: int, data: dict) -> None:
        try:
            response = requests.post(self.base_url + "/callback/discord", json=data, timeout=TIME_OUT_SECONDS)
            response.raise_for_status()
            res = response.json()
            if res["code"] == 0:
                logger.info("Callback Discord " + str(discord_id) + " success")
            else:
                logger.error("Callback Discord " + str(discord_id) + " error: " + res["msg"])
        except requests.HTTPError as e:
            logger.error("Callback Discord " + str(discord_id) + " error: " + str(e))
        except requests.exceptions.RequestException as e:
            print("Error during request:" + str(e))
        except Exception as e:
            logger.error("Callback Discord " + str(discord_id) + " error: " + str(e))

    def update_discord_ssid(self, discord_id: int, session_id: str) -> None:
        try:
            response = requests.post(self.base_url + "/manage/updateManDiscordSSID", json={
                "id": discord_id,
                "sessionId": session_id
            }, timeout=TIME_OUT_SECONDS)
            response.raise_for_status()
            res = response.json()
            if res["code"] == 0:
                logger.info("Update Discord " + str(discord_id) + " SSID success")
            else:
                logger.error("Update Discord " + str(discord_id) + " SSID error: " + res["msg"])
        except requests.HTTPError as e:
            logger.error("Update Discord SSID " + str(discord_id) + " error: " + str(e))
        except requests.exceptions.RequestException as e:
            print("Error during request:" + str(e))
        except Exception as e:
            logger.error("Callback Discord " + str(discord_id) + " error: " + str(e))

    def get_discord(self, discord_id: int) -> dict:
        try:
            response = requests.get(self.base_url + "/manage/getManDiscord", params={
                "id": discord_id
            }, timeout=TIME_OUT_SECONDS)
            response.raise_for_status()
            res = response.json()
            if res["code"] == 0:
                logger.info("Get Discord " + str(discord_id) + " success")
                return res["data"]
            else:
                logger.error("Get Discord " + str(discord_id) + " error: " + res["msg"])
        except requests.HTTPError as e:
            logger.error("Get Discord " + str(discord_id) + " error: " + str(e))
        except requests.exceptions.RequestException as e:
            print("Error during request:" + str(e))
        except Exception as e:
            logger.error("Callback Discord " + str(discord_id) + " error: " + str(e))
