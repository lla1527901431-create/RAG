from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")


text_a = "STM32 的 ADC 分辨率是 12 位。"
text_b = "STM32 的 ADC 是 12-bit 模数转换器。"
text_c = "今天晚上我要吃火锅。"


vector_a = model.encode([text_a])
vector_b = model.encode([text_b])
vector_c = model.encode([text_c])


similarity_ab = cosine_similarity(vector_a, vector_b)
similarity_ac = cosine_similarity(vector_a, vector_c)


print("A 和 B 的相似度：", similarity_ab[0][0])
print("A 和 C 的相似度：", similarity_ac[0][0])