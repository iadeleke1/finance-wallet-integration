import jwt
import datetime
import os

# Load environment variables or secrets
GOOGLE_ISSUER_ID = os.getenv("GOOGLE_ISSUER_ID", "demo_issuer")
PRIVATE_KEY_PATH = os.getenv("GOOGLE_PRIVATE_KEY_PATH", "wallet_google/demo_key.pem")

# Load private key
with open(PRIVATE_KEY_PATH, "r") as key_file:
    private_key = key_file.read()

# Construct payload
payload = {
    "iss": GOOGLE_ISSUER_ID,
    "aud": "google",
    "typ": "savetowallet",
    "iat": int(datetime.datetime.utcnow().timestamp()),
    "payload": {
        "portfolioClass": {
            "id": "demo_user_portfolio",
            "accountType": "brokerage",
            "balance": "$4,532.10",
            "preferredAsset": "QQQ",
            "aumLevel": "Moderate"
        }
    }
}

# Generate JWT
encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
print("📲 Generated JWT Pass:")
print(encoded_jwt)
