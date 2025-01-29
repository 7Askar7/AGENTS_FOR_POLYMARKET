import pickle

from datetime import datetime
from typing import List

from langchain.agents import Tool
from langchain.tools import StructuredTool

from app.models import EmptyInput, TimestampInput
from app.sources.feed_db import fetch_new_entries
from app.agents.simple_agent import SimpleAgent
from app.utils import get_env

from backtests.backtester import BacktestConfig, PredictorBacktester
from backtests.timestamp_generator import TimestampGenerator


class MockedSimplePredictorAgent(SimpleAgent):

    def __init__(self, api_key: str, timestamp_generator: TimestampGenerator, temperature: float = 0.35):
        self.timestamp_generator = timestamp_generator
        super().__init__(api_key=api_key, temperature=temperature)

    def _create_tools(self) -> List[Tool]:
        """Creates the list of available tools."""
        return [
            StructuredTool(
                name="GetNewsAndTweets",
                func=fetch_new_entries,
                description="Fetch and parse news & tweets items from Defillama Feed.",
                args_schema=TimestampInput,
            ),
            StructuredTool(
                name="GetCurrentTimestamp",
                func=self.timestamp_generator,
                description="Fetch the current timestamp in the format YYYY-MM-DD. Example: 2024-01-01",
                args_schema=EmptyInput,
            ),
        ]

def run_backtest(question: str, description: str, start_date: str, end_date: str, delta_time: int = 3) -> List[dict]:
    api_key: str = get_env("OPENAI_API_KEY")
    generator = TimestampGenerator(start_date=start_date, end_date=end_date, delta_time=delta_time)
    agent = MockedSimplePredictorAgent(api_key=api_key, timestamp_generator=generator)
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
        start_date=datetime(2024, 10, 17),
        end_date=datetime(2024, 11, 6),
        delta_time=3,
    )

    with open("trump.pickle", "wb+") as f:
        pickle.dump(data, f)
