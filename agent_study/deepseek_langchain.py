from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    model='deepseek-chat',
    openai_api_base='https://api.deepseek.com',
    max_tokens=1024
)

response = llm.invoke("Hi!")
print(response.content)