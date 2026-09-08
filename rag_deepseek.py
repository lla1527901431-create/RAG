import os
import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from openai import OpenAI


# =========================
# 1. 加载环境变量
# =========================

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")


# =========================
# 2. 加载 Embedding 模型
# =========================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
    #一个多语言的句子嵌入模型，适用于中文、英文等多种语言的文本相似度计算。
)


# =========================
# 3. 连接 ChromaDB
# =========================

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    name="stm32_collection"
)


# =========================
# 4. 创建 DeepSeek 客户端
# =========================

llm_client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)


# =========================
# 5. 循环提问
# =========================

while True:

    query = input("\n请输入你的问题：")

    # 如果输入 exit，就退出程序
    if query.lower() == "exit":
        print("程序结束。")
        break

    # =========================
    # 6. 把问题转换成向量
    # =========================

    query_vector = model.encode([query])

    # =========================
    # 7. 从 ChromaDB 检索资料
    # =========================

    results = collection.query(
        query_embeddings=query_vector.tolist(),
        n_results=3
    )

    documents = results["documents"][0]

    '''
    print("\n========== 找到的资料 ==========")

    for i, document in enumerate(documents):
        print(f"\n--- 第 {i + 1} 个资料 ---")
        print(document)
    '''

    # =========================
    # 8. 把检索结果组合成 Context
    # =========================

    context = "\n\n".join(documents)

    # =========================
    # 9. 创建 Prompt
    # =========================

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

    # =========================
    # 10. 调用 DeepSeek
    # =========================

    response = llm_client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # =========================
    # 11. 获取 DeepSeek 回答
    # =========================

    answer = response.choices[0].message.content

    print("\n========== DeepSeek 回答 ==========")
    print(answer)