from langchain_openai.chat_models.base import BaseChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = BaseChatOpenAI(
    model='deepseek-chat',
    openai_api_base='https://api.deepseek.com',
    temperature=0
    )

# 直接调用模型，结果错误
# print(llm.predict('3.14 ^ 6.5'))

# 调用内置agent
from langchain.agents import load_tools, initialize_agent, get_all_tool_names

tools = load_tools(['llm-math'], llm=llm)
agent = initialize_agent(tools, llm=llm)

print(agent.run('3.14 ^ 6.5'))
# print(get_all_tool_names())
# 内置工具不能满足业务需求，需要结合业务场景来自定义工具

# 自定义工具
from langchain.agents import initialize_agent, get_all_tool_names
from datetime import datetime
from langchain.tools import Tool

def get_current_time(query):
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

tools = [Tool(
    name='get_current_time',
    func=get_current_time,
    description='获取当前日期时间'
)]

agent = initialize_agent(tools, llm=llm, verbose=True)
result = agent.run('现在时间是多少')
print(result)