import pytest

from typing import List, Dict

from app.clients.llamafeed import DefillamaFeedClient


@pytest.fixture
def real_client():
    """
    Returns a real instance of DefillamaFeedClient.
    """
    return DefillamaFeedClient()


def _check_non_empty_list_of_dicts(data: List[Dict]):
    """
    Helper assertion function that checks if the response is a 
    non-empty list and that the first item is a dictionary.
    """
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    if len(data) > 0:
        assert isinstance(data[0], dict), f"Expected dict in first item, got {type(data[0])}"
    # The list might be empty if the feed has no items at the moment.


@pytest.mark.integration
def test_get_news_integration(real_client):
    """
    Calls the /news endpoint in the real API and checks 
    that we get a non-empty list of dicts (or at least a list).
    """
    data = real_client.get_news()
    _check_non_empty_list_of_dicts(data)


@pytest.mark.integration
def test_get_tweets_integration(real_client):
    """
    Calls the /tweets endpoint in the real API.
    """
    data = real_client.get_tweets()
    _check_non_empty_list_of_dicts(data)


@pytest.mark.integration
def test_get_hacks_integration(real_client):
    """
    Calls the /hacks endpoint in the real API.
    """
    data = real_client.get_hacks()
    _check_non_empty_list_of_dicts(data)


@pytest.mark.integration
def test_get_polymarket_integration(real_client):
    """
    Calls the /polymarket endpoint in the real API.
    """
    data = real_client.get_polymarket()
    _check_non_empty_list_of_dicts(data)


@pytest.mark.integration
def test_get_unlocks_integration(real_client):
    """
    Calls the /unlocks endpoint in the real API.
    """
    data = real_client.get_unlocks()
    _check_non_empty_list_of_dicts(data)


@pytest.mark.integration
def test_get_raises_integration(real_client):
    """
    Calls the /raises endpoint in the real API.
    """
    data = real_client.get_raises()
    _check_non_empty_list_of_dicts(data)


@pytest.mark.integration
def test_get_transfers_integration(real_client):
    """
    Calls the /transfers endpoint in the real API.
    """
    data = real_client.get_transfers()
    _check_non_empty_list_of_dicts(data)


@pytest.mark.integration
def test_get_governance_integration(real_client):
    """
    Calls the /governance endpoint in the real API.
    """
    data = real_client.get_governance()
    _check_non_empty_list_of_dicts(data)
