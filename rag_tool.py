import chromadb
from sentence_transformers import SentenceTransformer

# 加载 Embedding 模型
model = SentenceTransformer("all-MiniLM-L6-v2")

# 连接之前已经建立好的 ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

# 获取之前建立的 STM32 文档集合
collection = client.get_or_create_collection(
    name="stm32_collection"
)

def search_stm32_docs(query, n_results=3):
    """
    搜索 STM32 技术文档。

    参数：
        query：用户的问题
        n_results：返回多少条相关资料

    返回：
        相关文档列表
    """

    # 把用户的问题转换成向量
    query_vector = model.encode([query])


    # 在 ChromaDB 中进行相似度检索
    results = collection.query(
        query_embeddings=query_vector.tolist(),
        n_results=n_results
    )


    # 取出检索到的文档
    documents = results["documents"][0]


    # 返回文档
    return documents


# 只有直接运行 rag_tool.py 时，下面的代码才会执行
if __name__ == "__main__":

    query = input("请输入问题：")

    documents = search_stm32_docs(query)

    print("\n========== RAG Tool 检索结果 ==========")

    for i, document in enumerate(documents):
        print(f"\n--- 第 {i + 1} 个结果 ---")
        print(document)