import chromadb


client = chromadb.PersistentClient(path="./chroma_db")


collection = client.get_or_create_collection(
    name="test_collection"
)


texts = [
    "STM32 的 ADC 分辨率是 12 位。",
    "STM32 的 GPIO 可以配置为输入或者输出。",
    "今天晚上我要吃火锅。"
]


collection.add(
    documents=texts,
    ids=["text_1", "text_2", "text_3"]
)


print("向量库创建成功！")
print("数据数量：", collection.count())
query_text = "STM32 ADC 12 位"

results = collection.query(
    query_texts=[query_text],
    n_results=1
)

print("查询问题：", query_text)
print("最相关的内容：", results["documents"])