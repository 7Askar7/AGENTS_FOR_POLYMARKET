import pytest
from typing import List, Dict

# Add base directory to sys.path if necessary
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.clients.polymarket import PolyMarketClient
from app.utils import get_env


@pytest.fixture
def client():
    """
    Pytest fixture to initialize PolyMarketClient with real API credentials.
    """
    # can be empty
    key = ""
    api_key = ""
    api_secret = ""
    api_passphrase = ""
    return PolyMarketClient(key, api_key, api_secret, api_passphrase)


def _check_non_empty_list_of_dicts(data: List[Dict]):
    """
    Helper assertion function that checks if the response is a 
    list and that the first item is a dictionary.
    """
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    if len(data) > 0:
        assert isinstance(data[0], dict), f"Expected dict in first item, got {type(data[0])}"


@pytest.mark.integration
def test_get_markets_integration(client):
    """
    Calls the get_markets method and checks 
    that we get a list of markets.
    """
    markets = client.get_markets()
    _check_non_empty_list_of_dicts(markets)
    market = markets[-1]
    assert market.get('condition_id'), "Missing condition_id"
    assert market.get('question'), "Missing question"
    assert market.get('description'), "Missing description"
    assert market.get('end_date_iso'), "Missing end_date_iso"
    assert market.get('market_slug'), "Missing market_slug"
    assert market.get('minimum_order_size'), "Missing minimum_order_size"
    assert market.get('minimum_tick_size'), "Missing minimum_tick_size"
    assert market.get('active') is not None, "Missing active"
    assert market.get('closed') is not None, "Missing closed"
    assert market.get('archived') is not None, "Missing archived"


@pytest.mark.integration
def test_get_simplified_markets_integration(client):
    """
    Calls the get_simplified_markets method and checks 
    that we get a list of simplified markets.
    """
    simplified_markets = client.get_simplified_markets()
    _check_non_empty_list_of_dicts(simplified_markets)
    market = simplified_markets[-1]


@pytest.mark.integration
def test_get_market_integration(client):
    """
    Calls the get_market method with a known market_id and checks the response.
    Replace 'known_market_id' with an actual market ID for testing.
    """
    known_market_id = "0xbfe1547b3582fb5307c604f62d6f5818adadf9260a1f5a93f16216c41baba964"
    market = client.get_market(known_market_id)
    assert isinstance(market, dict), f"Expected dict, got {type(market)}"
    assert market.get('condition_id') == known_market_id, "Market ID does not match"


@pytest.mark.integration
def test_get_price_integration(client):
    """
    Calls the get_price_history method with a known market_id and checks the response.
    Replace 'known_market_id' with an actual market ID for testing.
    """
    token_id = "5114173491195416254365602929074381343823182276653657249022440867189120977342"
    price: float = client.get_price(token_id)
    assert isinstance(price, float), f"Expected float, got {type(price)}"
    assert price >= 0, "Price should be non-negative"


@pytest.mark.integration
def test_get_price_history_integration(client):
    """
    Calls the get_price_history method with a known market_id and checks the response.
    Replace 'known_market_id' with an actual market ID for testing.
    """
    token_id = "5114173491195416254365602929074381343823182276653657249022440867189120977342"
    start_ts = 1632141900
    end_ts = 1737399571
    price_history = client.get_price_history_with_timestamps(token_id, start_ts, end_ts, 60*24)
    _check_non_empty_list_of_dicts(price_history)
    price = price_history[-1]
    assert price.get('p'), "Missing price"
    assert price.get('t'), "Missing timestamp"


@pytest.mark.integration
def test_get_price_history_with_interval_integration(client):
    """
    Calls the get_price_history_with_interval method with a known market_id and checks the response.
    Replace 'known_market_id' with an actual market ID for testing.
    """
    token_id = "5114173491195416254365602929074381343823182276653657249022440867189120977342"
    interval = "1d"
    fidelity = 1
    price_history = client.get_price_history_with_interval(token_id, interval, fidelity)
    _check_non_empty_list_of_dicts(price_history)
    price = price_history[-1]
    assert price.get('p'), "Missing price"
    assert price.get('t'), "Missing timestamp"
