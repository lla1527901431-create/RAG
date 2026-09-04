#multilingual指的是多语言的意思，rag_multilingual.py是一个多语言的RAG
import fitz
import chromadb
from sentence_transformers import SentenceTransformer


# =========================
# 1. 读取 PDF
# =========================

pdf = fitz.open("documents/STM32.pdf")

text = ""

for page in pdf:
    text += page.get_text()

pdf.close()

print("PDF 文本长度：", len(text))
# =========================
# 2. 切分文本
# =========================

def split_text(text, chunk_size=500, overlap=50):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start = end - overlap

    return chunks


chunks = split_text(text)

print("Chunk 数量：", len(chunks))
# =========================
# 3. 加载多语言 Embedding 模型
# =========================

model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)
# =========================
# 4. 创建新的 Chroma 数据库
# =========================

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="stm32_multilingual"
)
# =========================
# 5. 生成 Chunk 向量
# =========================

print("正在生成 Embedding，请稍等...")

vectors = model.encode(
    chunks,
    show_progress_bar=True
)

print("Embedding 完成！")
# =========================
# 6. 创建 Chunk ID
# =========================

ids = []

for i in range(len(chunks)):
    ids.append(f"chunk_{i}")
    # =========================
# 7. 写入向量数据库
# =========================

if collection.count() == 0:

    collection.add(
        documents=chunks,
        embeddings=vectors.tolist(),
        ids=ids
    )

    print("向量库建立完成！")

else:

    print("向量库已经存在，跳过写入。")


print("数据库中的数据数量：", collection.count())
# =========================
# 8. 用户提问
# =========================

query = input("\n请输入你的问题：")


# =========================
# 9. 把中文问题转换成向量
# =========================

query_vector = model.encode([query])


# =========================
# 10. 从向量数据库检索
# =========================

results = collection.query(
    query_embeddings=query_vector.tolist(),
    n_results=3
)


# =========================
# 11. 显示检索结果
# =========================

print("\n========== 检索结果 ==========")

for i, document in enumerate(results["documents"][0]):

    print(f"\n--- 第 {i + 1} 个结果 ---")

    print(document)