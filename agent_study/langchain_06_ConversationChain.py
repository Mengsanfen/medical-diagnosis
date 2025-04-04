# Description: A simple example of a conversation chain.（简单对话场景）

from langchain_openai.chat_models.base import BaseChatOpenAI
from dotenv import load_dotenv
load_dotenv()
llm = BaseChatOpenAI(
    model='deepseek-chat',
    openai_api_base='https://api.deepseek.com',
    temperature=0
)

# 简单对话场景
# from langchain.chains import ConversationChain
#
# conversation = ConversationChain(llm=llm, verbose=True)
# # print(conversation.prompt.template)   # 库封装的模板提示词
#
# while True:
#     Input = input('User: ') # hello | 你叫什么名字
#     result = conversation.predict(input=Input)
#     print('Assistant: ', result)

# 修改提示词
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate

template = '''
下面是一段人类与人工智能的友好对话。人工智能是健谈的，并根据其上下文提供许多具体细节。如果人工智能不知道一个问题，就会如实回答不知道，请用中文回复。

当前对话：
{history}
User:{input}
Assistant:
'''
prompt = PromptTemplate.from_template(template)
# 默认会进行记忆累加历史对话
conversation = ConversationChain(llm=llm, prompt=prompt, verbose=True)
# print(conversation.prompt.template)

while True:
    human_input = input('User: ')
    result = conversation.predict(input=human_input)
    print('Assistant: ', result)
