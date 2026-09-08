import re


def split_sentences(text):
    """
    把文本按照句号、问号、感叹号进行分句。
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
    max_chars=150,
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


text = (
    "The STM32 microcontroller contains a 12-bit ADC. "
    "The ADC can convert analog signals into digital values. "
    "It supports multiple input channels. "
    "The conversion result is stored in a data register. "
    "The ADC can operate in different conversion modes. "
    "These modes can be configured by software."
)


chunks = chunk_by_sentence(
    text,
    max_chars=150,
    overlap_sentences=1
)


print("=" * 60)
print("Chunk 切分结果")
print("=" * 60)

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i + 1} ---")
    print(f"字符数：{len(chunk)}")
    print(chunk)