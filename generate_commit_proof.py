import subprocess
import base64
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# ----------------------------------------------------
# 1. Get latest commit hash (40 chars)
# ----------------------------------------------------
commit_hash = subprocess.check_output(
    ["git", "log", "-1", "--format=%H"]
).decode().strip()

print("\nCommit Hash:")
print(commit_hash)

# ----------------------------------------------------
# 2. Load student private key (PEM)
# ----------------------------------------------------
with open("student_private.pem", "rb") as f:
    private_key = load_pem_private_key(f.read(), password=None)

# ----------------------------------------------------
# 3. Sign commit hash (RSA-PSS-SHA256)
# ----------------------------------------------------
signature = private_key.sign(
    commit_hash.encode("utf-8"),
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH,
    ),
    hashes.SHA256(),
)

# ----------------------------------------------------
# 4. Load instructor public key
# ----------------------------------------------------
with open("instructor_public.pem", "rb") as f:
    instructor_pub = load_pem_public_key(f.read())

# ----------------------------------------------------
# 5. Encrypt signature (RSA-OAEP-SHA256)
# ----------------------------------------------------
encrypted_signature = instructor_pub.encrypt(
    signature,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)

# ----------------------------------------------------
# 6. Base64 encode output
# ----------------------------------------------------
encoded = base64.b64encode(encrypted_signature).decode()

print("\nEncrypted Signature (Base64):")
print(encoded)
print("\n--- DONE ---")
