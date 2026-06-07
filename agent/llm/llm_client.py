from agent.config.settings import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from langchain_openai import ChatOpenAI
from pydantic.types import SecretStr

llm = ChatOpenAI(
    model=DEEPSEEK_MODEL,
    api_key=SecretStr(DEEPSEEK_API_KEY),
    base_url=DEEPSEEK_BASE_URL,
    temperature=0.7,
)
