# google_finance_playground.py

import os
from urllib.parse import urlencode

import requests
from google.oauth2.credentials import Credentials

class GoogleFinancePlaygroundClient:
    """
    A sandboxed “Playground” client for Google Finance portfolio testing.
    Supports:
      - OAuth2 code exchange against a sandbox endpoint
      - Resetting to a default demo portfolio
      - Fetching the demo portfolio payload
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        sandbox_base_url: str = "https://sandbox-googlefinance.example.com",
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = sandbox_base_url.rstrip("/")
        self.auth_url = f"{self.base_url}/oauth2/auth"
        self.token_url = f"{self.base_url}/oauth2/token"
        self.portfolio_url = f"{self.base_url}/v1/portfolios/demo"
        self.creds: Credentials = None

    def generate_auth_url(self, scopes=None, state="playground"):
        scopes = scopes or ["https://www.googleapis.com/auth/finance.readonly"]
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
        }
        return f"{self.auth_url}?{urlencode(params)}"

    def exchange_code(self, code: str) -> Credentials:
        payload = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        resp = requests.post(self.token_url, data=payload)
        resp.raise_for_status()
        token_data = resp.json()
        self.creds = Credentials(
            token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_uri=self.token_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        return self.creds

    def reset_demo_portfolio(self) -> dict:
        if not self.creds:
            raise RuntimeError("Call exchange_code() before resetting portfolio.")
        headers = {"Authorization": f"Bearer {self.creds.token}"}
        resp = requests.post(f"{self.portfolio_url}/reset", headers=headers)
        resp.raise_for_status()
        return resp.json()

    def get_demo_portfolio(self) -> dict:
        if not self.creds:
            raise RuntimeError("Call exchange_code() before fetching portfolio.")
        headers = {"Authorization": f"Bearer {self.creds.token}"}
        resp = requests.get(self.portfolio_url, headers=headers)
        resp.raise_for_status()
        return resp.json()


if __name__ == "__main__":
    # Demo usage: run this script to walk through OAuth and fetch the sandbox portfolio
    client = GoogleFinancePlaygroundClient(
        client_id=os.getenv("GF_CLIENT_ID"),
        client_secret=os.getenv("GF_CLIENT_SECRET"),
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
        sandbox_base_url="https://sandbox-googlefinance.example.com",
    )

    print("1) Visit this URL in your browser to authorize:")
    print(client.generate_auth_url())
    code = input("2) Paste the authorization code here: ").strip()

    # Exchange code for sandbox access token
    creds = client.exchange_code(code)
    print("✔️ Exchanged code, received sandbox access token.")

    # Reset to a fresh demo portfolio
    reset_resp = client.reset_demo_portfolio()
    print(f"🔄 Reset portfolio: {reset_resp}")

    # Fetch the current demo portfolio
    portfolio = client.get_demo_portfolio()
    print("📈 Demo Portfolio:")
    print(portfolio)
