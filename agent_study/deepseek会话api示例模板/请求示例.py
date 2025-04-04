import requests
import json

url = "https://api.deepseek.com/chat/completions"

payload = json.dumps({
  "messages": [                                   # 对话历史（AI 靠这个记住上下文！）
    {
      "content": "You are a helpful assistant",   # system 可以设定 AI 的性格 (●'◡'●)
      "role": "system"
    },
    {
      "content": "Hi",
      "role": "user"
    }
  ],
  "model": "deepseek-chat",                       # 指定 AI 模型
  "frequency_penalty": 0,                         # 减少重复词（-2.0~2.0 🚗💨）
  "max_tokens": 2048,                             # 限制回答长度（防止 AI 变话痨 💦）
  "presence_penalty": 0,                          # 减少重复话题（-2.0~2.0，让 AI 别老提同一件事 🗣️）
  "response_format": {                            # 控制返回格式
    "type": "text"
  },
  "stop": None,                                   # 遇到这些词就刹车（比如 ["。", "\n"] 让 AI 别写太长 🛑）
  "stream": False,                                # 流式传输（让 AI 一小段一小段地往外蹦，像真人聊天 💬✨）
  "stream_options": None,
  "temperature": 1,                               # 控制 AI 的「脑洞大小」：0=保守老实 / 1=放飞自我
  "top_p": 1,                                     # 让 AI 更专注 or 更发散（0~1，越小越保守 🤔）
  "tools": None,
  "tool_choice": "none",
  "logprobs": False,                              # 返回 token 概率（适合调试，看看 AI 怎么“想”的 🤖💭）
  "top_logprobs": None
})
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer <TOKEN>'               # <TOKEN> 替换为你的 API KEY
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

## 响应示例


# {
#   "id": "dabac278-942d-4939-bd8a-c4c6df80569d",   # 本次聊天的唯一ID 🧾
#   "object": "chat.completion",
#   "created": 1743387813,                          # 生成时间戳，精确到你眨眼的瞬间 👀💫
#   "model": "deepseek-chat",                       # 用的哪个AI模型，这里是你的聪明小DeepSeek 🤖
#   "choices": [                                    # 最重要的部分！AI的回复藏在这里 🎁
#     {
#       "index": 0,
#       "message": {
#         "role": "assistant",
#         "content": "Hello! How can I assist you today? 😊" # AI的卖萌回答！
#       },
#       "logprobs": null,
#       "finish_reason": "stop"                     # 结束原因："stop"=正常结束 🛑/"length"=字数到了 ✂️
#     }
#   ],
#   "usage": {                                      # 你的"算力小票"🧾
#     "prompt_tokens": 9,
#     "completion_tokens": 11,
#     "total_tokens": 20,
#     "prompt_tokens_details": {
#       "cached_tokens": 0
#     },
#     "prompt_cache_hit_tokens": 0,
#     "prompt_cache_miss_tokens": 9
#   },
#   "system_fingerprint": "fp_3d5141a69a_prod0225"
# }
