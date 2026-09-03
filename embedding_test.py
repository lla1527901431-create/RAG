from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")

text = "STM32 的 ADC 分辨率是 12 位。"

vector = model.encode(text)

print("向量类型：", type(vector))
print("向量维度：", vector.shape)
print("向量内容：", vector)