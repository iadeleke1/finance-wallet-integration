import os
import logging
import argparse
import json
from plaid import Client
from plaid.errors import PlaidError
from typing import List, Dict

# ─── Logging Setup ─────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─── Constants ─────────────────────────────────────────────────
SPENDING_SUBTYPES = ['brokerage', 'cash', 'checking', 'savings']
SUPPORTED_ENVS = ['production', 'development', 'sandbox']


# ─── Client Initialization ─────────────────────────────────────
def init_client(env: str) -> Client:
    if env not in SUPPORTED_ENVS:
        raise ValueError(f"Unsupported environment: {env}")
    return Client(
        client_id=os.getenv(f'PLAID_{env.upper()}_CLIENT_ID'),
        secret=os.getenv(f'PLAID_{env.upper()}_SECRET'),
        environment=env
    )


# ─── Portfolio Fetcher ─────────────────────────────────────────
def fetch_tagged_accounts(client: Client, token: str, filter_account_id=None) -> List[Dict]:
    try:
        response = client.Accounts.get(token)
        accounts = response['accounts']
        tagged = []

        for acct in accounts:
            is_spending = acct['type'] == 'investment' and acct['subtype'] in SPENDING_SUBTYPES

            if filter_account_id and acct['account_id'] != filter_account_id:
                continue

            tagged.append({
                'account_id':  acct['account_id'],
                'name':        acct['name'],
                'balance':     acct['balances']['current'],
                'subtype':     acct['subtype'],
                'is_spending': is_spending
            })

        logger.info(f"✅ Fetched {len(tagged)} tagged account(s).")
        return tagged

    except PlaidError as e:
        logger.error(f"Plaid API Error: {e.message}")
    except Exception as ex:
        logger.exception("Unexpected error during portfolio fetch.")
    return []


# ─── CLI Entrypoint ────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Tagged Plaid portfolio checker.")
    parser.add_argument('--env', choices=SUPPORTED_ENVS, default='production', help='Plaid environment')
    parser.add_argument('--account-id', help='Filter results by account_id')
    parser.add_argument('--json-output', action='store_true', help='Output results in JSON')
    args = parser.parse_args()

    access_token_env = f'PLAID_{args.env.upper()}_ACCESS_TOKEN'
    access_token = os.getenv(access_token_env)

    if not access_token:
        logger.error(f"Missing access token. Set {access_token_env}.")
        exit(1)

    client = init_client(args.env)
    results = fetch_tagged_accounts(client, access_token, args.account_id)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        for acct in results:
            flag = "🟢 Spending" if acct['is_spending'] else "🔴 Non-Spending"
            print(f"{flag} → {acct['name']} | ${acct['balance']} | {acct['subtype']}")


if __name__ == "__main__":
    main()
