from my_discord import SelfBot, get_all_discord

discord_list = get_all_discord()
for discord in discord_list:
    self_bot = SelfBot(discord["channelId"], discord["userToken"])
    self_bot.run_discord_bot(discord["id"])
