# 大模型开发之命名体识别

from langchain_openai.chat_models.base import BaseChatOpenAI
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

load_dotenv()
llm = BaseChatOpenAI(
    model="deepseek-chat",
    openai_api_base='https://api.deepseek.com',
    temperature=0,
    )
# 定义实体字段
# 类型：list, string, number
response_schemas = [
    ResponseSchema(type='list', name="disease", description="疾病名称实体"),
    ResponseSchema(type='list',name="symptom", description="疾病症状实体"),
    ResponseSchema(type='list',name="drug", description="药物名称实体"),
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()
# print(format_instructions)

# 内置提示词
template = '''
1、从以下用户输入的句子中，提取实体内容
2、仅根据用户输入抽取，不要推理，不要补充信息。
3、注意json格式，在json中不要出现//
4、如果字段名称为空，也需要保留字段名称。

{format_instructions}

用户输入: {input}

输出: 
'''

prompt = PromptTemplate(
    template=template,
    partial_variables={"format_instructions": format_instructions},
    input_variables=["input"],
)

# prompt = prompt.format(input='感冒是一种什么病？')
# print(prompt)

from langchain.chains import LLMChain

chain = LLMChain(llm=llm, prompt=prompt)

# llm_output = chain.run(input='胃痛是一种什么病?可以吃什么药缓解?') # {'disease': ['胃痛'], 'symptom': [], 'drug': []} <class 'dict'>
llm_output = chain.run(input='感冒是一种什么病？会咳嗽，吃感冒灵可以缓解吗')

output = output_parser.parse(llm_output)
print(output, type(output))
# {'disease': ['感冒'], 'symptom': ['咳嗽'], 'drug': ['感冒灵']} <class 'dict'>