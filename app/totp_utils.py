import base64
import time
import hmac
import hashlib
import struct

def hex_to_base32(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")
    return base32_seed


def _hotp(key: bytes, counter: int, digits: int = 6) -> str:
    msg = struct.pack(">Q", counter)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[-1] & 0x0F
    code = (struct.unpack(">I", h[o:o+4])[0] & 0x7FFFFFFF) % (10 ** digits)
    return str(code).zfill(digits)


def generate_totp(hex_seed: str, digits: int = 6, period: int = 30) -> str:
    base32_seed = hex_to_base32(hex_seed)
    key = base64.b32decode(base32_seed)
    timestep = int(time.time()) // period
    return _hotp(key, timestep, digits)


def verify_totp(hex_seed: str, code: str, window: int = 1, digits: int = 6, period: int = 30) -> bool:
    base32_seed = hex_to_base32(hex_seed)
    key = base64.b32decode(base32_seed)
    current_step = int(time.time()) // period
    for offset in range(-window, window + 1):
        if _hotp(key, current_step + offset, digits) == code:
            return True
    return False
