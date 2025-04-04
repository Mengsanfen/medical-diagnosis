from langchain.memory import ConversationBufferMemory
from langchain_openai.chat_models.base import BaseChatOpenAI
from dotenv import load_dotenv
from langchain.tools import Tool
from langchain.chains import LLMRequestsChain, LLMChain
from langchain.prompts import Prompt
from langchain.agents import initialize_agent
from langchain.agents import ZeroShotAgent, AgentExecutor

load_dotenv()
llm = BaseChatOpenAI(
    model="deepseek-chat",
    openai_api_base='https://api.deepseek.com',
    temperature=0,
)

def generic_func(query):
    prompt = Prompt.from_template('回答问题: {query}')
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    return llm_chain.run(query)

def search_func(query):
    prompt = Prompt.from_template('''
    请根据以下搜索结果，回答用户问题。
    搜索结果：
    {requests_result}
    问题：{query}
    ''')
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    llm_requests_chain = LLMRequestsChain(llm_chain=llm_chain)
    input = {
        'query': query,
        'url':'https://www.google.com/search?q='+query.replace(' ', '+'),
    }
    return llm_requests_chain.run(input)

tools = [
    Tool(
        name='通用大模型',
        func=generic_func,
        description='利用大模型自身能力，回答问题'
    ),
    Tool(
        name='搜索引擎',
        func=search_func,
        description='其他模型没有正确答案时，使用该工具'
    )
]

suffix = """Begin!
{chat_history}
Question: {input}
{agent_scratchpad}
"""

agent_prompt = ZeroShotAgent.create_prompt(
    tools,
    prefix="请用中文回答以下问题，可以使用以下工具：",
    suffix=suffix,
    input_variables=["input", "chat_history", "agent_scratchpad"],
)
llm_chain = LLMChain(llm=llm, prompt=agent_prompt, verbose=True)

memory = ConversationBufferMemory(memory_key="chat_history")
agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools)
agent_chain = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    memory=memory,
)

while True:
    human_input = input("问题: ")
    result = agent_chain.run(human_input)
    print('答案: ', result, '\n')