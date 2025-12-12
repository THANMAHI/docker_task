import json
import requests

def request_seed(student_id: str, github_repo_url: str, api_url: str):
    """
    Request encrypted seed from instructor API
    """
    # 1. Read student public key from PEM file
    with open("/app/student_public.pem", "r") as f:
        public_key_pem = f.read()

    # 2. Prepare JSON payload
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_pem  # Python automatically handles \n correctly
    }

    # 3. Send POST request
    try:
        response = requests.post(api_url, json=payload, timeout=10)
    except Exception as e:
        print("❌ Request failed:", e)
        return

    # 4. Parse JSON response
    try:
        data = response.json()
    except:
        print("❌ Invalid JSON response:", response.text)
        return

    if data.get("status") != "success":
        print("❌ API Error:", data)
        return

    encrypted_seed = data.get("encrypted_seed")

    # 5. Save encrypted seed to file
    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)

    print("✅ Encrypted seed saved to encrypted_seed.txt")
    return encrypted_seed


if __name__ == "__main__":
    # 👇 Replace these values WITH YOUR OWN DETAILS
    STUDENT_ID = "23A91A61B3"
    GITHUB_REPO_URL = "https://github.com/THANMAHI/docker_task"  
    API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

    request_seed(STUDENT_ID, GITHUB_REPO_URL, API_URL)
