import os
from typing import Annotated, Dict, List, Optional, Sequence

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.tools import tool, Tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from app.agentsV2.settings import BASE_MODEL

class AgentTopNews:
    """Agent class for analyzing and retrieving top news sources."""
    
    @staticmethod
    @tool
    def query_reframing(query: Annotated[str, "User request"]) -> str:
        """
        Reframe the user's query to better capture broader aspects of the topic.

        Args:
            query: The original user query to be reframed.

        Returns:
            str: The reframed query optimized for news source search.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            Task: Using this format, reframe the following query to cover broader aspects
            of the topic for finding top sites.
            
            Based on the user's query, reframe it to cover broader aspects of the topic.
            The reframed query should contain keywords and related topics that will help
            find the most authoritative and relevant sources.

            For example:
            Input: "Will Bitcoin reach 100k"
            Output: "Top sites about cryptocurrencies, Bitcoin and price predictions"

            Input: "Will Spartak become champion?"
            Output: "Top sites about football, Russian football clubs and championship predictions"

            Input: "What are oil price forecasts for 2025?"
            Output: "Top sites about commodity markets, oil and energy resource price forecasts"

            Input: "Best investment strategies in 2025"
            Output: "Top sites about investments, financial strategies and economic forecasts"
            """),
            ("human", "{request_from_user}")
        ])

        llm = ChatOpenAI(
            model=BASE_MODEL,
            temperature=0.2
        )

        chain = prompt | llm
        response = chain.invoke({"request_from_user": query})
        return response.content

    @staticmethod
    @tool
    def top_web_urls(query: Annotated[str, "Reframing Query"]) -> str:
        """
        Retrieve and analyze top websites based on the reframed query.

        Args:
            query: The reframed search query.

        Returns:
            str: Analyzed list of top websites.
        """
        all_content = ""
        search_tool = TavilySearchResults(
            max_results=10,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=True,
            include_images=False
        )

        search_results = search_tool.invoke({"query": query})
        all_content = "\n".join(
            result["content"] for result in search_results
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "List the top 10 most trustworthy websites that should be prioritized.Only websites names"),
            ("human", "{contents}")
        ])

        llm = ChatOpenAI(
            model=BASE_MODEL,
            temperature=0.2
        )

        chain = prompt | llm
        response = chain.invoke({"contents": all_content})
        return response.content

    def create_news_agent(self) -> AgentExecutor:
        """
        Create an agent for analyzing top news sources.

        Returns:
            AgentExecutor: Configured agent executor for news analysis.
        """
        llm = ChatOpenAI(model=BASE_MODEL, temperature=0.9)

        tools = [
            Tool(
                name="Query_Reframing",
                func=self.query_reframing,
                description="Reframing user query for site search"
            ),
            Tool(
                name="Top_urls",
                func=self.top_web_urls,
                description="Get list of top news channels"
            )
        ]

        system_prompt = """
        Your task is to find and evaluate the most reliable news and analytical websites
        for queries related to the user's topic and list these websites.
        Do not answer the user's question!
        Strictly provide only the list of websites top 10!

        Output example:
        Jonsen, NewNews and other 
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        agent = create_tool_calling_agent(
            llm=llm,
            tools=tools,
            prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=5
        )

    def get_top_news(self, user_request: str) -> str:
        """
        Analyze news sources based on user request.

        Args:
            user_request: The user's original query.

        Returns:
            str: Analysis results including top news sources.
        """
        news_agent = self.create_news_agent()
        result = news_agent.invoke({"input": user_request})
        return result["output"]



if __name__ == "__main__":
    try:
        user_req = "Will Spartak win their next match?"
        news_agent = AgentTopNews()
        top_news = news_agent.get_top_news(user_req)
        print("Top News Sources:")
        print(top_news)
    except Exception as e:
        print(f"Error during execution: {str(e)}")