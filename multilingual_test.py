from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# 加载多语言 Embedding 模型
model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)


# 中文问题
text_chinese = "STM32 的 ADC 分辨率是多少？"


# 英文问题
text_english = "What is the resolution of the STM32 ADC?"


# 完全无关的问题
text_other = "What should I eat for dinner tonight?"


# 转换成向量
vector_chinese = model.encode([text_chinese])
vector_english = model.encode([text_english])
vector_other = model.encode([text_other])


# 计算相似度
similarity_chinese_english = cosine_similarity(
    vector_chinese,
    vector_english
)

similarity_chinese_other = cosine_similarity(
    vector_chinese,
    vector_other
)


# 输出结果
print("中文和英文问题的相似度：",
      similarity_chinese_english[0][0])

print("中文问题和无关问题的相似度：",
      similarity_chinese_other[0][0])