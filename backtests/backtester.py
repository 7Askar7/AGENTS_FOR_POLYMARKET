import time

from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.agents.base_agent import BasePredictorAgent


@dataclass
class BacktestConfig:
    """
    Configuration for backtesting a predictor agent.

    Args:
        agent (BasePredictorAgent): Predictor agent to backtest
        start_date (datetime): Start timestamp in format 'YYYY-MM-DD'
        end_date (datetime): End timestamp in format 'YYYY-MM-DD'
        delta_time (int): Time delta in days between timestamps
        question (str): Question to ask the predictor agent
        description (str): Description of the event
    """
    agent: BasePredictorAgent
    start_date: datetime
    end_date: datetime
    delta_time: int
    question: str
    description: str


class PredictorBacktester:
    """
    Backtester for predictor agents.
    
    It runs a backtest for a given predictor agent over a specified date range and saves the results.
    """

    def __init__(self, config: BacktestConfig):
        self.agent = config.agent
        self.config = config

    def _generate_dates(self):
        current_date = self.config.start_date
        end_date = self.config.end_date
        while current_date <= end_date:
            yield current_date
            current_date += timedelta(days=self.config.delta_time)

    def run_backtest(self) -> List[Dict]:
        responses: List[Dict] = []
        for date in self._generate_dates():
            response = self.agent.predict(question=self.config.question, description=self.config.description)
            response['date'] = date
            responses.append(response)
            time.sleep(10)
        return responses
