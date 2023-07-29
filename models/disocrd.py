class Discord:
    def __init__(self, user_token: str, session_id: str, channel_id: str, guild_id: str, dm_channel_id: str):
        self.user_token = user_token
        self.session_id = session_id
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.dm_channel_id = dm_channel_id
