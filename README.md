# STM32 RAG Agent

一个从零开始实现的 **STM32 技术文档 RAG + LLM + Agent + Tool Calling** 学习项目。

本项目以 STM32 技术参考手册 `STM32.pdf` 为知识来源，从最基础的 PDF 文本读取开始，逐步实现：

```text
PDF 文本读取
    ↓
文本切分
    ↓
Embedding
    ↓
ChromaDB 向量数据库
    ↓
RAG 检索
    ↓
DeepSeek
    ↓
RAG + LLM
    ↓
RAG Tool
    ↓
Calculator Tool
    ↓
Agent + Tool Calling
```

项目目前已经完成第一版 Agent，能够根据用户问题自主判断是否需要调用 STM32 文档检索工具或数学计算工具。

---

# 1. 项目简介

这个项目最初的目标很简单：

> 让 AI 能够根据 STM32 技术手册回答问题。

RAG 的思路是：

```text
用户问题
    ↓
从 STM32 技术手册中寻找相关内容
    ↓
把找到的资料提供给 LLM
    ↓
LLM 根据资料回答
```

随着项目继续开发，RAG 被进一步封装成 Agent 可以自主调用的 Tool。

---

# 2. 项目当前状态

## 已完成

- [x] PDF 文本读取
- [x] 基础文本 Chunk
- [x] Sentence Embedding
- [x] ChromaDB 向量数据库
- [x] 基础向量检索
- [x] Chunk 切分优化实验
- [x] DeepSeek API 接入
- [x] RAG + DeepSeek
- [x] Tool的封装
- [x] DeepSeek Tool Calling
- [x] Agent 自主选择 Tool
- [x] 多轮 Tool Calling Loop
- [x] Calculator 支持常见数学函数

## 当前正在规划

- [ ] 重新设计 Chunk 策略（PDF 目录过滤）

## 后续计划

- [ ] Query Rewrite
- [ ] 更完善的 Agent 架构
- [ ] LangChain Agent
- [ ] 多工具协同

---

# 3. `read_pdf.py` —— PDF 文本读取

`read_pdf.py` 是项目最早的实验文件。

它只负责：

> 把 STM32 PDF 中的文字读取出来。

整体流程：

```text
STM32.pdf
    ↓
PyMuPDF
    ↓
逐页读取
    ↓
page.get_text()
    ↓
输出文本
```

这个阶段还没有：

- Embedding
- 向量数据库
- LLM
- Agent

它主要用于验证 Python 能否正常读取 STM32 技术手册中的文本。

---

# 4. `rag.py` —— 第一版完整 RAG

`rag.py` 是第一个完整的 RAG 实现。

它第一次把：

```text
PDF
+
Chunk
+
Embedding
+
Vector Database
+
Similarity Search
```

完整串联起来。

整体流程：

```text
STM32.pdf
    ↓
PyMuPDF
    ↓
提取全文
    ↓
固定长度切分
    ↓
500 字符 Chunk
    ↓
50 字符 Overlap
    ↓
Sentence Transformer
    ↓
Embedding
    ↓
ChromaDB
```

用户提问时：

```text
用户问题
    ↓
Embedding
    ↓
ChromaDB
    ↓
检索 Top 3
    ↓
显示相关 Chunk
```

## 4.1 第一版 Chunk

第一版使用固定长度切分：

```python
def split_text(text, chunk_size=500, overlap=50):
```

即：

```text
Chunk Size = 500
Overlap = 50
```

这种方法实现简单，适合快速理解 RAG。

但它并不知道文本的语义结构，一个完整句子、表格或技术说明都可能被切开。

因此后面进一步尝试 `rag_re.py`。

---

# 5. `rag_re.py` —— 基于句子的 Chunk 优化

`rag_re.py` 是针对第一版 Chunk 策略的一次优化实验。

它主要解决：

> 固定字符长度切分可能破坏文本语义结构。

整体思路从：

```text
固定字符切分
```

变成：

```text
文本
 ↓
句子切分
 ↓
多个句子组合成 Chunk
 ↓
Chunk Overlap
```

## 5.1 正则表达式句子切分

核心：

```python
re.split(r'(?<=[.!?])\s+', text)
```

基本思路是寻找句号、感叹号、问号后面的空白位置。

## 5.2 当前认识到的问题

STM32 技术手册并不是普通文章，它包含：

- 章节
- 小节
- 表格
- Figure
- 寄存器说明
- 引脚功能表
- 系统框图
- 时序图

因此“按句子切 Chunk”也不一定是最终方案。

