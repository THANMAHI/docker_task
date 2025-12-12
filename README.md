# docker_task
PKI 2FA Verification System
Overview

This project implements a full Public-Key-Infrastructure-based 2FA verification system using RSA-OAEP decryption and TOTP generation.

The system provides:

RSA key pair generation

Instructor-encrypted seed decryption

TOTP code generation (SHA-1, 30s)

API endpoints for seed decryption, code generation, and verification

Dockerized runtime environment

Cron-based TOTP logging

app.py                    # API server (FastAPI)
decrypt_seed.py           # RSA decryption logic
totp_utils.py             # TOTP generation utilities
scripts/log_2fa_cron.py   # Cron script
cron/2fa-cron             # Cron schedule
student_private.pem       # Student private key
student_public.pem        # Student public key
instructor_public.pem     # Instructor public key
Dockerfile                # Multi-stage build
docker-compose.yml        # Runtime configuration
requirements.txt          # Python dependencies
.gitattributes            # Ensure LF for cron file

Endpoints
POST /decrypt-seed

Decrypts encrypted seed and stores hex seed to /data/seed.txt.

GET /generate-2fa

Returns current TOTP code + seconds remaining.

POST /verify-2fa

Verifies TOTP code with ±1 time window.