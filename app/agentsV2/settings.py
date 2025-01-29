import os

from app.utils import get_env


os.environ["OPENAI_API_KEY"]= get_env("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = get_env("TAVILY_API_KEY")

BASE_MODEL = "gpt-4o-mini"
MAIN_MODEL = "gpt-4o"
