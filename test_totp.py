from totp_utils import generate_totp_code, verify_totp_code

with open("seed.txt", "r") as f:
    seed_hex = f.read().strip()

code = generate_totp_code(seed_hex)
print("TOTP Code:", code)

print("Verification:", verify_totp_code(seed_hex, code))
