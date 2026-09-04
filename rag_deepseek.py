import os
import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from openai import OpenAI

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
    #一个多语言的句子嵌入模型，适用于多种语言的文本表示和相似度计算。
)

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    name="stm32_multilingual"
)

query = input("\n请输入你的问题：")

query_vector = model.encode([query])

results = collection.query(
    query_embeddings=query_vector.tolist(),
    #tolist是将NumPy数组转换为Python列表的方法，以便与Chroma数据库进行交互。
    n_results=3
)

documents = results["documents"][0]

print("\n========== 找到的资料 ==========")

for i, document in enumerate(documents):
    print(f"\n--- 第 {i + 1} 个资料 ---")
    print(document)

    context = "\n\n".join(documents)
    #join 规定了每两个相邻的列表元素之间，都放一次 "\n\n"
    #即用 join 前的字符串作为分隔符，把列表中的元素连接成一个新的字符串

prompt = f"""
    请根据下面提供的资料回答问题。

    资料：
    {context}

    问题：
    {query}

    要求：
    1. 只根据提供的资料回答。
    2. 如果资料中没有答案，请明确说“资料中没有找到相关信息”。
    3. 请用中文回答。
    """

llm_client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

response = llm_client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

answer = response.choices[0].message.content

print("\n========== DeepSeek 回答 ==========")
print(answer)