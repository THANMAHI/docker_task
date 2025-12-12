from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import time
import base64

from crypto_utils import load_private_key, decrypt_seed
from totp_utils import generate_totp, verify_totp

app = FastAPI()

DATA_PATH = "/data/seed.txt"

class SeedRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/decrypt-seed")
def decrypt_seed_api(req: SeedRequest):
    private_key = load_private_key()

    try:
        hex_seed = decrypt_seed(req.encrypted_seed, private_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Decryption failed")

    # Save seed to persistent storage
    os.makedirs("/data", exist_ok=True)
    with open(DATA_PATH, "w") as f:
        f.write(hex_seed)

    return {"status": "ok"}


@app.get("/generate-2fa")
def generate():
    if not os.path.exists(DATA_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(DATA_PATH, "r") as f:
        hex_seed = f.read().strip()

    code = generate_totp(hex_seed)

    remaining = 30 - (int(time.time()) % 30)

    return {"code": code, "valid_for": remaining}


@app.post("/verify-2fa")
def verify(req: VerifyRequest):
    if not req.code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not os.path.exists(DATA_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(DATA_PATH, "r") as f:
        hex_seed = f.read().strip()

    is_valid = verify_totp(hex_seed, req.code)

    return {"valid": is_valid}
