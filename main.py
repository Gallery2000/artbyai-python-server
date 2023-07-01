from my_discord import SelfBot, get_all_discord

discord_list = get_all_discord()
for discord_data in discord_list:
    self_bot = SelfBot(discord_data["channelId"])
    self_bot.run(discord_data["userToken"])