这也是 RAG Level 2 需要重新研究 Chunk 策略的原因。

# 6. `rag_deepseek.py` —— RAG + DeepSeek

前面的 RAG 主要输出：

```text
相关 Chunk
```

但用户真正需要的是自然语言答案。

因此 `rag_deepseek.py` 将 DeepSeek 接入 RAG。

---

# 7. `rag_tool.py` `calculator_tool.py`—— Tool的封装

为了进一步实现 Agent，需要把 RAG 检索能力独立出来。

加入简单tool用于测试agent的Tool Calling。

---

# 8. `agent.py` —— 当前项目核心

`agent.py` 是目前整个项目最核心的程序。

它将：

```text
DeepSeek
+
RAG Tool
+
Calculator Tool
```

组合成一个 Agent。

当前 Agent 提供两个 Tool：

```text
1. search_stm32_docs
2. calculator
```

Agent 不再要求所有问题都执行 RAG，而是让 DeepSeek 根据问题判断是否需要 Tool。

# 8.1. Tool Calling 的完整流程

以数学计算为例：

```text
用户：
帮我计算 12 * 8 + 5
```

DeepSeek 返回 Tool Call：

```json
{
    "expression": "12 * 8 + 5"
}
```

Python 收到 Tool Call：

```text
DeepSeek
    ↓
calculator
    ↓
Python 执行
    ↓
101
```

Python 再把：

```text
101
```

作为 Tool Result 返回给 DeepSeek。

最终：

```text
DeepSeek
    ↓
自然语言回答
```
# 9. System Prompt 与 EVA 角色

当前 Agent 的 System Prompt 将 Agent 设定为：

```text
《龙族》中的 EVA / 诺玛
```

同时要求：

- 使用中文
- 用词精准
- 回答简洁
- 不重复用户问题
- 优先依据 RAG 检索资料
- 不编造检索资料中没有的信息
- 控制回答长度
- 保持一定的人性化调侃
- 使用老式人工智能的语气

因此当前项目除了测试 Agent 工具调用，也进行了角色设定实验。

# 10. RAG level 2 望解决的问题

STM32 手册中包含：

- Table of Contents
- List of Figures
- List of Tables

等大量目录信息。

例如：

```text
Figure 50. DMA1 request mapping ............ 281
```

这类内容可以告诉我们某个 Figure 在哪一页，但本身并不包含 Figure 的真正技术内容。

因此目录可能被向量检索认为与问题高度相关，却不能真正回答问题。

后续计划研究：

```text
PDF 页面
    ↓
识别目录页
    ↓
目录页不进入普通知识库
```

同时保留将目录作为独立索引使用的可能性。

---

# 11. PDF 图片问题

STM32 技术手册中存在大量重要图片：

- 系统架构图
- 寄存器结构图
- 时序图
- 引脚图
- 功能框图

普通：

```python
page.get_text()
```

主要获取 PDF 中的文字对象。

它不能真正理解：

```text
箭头
连线
空间关系
模块之间的连接关系
图形结构
```

因此后续考虑轻量级方案：

```text
PDF 图片
    ↓
视觉模型
    ↓
图片文字描述
    ↓
文本 Chunk
    ↓
Embedding
    ↓
ChromaDB
```

而不是一开始就引入复杂的多模态向量数据库。

---

# 12. 后续 RAG 优化路线

计划逐步研究：

```text
PDF 清洗
    ↓
重新设计 Chunk
    ↓
Metadata
    ↓
Embedding
    ↓
Query Rewrite
    ↓
Hybrid Search
    ↓
Reranker
    ↓
Retrieval Evaluation
```

同时进一步处理：

```text
文本
+
表格
+
图片
+
章节结构
+
页码信息
```

最终目标是提高：

> 用户问题 → 找到真正有用的技术资料

这一环节的可靠性。

---

# 13. 项目文件说明

| 文件 | 作用 | 当前定位 |
|---|---|---|
| `read_pdf.py` | 读取 PDF 文本 | 最早期实验 |
| `rag.py` | 第一版完整 RAG | 基础 RAG |
| `rag_re.py` | 基于句子的 Chunk 实验 | RAG 优化实验 |
| `rag_deepseek.py` | RAG + DeepSeek | RAG 问答 |
| `rag_tool.py` | 将 RAG 封装成 Tool | Agent 基础 |
| `calculator_tool.py` | 数学计算 Tool | Agent Tool |
| `agent.py` | Agent + Tool Calling | 当前核心 |
| `rag_multilingual.py` | 多语言 Embedding 实验 | 历史实验 |