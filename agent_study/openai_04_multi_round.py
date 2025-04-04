from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(base_url="https://api.deepseek.com")


messages = []

while True:
    content = input("User: ")
    messages.append({'role':'user', 'content':content})
    print(messages)
    # exit()

    response = client.chat.completions.create(
      model="deepseek-chat",
      messages=messages
    )
    asst_content = response.choices[0].message.content
    messages.append({'role':'Assistant', 'content':asst_content})
    print('Assistant: ', asst_content)
    print(messages)