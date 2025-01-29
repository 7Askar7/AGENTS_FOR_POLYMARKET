import json
import re

from typing import TypedDict, Dict, List
from enum import Enum

import pandas as pd

from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor


from app.agents.base_agent import BasePredictorAgent
from app.agentsV2.agent_get_news import NewsAnalysisAgent
from app.agentsV2.agent_optional_analyze import AgentOptionsAnalyzer
from app.agentsV2.agent_sort_url import AgentTopNews
from app.agentsV2.settings import MAIN_MODEL


class AgentState(TypedDict):
    user_request: str
    top_news: str
    agent_news: str
    agent_option: str
    final_analysis: str
    messages: List[Dict[str, str]]
    current_turn: int


class AgentTurn(Enum):
    NEWS = "news"
    OPTION = "option"
    COMPLETE = "complete"


class NewsAnalysisPredictorAgent(BasePredictorAgent):

    def __init__(self, llm=None):
        self._llm = llm or ChatOpenAI(model=MAIN_MODEL, temperature=0.7)
        super().__init__(self._llm)

    def _create_agent(self) -> AgentExecutor:
        # Optional: Create agent executor if needed
        return None

    def predict(self, question: str, description: str, data_frm: pd.DataFrame) -> Dict:
        # Use existing workflow to generate prediction
        workflow = self._create_news_workflow(data_frm, description)
        
        result = workflow.invoke({
            "user_request": question,
            "top_news": "",
            "agent_news": "",
            "agent_option": "",
            "final_analysis": "",
            "messages": [],
            "current_turn": 0
        })
        
        return result.get("final_analysis", {
            "probabilities": {"positive": 0.5, "negative": 0.5},
            "confidence": "low",
            "reasoning": ["Unable to generate analysis"]
        })

    def _should_continue_dialogue(self, state: AgentState) -> AgentTurn:
        if state["current_turn"] >= 3:  
            return AgentTurn.COMPLETE
        
        last_message = state["messages"][-1] if state["messages"] else None
        if last_message:
            if last_message["agent"] == "news":
                return AgentTurn.OPTION
            else:
                return AgentTurn.NEWS
        
        return AgentTurn.NEWS

    def _create_final_analysis(self, state: AgentState) -> AgentState:
        messages_summary = "\n".join([
            f"{msg['agent']}: {msg['content']}" 
            for msg in state["messages"]
        ])
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            Task: Provide a clear answer to the user's question based on the arguments from both agents.
            Your explanation should be built on facts presented by both agents.

            After analysis, format your final answer as a JSON string with this structure:
            {{
                "probabilities": {{
                    "positive": number between 0 and 1,
                    "negative": number between 0 and 1
                }},
                "confidence": "high" or "medium" or "low",
                "reasoning": ["reason 1", "reason 2", "reason 3"]
            }}

            Your response must be a valid JSON string. Base the probabilities and confidence on the strength
            of evidence from both agents. Include key reasoning points that led to your conclusion.
            """),
                    ("human", """User question: {user_request}
            Arguments from both agents: {models_argument}""")
                ])

        chain = prompt | self._llm
        response = chain.invoke({
            "user_request": state["user_request"],
            "models_argument": messages_summary
        })

        try:
            # Try to find JSON pattern
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                analysis_result = json.loads(json_match.group())
            else:
                # If no JSON found, format the response
                analysis_result = {
                    "probabilities": {"positive": 0.5, "negative": 0.5},
                    "confidence": "low",
                    "reasoning": [response.content.strip()]
                }
        except (json.JSONDecodeError, Exception) as e:
            analysis_result = {
                "error": str(e),
                "probabilities": {"positive": 0.5, "negative": 0.5},
                "confidence": "low",
                "reasoning": [f"Error occurred: {str(e)}"]
            }

        state["final_analysis"] = analysis_result
        return state

    def _create_news_workflow(self, data_frm: pd.DataFrame, event: str):
        workflow = StateGraph(AgentState)
        
        def get_top_news(state: AgentState) -> AgentState:
            agent = AgentTopNews()
            state["top_news"] = agent.get_top_news(state["user_request"])
            state["messages"] = []
            state["current_turn"] = 0
            return state

        def analyze_news(state: AgentState) -> AgentState:
            agent = NewsAnalysisAgent()
            
            if state["agent_option"]:
                if state["current_turn"] <= 5:
                    state["current_turn"] += 1
                    message = state["agent_option"]
                else:
                    return AgentTurn.COMPLETE
            else:
                message = state["user_request"]

            analysis = agent.analyze_news(message, state["top_news"])
            state["agent_news"] = "NEWS AGENT DEBATE: " + analysis
            state["messages"].append({
                "agent": "news",
                "content": analysis
            })
            return state

        def option_agent(state: AgentState) -> AgentState:
            agent = AgentOptionsAnalyzer(data_frm)
            if state["agent_news"]:
                if state["current_turn"] <= 5:
                    state["current_turn"] += 1
                    message = state["agent_news"]
                else:
                    return AgentTurn.COMPLETE
            else:
                message = state["user_request"]

            analysis = agent.analyze_and_debate(message, event)
            state["agent_option"] = "OPTIONS AGENT DEBATE: " + analysis
            state["messages"].append({
                "agent": "option",
                "content": analysis
            })
            return state

        # Add nodes and configure workflow
        workflow.add_node("get_top_news", get_top_news)
        workflow.add_node("analyze_news", analyze_news)
        workflow.add_node("option_agent", option_agent)
        workflow.add_node("create_final_analysis", self._create_final_analysis)
        
        workflow.set_entry_point("get_top_news")
        workflow.add_edge("get_top_news", "analyze_news")
        workflow.add_edge("analyze_news", "option_agent")
        
        workflow.add_conditional_edges(
            "option_agent",
            self._should_continue_dialogue,
            {
                AgentTurn.NEWS: "analyze_news",
                AgentTurn.OPTION: "option_agent",
                AgentTurn.COMPLETE: "create_final_analysis"
            }
        )
        
        workflow.set_finish_point("create_final_analysis")
        return workflow.compile()

# Example usage
if __name__ == "__main__":

    data_option = pd.read_csv("/Users/ios/Downloads/Telegram Desktop/polymarket_sample.csv")
    predictor = NewsAnalysisPredictorAgent()
    result = predictor.predict(
        question= "Israel withdraws from Gaza in 2025?",
        description="""This market will resolve to "Yes" if Israel announces it has ceased all ground operations within and has withdrawn all ground forces from Gaza between January 1 and December 31, 2025, 11:59 PM ET. Otherwise, this market will resolve to "No".
For this market to resolve to "Yes" it is sufficient that Israel announces its ground forces have withdrawn into or behind intended buffer zones, even if that zone is established on internationally recognized Palestinian territory.
The primary resolution source for this market will be information from the Israeli government, however a consensus of credible reporting will also be used.""",
        data_frm=data_option
    )
    print(result)