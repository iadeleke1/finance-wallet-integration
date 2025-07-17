import json
import datetime

def simulate_vault_upload(user_id="demo_user"):
    payload = {
        "user_id": user_id,
        "wallet_type": "google",
        "preferred_asset": "QQQ",
        "portfolio": [
            {
                "account_id": "acct-001",
                "balance": 4532.10,
                "is_spending": True,
                "subtype": "brokerage"
            }
        ],
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    print("🔐 Simulated Vault Payload:")
    print(json.dumps(payload, indent=2))

simulate_vault_upload()
