import pytest

from app.agents.swarm import SwarmAgent
from app.agents.simple_agent import SimpleAgent
from app.utils import get_env

@pytest.fixture
def api_key():
    return get_env("OPENAI_API_KEY")


def test_swarm_agent(api_key):
    question = "Bitcoin above $105,000 on January 31?"
    description = """
    This market will resolve to "Yes" if the Binance 1 minute candle for BTCUSDT 31 Jan '25 12:00 in the ET timezone (noon) has a final “Close” price of 105,000.01 or higher. Otherwise, this market will resolve to "No".
    """
    agents = [
        SimpleAgent(api_key=api_key, temperature=i/10) for i in range(1, 5)
    ]
    swarm = SwarmAgent(api_key=api_key, agents=agents)
    result = swarm.predict(question, description)
    # Wait
    # {'probabilities': {'positive': 0.4, 'negative': 0.6}, 'confidence': 'medium',
    # 'reasoning': ["There is no direct information from the news or tweets about Trump's chances of winning the election.",
    # "The political landscape is highly dynamic and polarized, presenting challenges for Trump's candidacy.", 'Public opinion and political developments can change rapidly, affecting the election outcome.', 'Historical trends show mixed results for incumbents or former presidents seeking re-election.',
    # "Current sentiment in news and social media indicates a divided opinion on Trump's policies and leadership."]}
    assert 'probabilities' in result
    assert 'confidence' in result
    assert 'reasoning' in result
    assert len(result['reasoning']) > 0
