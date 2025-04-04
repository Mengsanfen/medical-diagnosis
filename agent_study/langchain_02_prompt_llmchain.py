from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()

from langchain_openai.chat_models.base import BaseChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

llm = BaseChatOpenAI(
    model="deepseek-chat",
    openai_api_base='https://api.deepseek.com')

template = '写一首描写{sence}的诗'

prompt = PromptTemplate.from_template(template)
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.predict(sence='秋天')

print(result)
