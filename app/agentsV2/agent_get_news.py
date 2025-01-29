import json
import os
from typing import Annotated, List, Dict

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import Tool,tool
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from app.agentsV2.settings import BASE_MODEL, MAIN_MODEL

class NewsAnalysisAgent:
    @staticmethod
    @tool
    def fetch_and_summarize_news(question: Annotated[str, "User question about news"]) -> str:
        """
        Fetch news from the internet and provide a summary for decision-making.
        """

        global analytics_result_llm

        llm = ChatOpenAI(model=BASE_MODEL)

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
            Task #1:
            Summarize news based on the user's request.
            User query: {question}
            Make sure to include all key points.
            """),
            ("human", "{news}")
        ])

        chain = prompt | llm

        search_tool = TavilySearchResults(
            max_results=10,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=True,
            include_images=False
        )

        final_query = question + f" Use these sources: {top_news}"
        urls = search_tool.invoke({"query": final_query})
        print(f"Using top sources: {top_news}")

        all_text = ""
        for index, url in enumerate(urls, 1):
            try:
                domain = url['url'].split("/")[2]
                text_to_summarize = f"NEWS URL {domain}\n\n{url['content']}\n\n"
                generated_text = chain.invoke({"news": text_to_summarize}).content
                all_text += generated_text
            except KeyError as e:
                print(f"Error processing URL {url['url']}: {e}")

        summary_text = chain.invoke({"news": all_text}).content
        analytics_result_llm = summary_text

        return summary_text

    @staticmethod
    @tool
    def generate_positive_and_negative_queries(query: Annotated[str, "User request"]) -> Annotated[List[str], "List of queries in different tones"]:
        """
        Generate positive and critical search queries for the given topic.
        """
        llm = ChatOpenAI(model=BASE_MODEL)

        prompt = PromptTemplate(
            input_variables=["user_query"],
            template="""
            Your task is to create two search query variants for the same topic:
            1. A POSITIVE query that highlights potential benefits and successes.
            2. A CRITICAL query that emphasizes risks and issues.

            User query: "{user_query}"

            Positive query should:
            - Use optimistic phrasing
            - Focus on potential benefits
            - Be constructive and hopeful

            Critical query should:
            - Be skeptical
            - Highlight potential downsides
            - Be analytical and cautious

            Generate two queries:
            1. POSITIVE query:
            2. CRITICAL query:
            """
        )

        chain = prompt | llm

        response = chain.invoke({"user_query": query})
        return [line.split(":")[1].strip() for line in response.content.split("\n") if ":" in line]
    
    @staticmethod
    @tool
    def debate_analysis_tool(debate_question: Annotated[str, "Question from another agent in the debate"]) -> str:
        """
        Provide a detailed analysis of arguments from another agent in a debate.
        """
        llm = ChatOpenAI(model=BASE_MODEL)

        prompt = PromptTemplate(
            input_variables=["analytics_result", "debate_question"],
            template="""
            Your task is to provide a detailed response to another LLM agent's question.
            Use specific facts and explain whether you agree or disagree with their argument.
            Your analysis: {analytics_result}
            The other agent's argument: {debate_question}
            """
        )

        chain = prompt | llm

        return chain.invoke({
            "analytics_result": analytics_result_llm,
            "debate_question": debate_question
        }).content

    def create_news_analysis_agent(self) -> AgentExecutor:
        """
        Create an agent for multi-step news analysis:
        1. Rephrase user query.
        2. Search news from different perspectives.
        3. Summarize results.
        4. Verify the reliability of sources.
        """
        llm = ChatOpenAI(model=MAIN_MODEL, temperature=0.2)

        tools = [
            Tool(name="Rephrase_Query", func=self.generate_positive_and_negative_queries, description="Generate positive and critical query variants"),
            Tool(name="Internet_Search", func=self.fetch_and_summarize_news, description="Fetch and summarize news"),
            Tool(name="Debate_Tool", func=self.debate_analysis_tool, description="Analyze and respond to debates")
        ]

        system_prompt = """You are an analytical agent assisting users in obtaining comprehensive information by evaluating various perspectives.
        Follow these tasks:
        1. Create alternative search queries.
        2. Gather objective data.
        3. Critically analyze the findings.
        4. Provide a balanced and unbiased analysis.
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
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

    def analyze_news(self, query: str, top_url: str) -> str:
        """
        Perform news analysis for a given query and URL.
        """
        global top_news
        top_news = " ".join(top_url.split("\n")).replace("*", "")

        news_agent = self.create_news_analysis_agent()
        result = news_agent.invoke({"input": query})
        return result["output"]
    

if __name__ == "__main__":
    user_req = "Will Spartak win the upcoming match?"
    news_agent = NewsAnalysisAgent()
    top_news = news_agent.analyze_news(user_req, "LIST OF NEWS")
