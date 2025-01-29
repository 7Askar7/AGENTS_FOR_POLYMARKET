import pickle

from datetime import datetime
from typing import List

from app.agents.swarm import SwarmAgent
from app.utils import get_env

from backtests.backtester import BacktestConfig, PredictorBacktester
from backtests.timestamp_generator import TimestampGenerator
from backtests.simple_agent_backtest import MockedSimplePredictorAgent


def run_backtest(question: str, description: str, start_date: str, end_date: str, delta_time: int = 3) -> List[dict]:
    api_key: str = get_env("OPENAI_API_KEY")
    agents = [
        MockedSimplePredictorAgent(
            api_key=api_key, temperature=i/10,
            timestamp_generator=TimestampGenerator(
                start_date=start_date,
                end_date=end_date,
                delta_time=delta_time
            )
        ) for i in range(3, 6)
    ]
    agent = SwarmAgent(api_key=api_key, agents=agents)
    config = BacktestConfig(
        agent=agent,
        start_date=start_date,
        end_date=end_date,
        delta_time=delta_time,
        question=question,
        description=description,
    )
    backtester = PredictorBacktester(config)
    return backtester.run_backtest()


if __name__ == "__main__":
    question = "Will Donald J. Trump win the 2024 US Presidential Election?"
    description = """
    This market will resolve to “Yes” if Donald J. Trump wins the last US Presidential Election. Otherwise, this market will resolve to “No.”

    The resolution source for this market is the Associated Press, Fox News, and NBC. This market will resolve once all three sources call the race for the same candidate. If all three sources haven’t called the race for the same candidate by the inauguration date (January 20, 2025) this market will resolve based on who is inaugurated.
    """
    data = run_backtest(
        question=question,
        description=description,
        start_date=datetime(2024, 10, 16),
        end_date=datetime(2024, 11, 6),
        delta_time=7,
    )

    with open("trump.pickle", "wb+") as f:
        pickle.dump(data, f)
