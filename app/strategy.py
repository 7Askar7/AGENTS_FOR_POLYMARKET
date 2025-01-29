from dataclasses import dataclass
from enum import Enum


class Action(Enum):
    BUY = 1
    SELL = 2
    HOLD = 3


@dataclass
class State:
    yes: float # Probability of YES
    confidence: str
    current_price: float # Current price of YES


def base_strategy(state: State, conf: float) -> Action:
    """ 
    Base strategy for trading on the prediction market

    Args:
        state (State): state of the prediction market with a agent prediction
        conf (float): confidence threshold

    Returns:
        Action: action to take
    """
    if abs(conf - 1) > 1:
        raise ValueError("Confidence must be between 0 and 1")

    if state.confidence != "high":
        return Action.HOLD

    delta = state.yes - state.current_price
    if delta > 0 and delta > conf:
        return Action.BUY
    elif delta < 0 and abs(delta) > conf:
        return Action.SELL
    else:
        return Action.HOLD
