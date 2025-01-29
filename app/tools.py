import logging
import requests

from typing import List
from datetime import datetime

from app.models import (
    PriceHistory,
    NewsItem,
    TweetItem,
    HackItem,
    PolymarketItem,
    UnlockItem,
    RaiseItem,
    TransferItem,
    GovernanceItem,
)

from app.clients.llamafeed import DefillamaFeedClient
from app.utils import get_env


def fetch_binance_price_history_tool(symbol: str) -> PriceHistory:
    """
    Fetches the price history of a cryptocurrency by symbol from Binance API
    symbol should be in the format like 'BTC', 'ETH', etc.
    """
    if symbol.endswith("USDT"):
        symbol = symbol[:-4]
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()+'USDT'}&interval=1h&limit=72"
    try:
        response = requests.get(url)
        response.raise_for_status()
        ohlcv = response.json()
        # example
        # [
        #     [
        #         1499040000000,      // Kline open time
        #         "0.01634790",       // Open price
        #         "0.80000000",       // High price
        #         "0.01575800",       // Low price
        #         "0.01577100",       // Close price
        #         "148976.11427815",  // Volume
        #         1499644799999,      // Kline Close time
        #         "2434.19055334",    // Quote asset volume
        #         308,                // Number of trades
        #         "1756.87402397",    // Taker buy base asset volume
        #         "28.46694368",      // Taker buy quote asset volume
        #         "0"                 // Unused field, ignore.
        #     ]
        # ]
        ohlcv = [
            {
                "open_time": data[0],
                "open_price": data[1],
                "high_price": data[2],
                "low_price": data[3],
                "close_price": data[4],
                "volume": data[5],
                "close_time": data[6],
                "quote_asset_volume": data[7],
                "number_of_trades": data[8],
                "taker_buy_base_asset_volume": data[9],
                "taker_buy_quote_asset_volume": data[10],
            }
            for data in ohlcv
        ]
        return PriceHistory(symbol=symbol, ohlcv=ohlcv)
    except Exception as e:
        logging.error(f"Failed to fetch price history: {e}")
        return None


def fetch_defillama_news_tool() -> List[NewsItem]:
    """
    Fetch and parse news items from Defillama Feed.
    """
    client = DefillamaFeedClient()
    try:
        data = client.get_news()
        return [NewsItem(**item) for item in data]
    except Exception as e:
        logging.error(f"Failed to fetch news: {e}")
        return []


def fetch_defillama_tweets_tool() -> List[TweetItem]:
    """
    Fetch and parse tweet items from Defillama Feed.
    """
    client = DefillamaFeedClient()
    try:
        data = client.get_tweets()
        return [TweetItem(**item) for item in data]
    except Exception as e:
        logging.error(f"Failed to fetch tweets: {e}")
        return []


def fetch_defillama_hacks_tool() -> List[HackItem]:
    """
    Fetch and parse hack items from Defillama Feed.
    """
    client = DefillamaFeedClient()
    try:
        data = client.get_hacks()
        return [HackItem(**item) for item in data]
    except Exception as e:
        logging.error(f"Failed to fetch hacks: {e}")
        return []


def fetch_defillama_polymarket_tool() -> List[PolymarketItem]:
    """
    Fetch and parse Polymarket items from Defillama Feed.
    """
    client = DefillamaFeedClient()
    try:
        data = client.get_polymarket()
        return [PolymarketItem(**item) for item in data]
    except Exception as e:
        logging.error(f"Failed to fetch polymarket data: {e}")
        return []


def fetch_defillama_unlocks_tool() -> List[UnlockItem]:
    """
    Fetch and parse unlock items from Defillama Feed.
    """
    client = DefillamaFeedClient()
    try:
        data = client.get_unlocks()
        return [UnlockItem(**item) for item in data]
    except Exception as e:
        logging.error(f"Failed to fetch unlocks: {e}")
        return []


def fetch_defillama_raises_tool() -> List[RaiseItem]:
    """
    Fetch and parse raise items from Defillama Feed.
    """
    client = DefillamaFeedClient()
    try:
        data = client.get_raises()
        return [RaiseItem(**item) for item in data]
    except Exception as e:
        logging.error(f"Failed to fetch raises: {e}")
        return []


def fetch_defillama_transfers_tool() -> List[TransferItem]:
    """
    Fetch and parse transfer items from Defillama Feed.
    """
    client = DefillamaFeedClient()
    try:
        data = client.get_transfers()
        return [TransferItem(**item) for item in data]
    except Exception as e:
        logging.error(f"Failed to fetch transfers: {e}")
        return []


def fetch_defillama_governance_tool() -> List[GovernanceItem]:
    """
    Fetch and parse governance items from Defillama Feed.
    """
    client = DefillamaFeedClient()
    try:
        data = client.get_governance()
        return [GovernanceItem(**item) for item in data]
    except Exception as e:
        logging.error(f"Failed to fetch governance: {e}")
        return []


def get_current_timestamp_tool() -> str:
    """
    Get current timestamp in format 'YYYY-MM-DD HH:MM:SS'. Example: '2022-01-01 12:00:00'
    """
    return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
