import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from decrypt_seed import load_private_key, decrypt_seed
from totp_utils import generate_totp_code, verify_totp_code

app = FastAPI()

DATA_DIR = "/data"
SEED_FILE = f"{DATA_DIR}/seed.txt"


# ------------------------------
# Request Models
# ------------------------------

class EncryptedSeedRequest(BaseModel):
    encrypted_seed: str


class VerifyCodeRequest(BaseModel):
    code: str


# ------------------------------
# Helpers
# ------------------------------

def read_seed():
    if not os.path.exists(SEED_FILE):
        return None
    with open(SEED_FILE, "r") as f:
        return f.read().strip()


def save_seed(seed_hex: str):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SEED_FILE, "w") as f:
        f.write(seed_hex)


# ------------------------------
# Endpoint 1: POST /decrypt-seed
# ------------------------------

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(body: EncryptedSeedRequest):
    encrypted_seed = body.encrypted_seed

    try:
        private_key = load_private_key()
        seed_hex = decrypt_seed(encrypted_seed, private_key)
        save_seed(seed_hex)
        return {"status": "ok"}

    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")


# ------------------------------
# Endpoint 2: GET /generate-2fa
# ------------------------------

@app.get("/generate-2fa")
def generate_2fa():
    seed_hex = read_seed()

    if seed_hex is None:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    # Generate TOTP code
    code = generate_totp_code(seed_hex)

    # Calculate seconds remaining in current TOTP period (0–29)
    current_time = int(time.time())
    valid_for = 30 - (current_time % 30)

    return {"code": code, "valid_for": valid_for}


# ------------------------------
# Endpoint 3: POST /verify-2fa
# ------------------------------

@app.post("/verify-2fa")
def verify_2fa(body: VerifyCodeRequest):
    if not body.code:
        raise HTTPException(status_code=400, detail="Missing code")

    seed_hex = read_seed()
    if seed_hex is None:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    # Verify with ±1 time window
    is_valid = verify_totp_code(seed_hex, body.code)

    return {"valid": is_valid}


# ------------------------------
# Optional: Basic health check
# ------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}
