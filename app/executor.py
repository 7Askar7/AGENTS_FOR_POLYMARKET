import time
import logging

from dataclasses import dataclass

from app.agents.base_agent import BaseAgent
from app.agentsV2.agents_graph import NewsAnalysisPredictorAgent

from app.clients.polymarket import PolyMarketClient
from app.strategy import Action, State, base_strategy



logger = logging.getLogger(__name__)


@dataclass
class Config:
    market_id: str # Market ID in the polymarket API
    sleep_time: int = 60 * 60 * 24
    trade_size: float = 10


class Executor:
    """
    Executor for the prediction market agent
    1. Get market data
    2. Get agent prediction
    3. Make decision based on agent prediction
    """
    def __init__(self, config: Config, agent: BaseAgent, client: PolyMarketClient):
        """
        Executor for the prediction market

        Args:
            config (Config): configuration for the executor
            agent (BaseAgent): base prediction agent
            client (PolyMarketClient): client for the polymarket API
        """
        logger.info("Initializing executor")
        logger.info(f"Config: {config}")
        self.agent = agent
        self.client = client
        self.config = config

    def run(self):
        market = self.client.get_market(market_id=self.market_id)
        if not market:
            raise ValueError("Market not found")
        if market['closed']:
            raise ValueError("Market is closed")

        # parse market data
        logger.info(f"Market: {market}")
        question = market['question']
        description = market['description']
        tokens = market['tokens']
        token_yes = [token for token in tokens if token['outcome'].lower() == 'yes'][0]
        token_no = [token for token in tokens if token['outcome'].lower() == 'no'][0]

        kwargs = {}
        if isinstance(self.agent, NewsAnalysisPredictorAgent):
            kwargs['data_frm'] = self.client.get_price_history_with_interval(token_id=token_yes['id'], interval='1d', fidelity=60*24)

        agent_prediction = self.agent.predict(question=question, description=description, data_frm=kwargs.get('data_frm', None))
        logger.info(f"Agent prediction: {agent_prediction}")

        if not agent_prediction:
            raise ValueError("Agent prediction not found")
        if 'probabilities' not in agent_prediction:
            raise ValueError("Probabilities not found in agent prediction")
        if agent_prediction['probabilities'] == 0.5:
            logger.info("Agent is not confident on prediction")
            return

        action: Action = base_strategy(
            state=State(yes=agent_prediction['probabilities']['positive'], current_price=token_yes['price']),
            conf=0.1
        )
        logger.info(f"Action: {action}")

        if action == Action.BUY:
            self.client.make_market_order(token_id=token_yes['id'], amount_usd=self.config.trade_size, is_buy=True)
        elif action == Action.SELL:
            self.client.make_market_order(token_id=token_no['id'], amount_usd=self.config.trade_size, is_buy=False)
        else:
            pass

    def start(self):
        while True:
            try:
                self.run()
            except Exception as e:
                logger.error(e)

            logger.info(f"Sleeping for {self.config.sleep_time} seconds")
            time.sleep(self.config.sleep_time)
