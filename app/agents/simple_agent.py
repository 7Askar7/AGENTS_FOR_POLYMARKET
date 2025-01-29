import json

from typing import List, Dict

from langchain.agents import Tool, AgentExecutor, ZeroShotAgent
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.tools import StructuredTool

from app.agents.base_agent import BasePredictorAgent
from app.agents.prompts import SYSTEM_PROMPT, ACTION_PROMPT

from app.models import (
    EmptyInput,
    SymbolInput,
)
from app.tools import (
    fetch_binance_price_history_tool,
    fetch_defillama_news_tool,
    fetch_defillama_tweets_tool,
    get_current_timestamp_tool,
)


class SimpleAgent(BasePredictorAgent):
    """
    Prediction agent to analyze news articles and predict event outcomes.

    Args:
        api_key (str): OpenAI API key
    """
    def __init__(self, api_key: str, temperature: float = 0.35): 
        llm = ChatOpenAI(
            openai_api_key=api_key,
            temperature=temperature,
            model_name="gpt-4o",
            max_tokens=1000,
        )
        # Initialize memory and agent executor
        self._memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=3
        )
        super().__init__(llm)

    def _create_tools(self) -> List[Tool]:
        """Creates the list of available tools."""
        return [
            StructuredTool(
                name="GetNews",
                func=fetch_defillama_news_tool,
                description="Fetch and parse news items from Defillama Feed.",
                args_schema=EmptyInput,
            ),
            StructuredTool(
                name="GetTweets",
                func=fetch_defillama_tweets_tool,
                description="Fetch and parse tweet items from Defillama Feed.",
                args_schema=EmptyInput,
            ),
            StructuredTool(
                name="GetPriceHistory",
                func=fetch_binance_price_history_tool,
                description="Fetch and parse price history for a cryptocurrency.",
                args_schema=SymbolInput,
            ),
            StructuredTool(
                name="GetCurrentTimestamp",
                func=get_current_timestamp_tool,
                description="Fetch the current timestamp.",
                args_schema=EmptyInput,
            ),
        ]

    def _create_agent(self) -> AgentExecutor:
        """Creates the agent executor with proper prompts and tools."""
        prompt = ZeroShotAgent.create_prompt(
            tools=self._tools,
            prefix=SYSTEM_PROMPT,
            suffix=ACTION_PROMPT,
            input_variables=["input", "agent_scratchpad"]
        )

        llm_chain = LLMChain(llm=self._llm, prompt=prompt)

        agent = ZeroShotAgent(
            llm_chain=llm_chain,
            tools=self._tools,
            verbose=False
        )

        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self._tools,
            memory=self._memory,
            verbose=False,
            max_iterations=5,
            handle_parsing_errors=True
        )

    def predict(self, question: str, description: str) -> Dict:
        """
        Predicts the outcome of an event based on news analysis.
        
        Args:
            news: List of news articles
            event_description: Event description
            
        Returns:
            Dict: Prediction results including probabilities and reasoning
        """
        try:
            input_text = f"""Question: {question}. Description: '{description}"""
            result = self._agent_executor.run(input=input_text)
            try:
                if isinstance(result, str):
                    # Try to find JSON pattern
                    import re
                    json_match = re.search(r'\{[\s\S]*\}', result)
                    if json_match:
                        return json.loads(json_match.group())
                    
                    # If no JSON found, format the response
                    return {
                        "probabilities": {"positive": 0.5, "negative": 0.5},
                        "confidence": "low",
                        "reasoning": [result.strip()]
                    }
                return result
            except json.JSONDecodeError:
                return {
                    "probabilities": {"positive": 0.5, "negative": 0.5},
                    "confidence": "low",
                    "reasoning": [str(result).strip()]
                }
            
        except Exception as e:
            return {
                "error": str(e),
                "probabilities": {"positive": 0.5, "negative": 0.5},
                "confidence": "low",
                "reasoning": [f"Error occurred: {str(e)}"]
            }
