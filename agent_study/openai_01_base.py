from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# 如果是deepseek的话是这样
client = OpenAI(base_url="https://api.deepseek.com")

response = client.chat.completions.create(
  model="deepseek-chat",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  stream=False,
  max_tokens=100,
  temperature=0,
  n=1,
)

print(response.choices[0].message.content)