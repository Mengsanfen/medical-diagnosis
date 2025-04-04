from langchain_openai.chat_models.base import BaseChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = BaseChatOpenAI(model='deepseek-chat', temperature=0)

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.prompts import FewShotPromptTemplate

examples = [
    {'sence':'秋天', 'type':'五言绝句',  'text':'床前明月光，疑是地上霜。\n举头望明月，低头思故乡。'},
    {'sence':'冬天', 'type':'七言律诗', 'text':'窗前明月光，疑是地上霜。\n举头望明月，低头思故乡。'}
]

example_template = '这是一首描写{sence}的诗，格式为{type}:\n{text}'
# example_prompt = PromptTemplate(
#     input_variables=['sence', 'type', 'text'],
#     template=example_template
# )
example_prompt = PromptTemplate.from_template(example_template)

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix='写一首描写{sence}的诗',
    suffix='\n\n{format_instructions}\n\n{query}',
    input_variables=['sence', 'type'],
    example_separator='\n\n',
    # format_example_prompt=example_prompt,
    # format_instructions='请将格式化为{type}',
    # validate_template=True,
    # template_format='f
)

print(prompt.fromat(sence='秋天', type='七言律诗'))