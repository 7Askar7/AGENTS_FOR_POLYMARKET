from typing import Dict, List
from abc import ABC, abstractmethod

from langchain.agents import Tool, AgentExecutor


class BasePredictorAgent(ABC):

    def __init__(self, llm):
        self._llm = llm
        self._tools = self._create_tools()
        agent_executor = self._create_agent()
        if agent_executor is not None:
            self._agent_executor = agent_executor

    def _create_tools(self) -> List[Tool]:
        """Creates the list of available tools."""
        return []

    def _create_agent(self) -> AgentExecutor:
        """Creates the agent executor."""
        pass

    @abstractmethod
    def predict(self, question: str, description: str, *args, **kwargs) -> Dict:
        """
        Predicts the outcome of an event.
        
        Args:
            question (str): The question of the event in the polymarket format.
            description (str): The description of the event from polymarket.

        Returns:
        {
            "probabilities": {
                "positive": 0.4,
                "negative": 0.6
            },
            "confidence": "medium",
            "reasoning": [
                "Current polling data and historical trends suggest a competitive race.",
                "Donald J. Trump has a strong base of support, but also significant opposition.",
                "The lack of recent news may indicate stability in the current political dynamics, but this could change as the election date approaches."
            ]
        }
        """
        raise NotImplementedError
