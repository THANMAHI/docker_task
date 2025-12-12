#!/usr/bin/env python3
import os
from datetime import datetime, timezone
from totp_utils import generate_totp

DATA_PATH = "/data/seed.txt"
LOG_PATH = "/cron/last_code.txt"

def main():
    try:
        if not os.path.exists(DATA_PATH):
            print("No seed yet, skipping", flush=True)
            return

        with open(DATA_PATH, "r") as f:
            hex_seed = f.read().strip()

        code = generate_totp(hex_seed)
        now = datetime.now(timezone.utc)
        ts = now.strftime("%Y-%m-%d %H:%M:%S")

        # Append the line
        with open(LOG_PATH, "a") as logf:
            logf.write(f"{ts} - 2FA Code: {code}\n")

    except Exception as e:
        # Cron captures stdout/stderr; write a short message to stderr to help debugging.
        print(f"Error in cron job: {e}", flush=True)

if __name__ == "__main__":
    main()
