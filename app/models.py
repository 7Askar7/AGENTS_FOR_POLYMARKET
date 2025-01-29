from pydantic import BaseModel, Field
from typing import List, Optional


class EmptyInput(BaseModel):
    """Empty input for tools that do not require arguments."""
    pass


class SymbolInput(BaseModel):
    symbol: str = Field(description="Symbol of the cryptocurrency in the format like 'BTC', 'ETH', etc.")


class PriceHistory(BaseModel):
    symbol: str = Field(description="Symbol of the cryptocurrency in the format like 'BTC', 'ETH', etc.")
    ohlcv: List[dict] = Field(description="OHLCV data for the cryptocurrency")


class NewsItem(BaseModel):
    title: str = Field(..., description="Title of the news article")
    content: str = Field(..., description="Body/content of the article")
    pub_date: str = Field(..., description="Publication date/time in ISO format")
    topic: Optional[str] = Field(None, description="High-level topic or category (if any)")
    sentiment: Optional[str] = Field(None, description="Sentiment label for the news (e.g., positive, negative)")
    entities: Optional[List[str]] = Field(None, description="List of entities (people, companies) mentioned")


class TweetItem(BaseModel):
    tweet_created_at: str = Field(..., description="Timestamp of the tweet creation in ISO format")
    tweet: str = Field(..., description="Text content of the tweet")
    user_name: str = Field(..., description="Display name of the Twitter user")
    sentiment: Optional[str] = Field(None, description="Sentiment label for the tweet")


class HackItem(BaseModel):
    name: str = Field(..., description="Name of the protocol or project that was hacked")
    timestamp: int = Field(..., description="Unix timestamp (seconds) for when the hack occurred")
    amount: Optional[float] = Field(None, description="Amount lost in the hack (if known)")
    technique: Optional[str] = Field(None, description="Technique used for the hack (e.g., Frontend Attack)")


class PolymarketItem(BaseModel):
    market_id: str = Field(..., description="Unique ID for the Polymarket event")
    question: str = Field(..., description="The question or proposition being bet on")
    outcome_yes_price: float = Field(..., description="Price (probability) for the 'Yes' outcome")
    up: bool = Field(..., description="Whether the outcome_yes_price is up (True) or down (False)")
    end_date_iso: str = Field(..., description="ISO timestamp for when the market/event ends")


class UnlockItem(BaseModel):
    name: str = Field(..., description="Full name of the token/project")
    symbol: str = Field(..., description="Ticker symbol of the token")
    next_event: int = Field(..., description="Unix timestamp for the next unlock event")
    to_unlock_usd: float = Field(..., description="Value of tokens to be unlocked, in USD")
    price: float = Field(..., description="Current price of the token")
    delta_rel: float = Field(..., description="Relative change or difference related to unlock events")


class RaiseItem(BaseModel):
    name: str = Field(..., description="Name of the project/protocol raising funds")
    timestamp: int = Field(..., description="Unix timestamp (seconds) for when the raise was announced/completed")
    amount: Optional[float] = Field(None, description="Amount raised in USD (if known)")
    round: Optional[str] = Field(None, description="Type of funding round (e.g., Seed, Series A)")
    lead_investor: Optional[str] = Field(None, description="Name of the lead investor, if known")


class TransferItem(BaseModel):
    transaction_hash: str = Field(..., description="Hash of the blockchain transaction")
    block_time: str = Field(..., description="Timestamp when the block was recorded, in ISO format")
    symbol: str = Field(..., description="Symbol of the asset being transferred")
    value: float = Field(..., description="Quantity of the asset transferred")
    value_usd: float = Field(..., description="USD value of the transferred amount")
    from_entity: str = Field(..., description="Address or entity from which the asset is sent")
    to_entity: str = Field(..., description="Address or entity to which the asset is sent")
    icon: Optional[str] = Field(None, description="URL to an icon for this asset")


class GovernanceItem(BaseModel):
    org_name: str = Field(..., description="Name of the organization or DAO")
    title: str = Field(..., description="Title of the proposal")
    status: str = Field(..., description="Current status (e.g., active, closed)")
    start: int = Field(..., description="Unix timestamp (seconds) for when the vote/proposal started")
    end: int = Field(..., description="Unix timestamp (seconds) for when the vote/proposal ends")
    link: str = Field(..., description="URL to the governance proposal")
    quorum: float = Field(..., description="Quorum threshold needed (if relevant)")
    choices: List[str] = Field(..., description="List of possible choices for voters (e.g., ['Yes', 'No'])")
    votes: List[float] = Field(..., description="Corresponding vote counts or weights per choice")
    voters: int = Field(..., description="Total number of voters")
    icon: Optional[str] = Field(None, description="URL to an icon representing the organization")


class Event(BaseModel):
    type: str = Field(description="Type of the event (e.g., news, tweet, hack, raise, governance)")
    data: dict = Field(description="Data associated with the event")


class TimestampInput(BaseModel):
    timestamp: str = Field(..., description="Current timestamp (date) in the format 'YYYY-MM-DD'. Example: '2024-01-01'")
