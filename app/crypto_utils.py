import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

def load_private_key():
    """
    Load student private key from student_private.pem
    """
    with open("student_private.pem", "rb") as f:
        key_data = f.read()

    private_key = serialization.load_pem_private_key(
        key_data,
        password=None
    )
    return private_key


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP
    
    Returns:
        64-character hex string
    """

    # 1. Base64 decode the encrypted seed
    try:
        encrypted_bytes = base64.b64decode(encrypted_seed_b64)
    except Exception:
        raise ValueError("Invalid base64 in encrypted seed")

    # 2. RSA OAEP decryption with SHA-256 and MGF1(SHA-256)
    try:
        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception:
        raise ValueError("RSA decryption failed")

    # 3. Convert decrypted bytes to UTF-8 string
    hex_seed = decrypted_bytes.decode("utf-8").strip()

    # 4. Validate 64-character hex seed
    if len(hex_seed) != 64:
        raise ValueError("Seed length invalid (must be 64 hex characters)")

    for ch in hex_seed:
        if ch not in "0123456789abcdef":
            raise ValueError("Seed contains non-hex characters")

    return hex_seed


if __name__ == "__main__":
    # Read encrypted seed
    with open("encrypted_seed.txt", "r") as f:
        encrypted_seed = f.read().strip()

    # Load private key
    private_key = load_private_key()

    # Decrypt seed
    try:
        seed = decrypt_seed(encrypted_seed, private_key)
        print("✅ Decrypted Seed:", seed)

        # Save seed to local file (later in Docker it will be /data/seed.txt)
        with open("seed.txt", "w") as f:
            f.write(seed)

        print("Seed saved to seed.txt")

    except Exception as e:
        print("❌ Error:", e)
