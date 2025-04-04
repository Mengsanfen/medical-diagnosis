from openai import OpenAI

# 使用dotenv加载.env文件里的api配置
# from dotenv import load_dotenv
# load_dotenv()

# 如果是硅基流动的话是这样
client = OpenAI(api_key='sk-ilbtqvggcrtvqqavtgdkpeuqxioelwtwwvxfjrwqcwhvnvlu', base_url="https://api.siliconflow.cn/v1")

response = client.chat.completions.create(
  model="Qwen/QwQ-32B",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  stream=True, # 是否流式输出
)

for item in response:
    content = item.choices[0].delta.content
    if content is not None:
        print(content, end='')