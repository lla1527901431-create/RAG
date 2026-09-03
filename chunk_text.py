def split_text(text, chunk_size=500, overlap=50):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start = end - overlap

    return chunks
import fitz


pdf = fitz.open("documents/STM32.pdf")

text = ""

for page in pdf:
    text += page.get_text()

pdf.close()


chunks = split_text(text)

print("原始文本长度：", len(text))
print("Chunk 数量：", len(chunks))

for i, chunk in enumerate(chunks[:5]):
    print("\n========== Chunk", i + 1, "==========")
    print(chunk)