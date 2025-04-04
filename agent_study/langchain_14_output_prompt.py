# 大模型开发之输出提示词重写
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

def structured_output_parser(response_schemas):
    text = '''
    请从以下文本中，抽取出实体信息，并按json格式返回，json包含首尾的"```json" 和 "```":
    以下是字段含义和类型，要求保留所有字段:
    '''
    for schema in response_schemas:
        text += schema.name + ' 字段，表示: ' + schema.description + ' 类型: ' + schema.type + '\n'
        return text

response_schemas = [
    ResponseSchema(type='list', name="disease", description="疾病名称实体"),
    ResponseSchema(type='list',name="symptom", description="疾病症状实体"),
    ResponseSchema(type='list',name="drug", description="药物名称实体"),
]

format_instructions = structured_output_parser(response_schemas)

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

template = '''
1、从以下用户输入的句子中，提取实体内容
2、仅根据用户输入抽取，不要推理，不要补充信息
{format_instructions}
____________________
用户输入: {input}
____________________
输出:
'''

prompt = PromptTemplate(
    template=template,
    partial_variables={"format_instructions": format_instructions},
    input_variables=["input"],
)

from langchain.chains import LLMChain

chain = LLMChain(llm=llm, prompt=prompt)

llm_output = chain.run(input='胃痛是一种什么病?可以吃什么药缓解?')
print(llm_output, type(llm_output))