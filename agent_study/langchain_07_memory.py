# Description: A simple example of a conversation chain.（简单对话场景）
from langchain.memory import (ConversationBufferMemory,
                                       ConversationBufferWindowMemory,
                                       ConversationSummaryBufferMemory,
                                       ConversationSummaryMemory)

from langchain_openai.chat_models.base import BaseChatOpenAI
from dotenv import load_dotenv
load_dotenv()
llm = BaseChatOpenAI(
    model='deepseek-chat',
    openai_api_base='https://api.deepseek.com',
    temperature=0
)

from langchain.chains import ConversationChain

conversation = ConversationChain(llm=llm, verbose=True)

# 只保留两轮 history
memory = ConversationBufferWindowMemory(k=2)
conversation = ConversationChain(llm=llm, memory=memory, verbose=True)

# 其他常用Memory
# memory = ConversationBufferMemory() # 保留完整会话（默认）
# memory = ConversationBufferWindowMemory(k=2)    # 保留前k轮对话
# memory = ConversationSummaryMemory(llm=llm)     # 总结前面的对话内容
# memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=100)    # 超过最大token数量的会话，会被总结

result = conversation.predict(input="你好，我是王宇翔，你是谁呢")