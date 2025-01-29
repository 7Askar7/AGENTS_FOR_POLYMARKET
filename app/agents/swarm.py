import json
import time

from typing import Dict, List

from langchain.agents import AgentExecutor, ZeroShotAgent
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

from app.agents.base_agent import BasePredictorAgent
from app.agents.prompts import SYSTEM_PROMPT, SWARM_ACTION_PROMPT


class SwarmAgent(BasePredictorAgent):
    """
    Prediction agent to analyze news articles and predict event outcomes.

    Args:
        api_key (str): OpenAI API key
    """
    def __init__(self, api_key: str, agents: List[BasePredictorAgent]): 
        llm = ChatOpenAI(
            openai_api_key=api_key,
            temperature=0.2,
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
        self.agents = agents

    def _create_agent(self) -> AgentExecutor:
        """Creates the agent executor with proper prompts and tools."""
        prompt = ZeroShotAgent.create_prompt(
            tools=self._tools,
            prefix=SYSTEM_PROMPT,
            suffix=SWARM_ACTION_PROMPT,
            input_variables=["input", "agent_scratchpad"]
        )

        llm_chain = LLMChain(llm=self._llm, prompt=prompt)

        agent = ZeroShotAgent(
            llm_chain=llm_chain,
            tools=self._tools,
            verbose=True
        )

        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self._tools,
            memory=self._memory,
            verbose=True,
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
            answers: List[Dict] = []
            for agent in self.agents:
                answer = agent.predict(question, description)
                answers.append(answer)
                time.sleep(10)
            input_text = json.dumps(answers)
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
