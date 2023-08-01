import base64
import datetime
import hashlib
import hmac

DISCORD_EPOCH = 1420070400000


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def time_snowflake(dt: datetime.datetime, /, *, high: bool = False) -> int:
    discord_millis = int(dt.timestamp() * 1000 - DISCORD_EPOCH)
    return (discord_millis << 22) + (2 ** 22 - 1 if high else 0)


def generate_nonce() -> str:
    return str(time_snowflake(utcnow()))


def verify_hmac_signature(data, signature, secret_key):
    key = bytes(secret_key, "utf-8")
    signature_calculated = hmac.new(key, data.encode("utf-8"), hashlib.sha256).digest()
    signature_calculated_base64 = base64.b64encode(signature_calculated).decode("utf-8")
    return hmac.compare_digest(signature, signature_calculated_base64)
