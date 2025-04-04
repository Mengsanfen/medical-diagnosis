import tiktoken

encoding = tiktoken.encoding_for_model('')

# 去掉Key，只保留Value
messages = [
    {"system", "You are a helpful asistant."},
    {"user", "Hello"},
]

print(f'Prompt_Tokens: {len(encoding.encode(str(messages)))}')