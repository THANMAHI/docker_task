import base64
import pyotp

def hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-char hex seed to Base32 encoding.
    Required for TOTP libraries.
    """
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")
    return base32_seed


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current TOTP code from a 64-character hex seed.
    SHA-1, 30 sec, 6 digits (default settings)
    """
    # 1. Convert hex -> bytes -> base32
    base32_seed = hex_to_base32(hex_seed)

    # 2. Create TOTP object with default settings
    totp = pyotp.TOTP(base32_seed)  # SHA-1, 30s, 6 digits (default)

    # 3. Generate current TOTP code
    code = totp.now()

    # 4. Return 6-digit code
    return code


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with ±1 period window tolerance.
    """
    # 1. Convert hex -> base32
    base32_seed = hex_to_base32(hex_seed)

    # 2. Create TOTP object
    totp = pyotp.TOTP(base32_seed)

    # 3. Verify with ±1 window (±30 seconds)
    return totp.verify(code, valid_window=valid_window)
