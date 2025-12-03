#!/usr/bin/env python3
import os
import datetime
from app.totp_utils import generate_totp_code


SEED_PATH = "/data/seed.txt"

def read_seed():
    if not os.path.exists(SEED_PATH):
        print("Seed file not found")
        return None
    with open(SEED_PATH, "r") as f:
        return f.read().strip()

def main():
    seed = read_seed()
    if not seed:
        print("No seed available")
        return

    # Generate TOTP code
    code = generate_totp_code(seed)

    # UTC timestamp
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Output format
    print(f"{now} - 2FA Code: {code}")

if __name__ == "__main__":
    main()
