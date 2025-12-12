from fastapi import FastAPI
from pydantic import BaseModel
import os

from app.crypto_utils import decrypt_seed, load_private_key
from app.totp_utils import generate_totp, verify_totp

app = FastAPI()

class SeedRequest(BaseModel):
    encrypted_seed: str

class TOTPVerifyRequest(BaseModel):
    code: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(req: SeedRequest):
    try:
        private_key = load_private_key()   # ← LOAD KEY HERE
        seed = decrypt_seed(req.encrypted_seed, private_key)

        os.makedirs("/data", exist_ok=True)
        with open("/data/seed.txt", "w") as f:
            f.write(seed)

        return {"status": "success", "seed": seed}
    except Exception as e:
        return {"error": str(e)}

@app.get("/generate-2fa")
def generate_2fa():
    try:
        with open("/data/seed.txt", "r") as f:
            seed = f.read().strip()

        code = generate_totp(seed)
        return {"code": code}
    except:
        return {"error": "Seed not found"}

@app.post("/verify-2fa")
def verify_2fa(req: TOTPVerifyRequest):
    try:
        with open("/data/seed.txt", "r") as f:
            seed = f.read().strip()

        valid = verify_totp(seed, req.code)
        return {"valid": valid}
    except:
        return {"error": "Seed not found"}
