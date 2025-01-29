import os
import pandas as pd
import numpy as np
from typing import Annotated, Dict, List, Optional, Sequence

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.tools import tool, Tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from app.agentsV2.settings import BASE_MODEL


class AgentOptionsAnalyzer:
    analytics_result_llm = None
    current_event = None

    def __init__(self, market_data):
        """
        Initializes the market analysis agent.
        Loads and processes trading data.
        """
        self.df = market_data
        self.clean_data()

    @staticmethod
    @tool
    def llm_analytics(event_name: Annotated[str, "String question from user"]) -> str:
        """
        Use this tool to provide detailed analytics for a given question.
        """
        llm = ChatOpenAI(model=BASE_MODEL)

        prompt = PromptTemplate(
            input_variables=["analytics", "user_query", "event"],
            template="""Analyze market data for event: {event}
                       Provide insights based on this analytics:
                       {analytics}
                       Answer question: {user_query}"""
        )

        chain = prompt | llm 

        res = chain.invoke({
            "analytics": str(AgentOptionsAnalyzer.analytics_result_llm),
            "user_query": str(event_name),
            "event": str(AgentOptionsAnalyzer.current_event)
        })

        AgentOptionsAnalyzer.analytics_result_llm = res.content
        
        return AgentOptionsAnalyzer.analytics_result_llm

    @staticmethod
    @tool
    def debate_tool(argument: Annotated[str, "Argument from other agent"]) -> str:
        """
        Tool for debating with another agent using market data insights.
        """
        llm = ChatOpenAI(model=BASE_MODEL)

        prompt = PromptTemplate(
            input_variables=["analytics", "argument"],
            template="""Counter or support this argument using market analytics:
                       Argument: {argument}
                       
                       Market Analytics:
                       {analytics}
                       
                       Provide detailed response with numerical evidence:"""
        )

        chain = prompt | llm

        res = chain.invoke({
            "analytics": str(AgentOptionsAnalyzer.analytics_result_llm),
            "argument": str(argument)
        })
        
        return res.content

    def clean_data(self):
        """
        Cleans and processes market data.
        """
        if 'Unnamed: 0' in self.df.columns:
            self.df.drop(columns=['Unnamed: 0'], inplace=True)
        
        # Исправленный парсинг даты
        try:
            self.df['date'] = pd.to_datetime(
                self.df['date'], 
                format='%m-%d-%Y %H:%M',  # Новый формат для MM-DD-YYYY HH:MM
                errors='coerce'
            )
        except ValueError:
            self.df['date'] = pd.to_datetime(
                self.df['date'], 
                format='%d-%m-%Y %H:%M',  # Альтернативный формат
                errors='coerce'
            )
        
        # Заполнение пропусков
        self.df['date'].ffill(inplace=True)
        
        for col in ['yes', 'no']:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            self.df[col].fillna(method='ffill', inplace=True)

    def get_analytics(self) -> Dict[str, dict]:
        """
        Performs market data analysis including trends, volatility and correlations.
        """
        analytics = {
            'price_analysis': {},
            'trend_analysis': {},
            'volatility': {},
            'correlations': {}
        }

        # Анализ ценовых данных
        for outcome in ['yes', 'no']:
            series = self.df[outcome]
            analytics['price_analysis'][outcome] = {
                'current': round(series.iloc[-1], 3),
                '30d_mean': round(series.tail(30).mean(), 3),
                'all_time_high': round(series.max(), 3),
                'all_time_low': round(series.min(), 3),
                'last_change_pct': round((series.iloc[-1] - series.iloc[-2])/series.iloc[-2]*100, 2)
            }

        # Анализ трендов
        analytics['trend_analysis'] = self._calculate_trends()

        # Волатильность
        for outcome in ['yes', 'no']:
            analytics['volatility'][outcome] = round(
                self.df[outcome].pct_change().std() * np.sqrt(365), 4  # Годовая волатильность
            )

        # Корреляции
        analytics['correlations'] = {
            'yes_no': round(self.df['yes'].corr(self.df['no']), 2)
        }

        return analytics

    def _calculate_trends(self) -> dict:
        """
        Calculates price trends using moving averages.
        """
        trends = {}
        window_size = min(7, len(self.df))
        
        for outcome in ['yes', 'no']:
            series = self.df[outcome]
            short_ma = series.rolling(window=window_size).mean()
            long_ma = series.rolling(window=window_size*2).mean()
            
            trends[outcome] = {
                'trend': 'upward' if short_ma.iloc[-1] > long_ma.iloc[-1] else 'downward',
                'momentum': 'increasing' if series.iloc[-1] > short_ma.iloc[-1] else 'decreasing'
            }
        
        return trends

    def create_market_agent(self) -> AgentExecutor:
        """
        Creates an agent specialized in market data analysis.
        """
        llm = ChatOpenAI(model=BASE_MODEL, temperature=0.2)

        tools = [
            Tool(
                name="Market_Debate",
                func=self.debate_tool,
                description="Use for debates about market predictions"
            ),
            Tool(
                name="Market_Analytics",
                func=self.llm_analytics,
                description="Provides analysis of prediction market trends"
            )
        ]

        system_prompt = """
        You are a prediction market analyst. Follow these steps:
        1. Use Market_Analytics to get market insights
        2. Use Market_Debate to discuss arguments
        3. Always reference numerical data in responses
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
            max_iterations=4,
            handle_parsing_errors=True
        )

    def analyze_and_debate(self, query: str, event_description: str) -> str:
        """
        Executes full analysis and debate cycle for market data.
        """
        try:
            AgentOptionsAnalyzer.current_event = event_description
            analysis = self.get_analytics()
            AgentOptionsAnalyzer.analytics_result_llm = str(analysis)

            market_agent = self.create_market_agent()
            result = market_agent.invoke({"input": query})
            
            return result["output"]
        except Exception as e:
            return f"Analysis error: {str(e)}"

if __name__ == "__main__":
    try:
        csv_file_read= pd.read_csv("/Users/ios/Downloads/Telegram Desktop/polymarket_sample.csv")
        user_query = "Israel withdraws from Gaza in 2025?"
        event_name = """This market will resolve to "Yes" if Israel announces it has ceased all ground operations within and has withdrawn all ground forces from Gaza between January 1 and December 31, 2025, 11:59 PM ET. Otherwise, this market will resolve to "No".
For this market to resolve to "Yes" it is sufficient that Israel announces its ground forces have withdrawn into or behind intended buffer zones, even if that zone is established on internationally recognized Palestinian territory.
The primary resolution source for this market will be information from the Israeli government, however a consensus of credible reporting will also be used."""
        
        analyzer = AgentOptionsAnalyzer(market_data=csv_file_read)
        result = analyzer.analyze_and_debate(user_query, event_name)
        print("Analysis Result:")
        print(result)
    except Exception as e:
        print(f"Error in main execution: {str(e)}")