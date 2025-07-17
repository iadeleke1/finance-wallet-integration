Here’s how to enhance the `prod_portfolio_checker_cli.py` module to automatically export results to both AWS S3 and Copilot Vault after tagging the portfolio accounts:

---

🧰 Requirements

• ✅ AWS: `boto3` configured with credentials and access to your target bucket.
• ✅ Copilot Vault: an API endpoint and write access for pushing JSON payloads.


---

🗂 Module Enhancements

import json
import boto3
import requests

# ─── AWS S3 Exporter ─────────────────────────────────────────────
def export_to_s3(data: list, bucket_name: str, object_key: str) -> bool:
    try:
        s3 = boto3.client('s3')
        payload = json.dumps(data, indent=2)
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=payload)
        logger.info(f"📦 Exported to S3: s3://{bucket_name}/{object_key}")
        return True
    except Exception as e:
        logger.error(f"S3 Export Failed: {e}")
        return False


# ─── Copilot Vault Exporter ──────────────────────────────────────
def export_to_copilot_vault(data: list, vault_url: str, api_key: str) -> bool:
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        payload = json.dumps(data)
        response = requests.post(vault_url, headers=headers, data=payload)
        response.raise_for_status()
        logger.info(f"🔐 Exported to Copilot Vault: {vault_url}")
        return True
    except Exception as e:
        logger.error(f"Copilot Vault Export Failed: {e}")
        return False

---

🧪 Sample Use in `main()` CLI Block

After portfolio results are tagged:

# Export JSON results to S3
if os.getenv('EXPORT_TO_S3') == 'true':
    export_to_s3(
        results,
        bucket_name=os.getenv('S3_BUCKET'),
        object_key=f"portfolio_export/{args.env}_portfolio.json"
    )

# Export results to Copilot Vault
if os.getenv('EXPORT_TO_VAULT') == 'true':
    export_to_copilot_vault(
        results,
        vault_url=os.getenv('VAULT_URL'),
        api_key=os.getenv('VAULT_API_KEY')
    )

---

🎛 Environment Variables to Set

# AWS
EXPORT_TO_S3=true
S3_BUCKET=my-finance-exports

# Copilot Vault
EXPORT_TO_VAULT=true
VAULT_URL=https://vault.copilot.microsoft.com/api/v1/portfolio/upload
VAULT_API_KEY=your_secure_api_key

---

Want to add retention rules for bucket or versioning in Vault next? Or simulate the vault upload in a test harness?
