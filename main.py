from app.executor import Executor, Config
from app.agents.base_agent import BasePredictorAgent
from app.agentsV2.agents_graph import NewsAnalysisPredictorAgent
from app.clients.polymarket import PolyMarketClient
from app.utils import get_env


if __name__ == "__main__":
    config: Config = Config(
        trade_size=float(get_env("TRADE_SIZE")),
        market_id=get_env("MARKET_ID"),
        sleep_time=60*60*24,
    )
    polymarket: PolyMarketClient = PolyMarketClient(
        key=get_env("PK"),
        api_key=get_env("CLOB_API_KEY"),
        api_secret=get_env("CLOB_SECRET"),
        api_passphrase=get_env("CLOB_PASS_PHRASE"),
    )

    agent: BasePredictorAgent = NewsAnalysisPredictorAgent()
    executor = Executor(
        config=config,
        polymarket=polymarket,
        agent=agent,
    )
    executor.start()
