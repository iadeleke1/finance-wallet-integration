Here’s a self-contained Python snippet that:

• Spins up both a Sandbox and Development (Playground) Plaid client
• Creates a mock investments portfolio
• Marks the investment account as non-spending (subtype = “other”)
• Fetches and tags accounts with an `is_spending` flag


from plaid import Client
import datetime

# ─── Configuration ──────────────────────────────────────────────
PLAID_CLIENT_ID    = 'your_client_id'
PLAID_SBX_SECRET   = 'your_sandbox_secret'
PLAID_DEV_SECRET   = 'your_dev_secret'

# Initialize Sandbox and Playground (Development) clients
sandbox_client    = Client(client_id=PLAID_CLIENT_ID,
                           secret=PLAID_SBX_SECRET,
                           environment='sandbox')

playground_client = Client(client_id=PLAID_CLIENT_ID,
                           secret=PLAID_DEV_SECRET,
                           environment='development')


# ─── Helper: create a sample investments portfolio ─────────────
def setup_portfolio(client):
    # 1. Create a sandbox public_token for investments
    sbx = client.Sandbox.public_token.create(
        institution_id='ins_109508',             # Sandbox investment institution
        initial_products=['investments']
    )
    public_token = sbx['public_token']

    # 2. Exchange for an access_token
    exch = client.Item.public_token.exchange(public_token)
    access_token = exch['access_token']

    # 3. Upsert holdings + account, marking subtype="other" (non-spending)
    today = datetime.date.today().isoformat()
    client.Sandbox.investments_holdings_upsert(
        access_token,
        holdings=[{
            'account_id':           'acc_1',
            'security_id':          'sec_1',
            'quantity':             10.0,
            'institution_price':    200.0,
            'institution_price_as_of': today
        }],
        accounts=[{
            'account_id':    'acc_1',
            'balances': {
                'current':   2000.0,
                'available': 2000.0,
                'limit':     None
            },
            'mask':           '0001',
            'name':           'Demo Portfolio Account',
            'official_name':  'Demo Investment Account',
            'type':           'investment',
            'subtype':        'other'    # <— non-spending marker
        }]
    )

    return access_token


# ─── Bootstrapping ─────────────────────────────────────────────
sandbox_token    = setup_portfolio(sandbox_client)
playground_token = setup_portfolio(playground_client)

print('SANDBOX_ACCESS_TOKEN:   ', sandbox_token)
print('PLAYGROUND_ACCESS_TOKEN:', playground_token)


# ─── Fetch & Tag Accounts with is_spending Flag ────────────────
def fetch_and_tag(client, token):
    resp = client.Accounts.get(token)
    tagged = []
    for acct in resp['accounts']:
        # non-spending if investment + subtype==other
        non_spend = (acct['type']=='investment' and acct['subtype']=='other')
        acct['is_spending'] = not non_spend

        tagged.append({
            'id':          acct['account_id'],
            'name':        acct['name'],
            'balance':     acct['balances']['current'],
            'is_spending': acct['is_spending']
        })
    return tagged

print('Sandbox Accounts:',    fetch_and_tag(sandbox_client, sandbox_token))
print('Playground Accounts:', fetch_and_tag(playground_client, playground_token))
