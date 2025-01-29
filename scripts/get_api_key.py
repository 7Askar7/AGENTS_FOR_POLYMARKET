import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from dotenv import load_dotenv

from py_clob_client.constants import POLYGON


def main():
    host = "https://clob.polymarket.com"
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = POLYGON
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    print(client.derive_api_key())


if __name__ == '__main__':
    load_dotenv()
    main()
