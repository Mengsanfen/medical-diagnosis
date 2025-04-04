from langchain_openai.chat_models.base import BaseChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = BaseChatOpenAI(
    model='deepseek-chat',
    openai_api_base='https://api.deepseek.com',
    temperature=0
)

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain

prompt1 = PromptTemplate.from_template(
    '我的名字叫{name}，项目开发团队主要做的人工智能与医学结合，请帮我起10个名字，包含创始人'
)

chain1 = LLMChain(llm=llm, prompt=prompt1, output_key = 'teams_names', verbose=True)

teams_names = chain1.predict(name='三分梦')

prompt2 = PromptTemplate.from_template(
    f'请从以下公司名字中，选择你认为最好的一个:\n {teams_names}'
)
chain2 = LLMChain(llm=llm, prompt=prompt2, verbose=True)
print(chain2.predict(teams_names=teams_names))

chain = SequentialChain(
    chains=[chain1, chain2],
    input_variables=['name'],
    verbose=True
)
result = chain.run({'name': '三分梦'})
print(result)