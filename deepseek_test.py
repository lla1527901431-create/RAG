from openai import OpenAI
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {
            "role": "user",
            "content": "请用一句话解释什么是 RAG。"
        }
    ]
)

print("AI回答：")
print(response.choices[0].message.content)

print("\nToken 使用情况：")
print("输入 Token：", response.usage.prompt_tokens)
print("输出 Token：", response.usage.completion_tokens)
print("总 Token：", response.usage.total_tokens)