from dotenv import load_dotenv
import os

from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON


def main():
    host = "https://clob.polymarket.com"
    key = os.getenv("PK")
    chain_id = POLYGON
    client = ClobClient(host, key=key, chain_id=chain_id)
    print(client.create_api_key())


if __name__ == '__main__':
    load_dotenv()
    main()
