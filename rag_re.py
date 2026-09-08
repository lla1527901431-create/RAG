import pymupdf as fitz
import chromadb
import re
from sentence_transformers import SentenceTransformer
from typing import List
import os


# =========================
# 1. 读取 PDF
# =========================

pdf = fitz.open("documents/STM32.pdf")

text = ""

for page in pdf:
    text += page.get_text()

pdf.close()


# =========================
# 2. 切分文本
# =========================

def split_sentences(text):
    """
    使用正则表达式把文本分成一个个句子。
    """

    sentences = re.split(r'(?<=[.!?])\s+', text)

    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    return sentences


def chunk_by_sentence(
    text,
    max_chars=500,
    overlap_sentences=1
):
    """
    根据句子进行文本分块。

    参数：
        text：原始文本
        max_chars：每个 Chunk 最大字符数
        overlap_sentences：相邻 Chunk 重叠几个句子
    """

    sentences = split_sentences(text)

    chunks = []
    current_chunk = []

    for sentence in sentences:

        current_length = sum(len(s) for s in current_chunk)

        if current_length + len(sentence) <= max_chars:
            current_chunk.append(sentence)

        else:
            if current_chunk:
                chunks.append(" ".join(current_chunk))

            current_chunk = current_chunk[-overlap_sentences:]
            current_chunk.append(sentence)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

chunks = chunk_by_sentence(
    text,
    max_chars=500,
    overlap_sentences=1
)


# =========================
# 3. 加载 Embedding 模型
# =========================

model = SentenceTransformer("all-MiniLM-L6-v2")


# =========================
# 4. 创建 Chroma 数据库
# =========================

client = chromadb.PersistentClient(
    #client 用于操作Chroma数据库
    #PersistentClient 用于创建持久化的 Chroma 数据库    
    #EphemeralClient 用于创建临时的 Chroma 数据库
    path="./chroma_db"
    #path 用于指定数据库的存储路径，后面引号内的是数据库的存储路径
)

collection = client.get_or_create_collection(
    name="stm32_collection"
)


# =========================
# 5. 把 Chunk 存进向量数据库
# =========================

# 把所有 Chunk 转换成向量
vectors = model.encode(chunks)

# 为每个 Chunk 创建唯一 ID
ids = []
for i in range(len(chunks)):
    ids.append(f"chunk_{i}")

# Chroma 一次最多处理 5461 条
# 所以我们分批写入
batch_size = 5000

for start in range(0, len(chunks), batch_size):

    end = start + batch_size

    collection.add(
        documents=chunks[start:end],
        embeddings=vectors[start:end].tolist(),
        ids=ids[start:end]
    )

    print(f"已经写入 {min(end, len(chunks))} / {len(chunks)} 条数据")

print("向量库建立完成！")
print("数据库中的数据数量：", collection.count())

'''
# =========================
# 6. 用户提问
# =========================

query = input("\n请输入你的问题：")


# =========================
# 7. 把问题转换成向量
# =========================

query_vector = model.encode([query])


# =========================
# 8. 从向量数据库检索
# =========================

results = collection.query(
    query_embeddings=query_vector.tolist(),
    n_results=3
)


# =========================
# 9. 显示检索结果
# =========================

print("\n========== 检索结果 ==========")

for i, document in enumerate(results["documents"][0]):

    print(f"\n--- 第 {i + 1} 个结果 ---")

    print(document)
'''