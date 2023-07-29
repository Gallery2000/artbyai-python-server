import datetime

DISCORD_EPOCH = 1420070400000


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def time_snowflake(dt: datetime.datetime, /, *, high: bool = False) -> int:
    discord_millis = int(dt.timestamp() * 1000 - DISCORD_EPOCH)
    return (discord_millis << 22) + (2 ** 22 - 1 if high else 0)


def generate_nonce() -> str:
    return str(time_snowflake(utcnow()))
