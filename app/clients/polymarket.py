from typing import Dict, List, Optional

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import MarketOrderArgs
from py_clob_client.order_builder.constants import BUY, SELL
from py_clob_client.http_helpers.helpers import get




class PolyMarketClient:
    """
    A client for interacting with the Polymarket API.
    """
    host = "https://clob.polymarket.com/"
    chain = POLYGON
    GET_PRICE_HISTORY = "/prices-history"

    def __init__(self, key: str, api_key: str, api_secret: str, api_passphrase: str):
        """
        Initialize the client.
        Call the create_api_key script to get the key, secret, and passphrase.
        """
        creds = ApiCreds(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase,
        )
        self.client = ClobClient(self.host, key=key, chain_id=self.chain, creds=creds)

    def get_markets(self) -> List[Dict]:
        return self.client.get_markets()['data']

    def get_simplified_markets(self) -> List[Dict]:
        return self.client.get_simplified_markets()['data']

    def get_market(self, market_id: str) -> Dict:
        """
        Get a market by ID.

        Args:
            market_id (str): The ID of the market (condition id)

        Returns:
            Dict:
            {
                'enable_order_book': True,
                'active': True,
                'closed': False,
                'archived': False,
                'accepting_orders': True,
                'accepting_order_timestamp': '2024-09-17T18:17:02Z',
                'minimum_order_size': 5,
                'minimum_tick_size': 0.001,
                'condition_id': '0xbfe1547b3582fb5307c604f62d6f5818adadf9260a1f5a93f16216c41baba964',
                'question_id': '0xbc425549dfa96c89beefa96229584077863ecb1f29ef56f7249e378795a3450e',
                'question': 'Will Dinamo Zagreb win the UEFA Champions League?',
                'description': 'This market will resolve to “Yes” if Dinamo Zagreb wins the 2024-25 UEFA...',
                'market_slug': 'will-dinamo-zagreb-win-the-uefa-champions-league',
                'end_date_iso': '2025-05-31T00:00:00Z',
                'game_start_time': None,
                'seconds_delay': 0,
                'fpmm': '',
                'maker_base_fee': 0,
                'taker_base_fee': 0,
                'notifications_enabled': True,
                'neg_risk': True,
                'neg_risk_market_id': '0xbc425549dfa96c89beefa96229584077863ecb1f29ef56f7249e378795a34500',
                'neg_risk_request_id': '0x0d5ef4d365d2605f10b890509bab12febd705cda6a88f856d506bc2cde019cf4',
                'icon': 'https://polymarket-upload.s3.us-east-2.amazonaws.com/will-dinamo-zagreb-win-the-uefa-champions-league-ZPwJ-1gXlnYa.png',
                'image': 'https://polymarket-upload.s3.us-east-2.amazonaws.com/will-dinamo-zagreb-win-the-uefa-champions-league-ZPwJ-1gXlnYa.png',
                'rewards': {'rates': [{'asset_address': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174', 'rewards_daily_rate': 2}],'min_size': 50, 'max_spread': 3.5},
                'is_50_50_outcome': False,
                'tokens': [
                    {
                        'token_id': '50029558763292490004907035090369845036388910577919998659622549622859634207886',
                        'outcome': 'Yes',
                        'price': 0.003,
                        'winner': False
                    },
                    {
                        'token_id': '5114173491195416254365602929074381343823182276653657249022440867189120977342',
                        'outcome': 'No',
                        'price': 0.997,
                        'winner': False
                    }
                ],
                'tags': ['Sports', 'Champions League', 'Soccer']
            }
        """
        return self.client.get_market(market_id)

    def make_market_order(self, token_id: str, amount_usd: float, is_buy: Optional[bool] = True) -> Dict:
        """
        Make a market order.

        Args:
            token_id (str): market token id (71321045679252212594626385532706912750332728571942532289631379312455583992563)
            amount_usd (float): amount in USDC
            is_buy (Optional[bool], optional): Market side. Defaults to True.

        Returns:
            Dict:
        """
        order_args = MarketOrderArgs(
            token_id=token_id,
            amount=amount_usd,
            side=BUY if is_buy else SELL,
        )
        signed_order = self.client.create_market_order(order_args)
        return signed_order

    def get_price(self, token_id: str, is_buy: Optional[bool] = True) -> float:
        """
        Get price for a token.

        Args:
            token_id (str): market token id (71321045679252212594626385532706912750332728571942532289631379312455583992563)
            is_buy (Optional[bool], optional): Market side. Defaults to True.

        Returns:
            float: Price
        """
        return float(self.client.get_price(token_id=token_id, side=BUY if is_buy else SELL)['price'])

    def get_price_history_with_interval(self, token_id: str, interval: str, fidelity: str) -> List[Dict]:
        """
        https://docs.polymarket.com/#timeseries-data
        
        The CLOB provides detailed price history data for each traded token.
        Args:
            token_id (str): the CLOB token id for which to fetch price history
            interval (str): a string representing a duration ending at the current time
            fidelity (int): the resolution of the data, in minutes

        Returns:
            List[Dict]: 
            [
                {
                    "t": 1632141600,
                    "p": 0.003
                },
                {
                    "t": 1632141900,
                    "p": 0.003
                }
            ]
        """
        timeseries_points = get("{}{}?market={}&interval={}&fidelity={}".format(self.host, self.GET_PRICE_HISTORY, token_id, interval, fidelity))
        return timeseries_points['history']

    def get_price_history_with_timestamps(self, token_id: str, startTs: int, endTs: int, fidelity: str) -> List[Dict]:
        """
        https://docs.polymarket.com/#timeseries-data
        
        The CLOB provides detailed price history data for each traded token.
        Args:
            token_id (str): the CLOB token id for which to fetch price history
            start_ts (int): the start time, a unix timestamp in UTC
            end_ts (int): the end time, a unix timestamp in UTC
            fidelity (int): the resolution of the data, in minutes

        Returns:
            List[Dict]: 
            [
                {
                    "t": 1632141600,
                    "p": 0.003
                },
                {
                    "t": 1632141900,
                    "p": 0.003
                }
            ]
        """
        timeseries_points = get("{}{}?market={}&startTs={}&endTs={}&fidelity={}".format(self.host, self.GET_PRICE_HISTORY, token_id, startTs, endTs, fidelity))
        return timeseries_points['history']

if __name__ == "__main__":
    PolyMarketClient().get_market()