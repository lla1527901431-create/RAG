# STM32 RAG 技术文档智能问答系统

一个基于 **RAG（Retrieval-Augmented Generation，检索增强生成）** 的 STM32 技术文档智能问答项目。

本项目从零实现并验证 RAG 的核心流程，包括 PDF 文档解析、文本切分、Embedding、向量数据库、相似度检索以及 DeepSeek 大模型生成回答。

## 项目流程

```text
STM32 PDF 技术文档
        ↓
    PyMuPDF 解析
        ↓
    文本切分 / Chunking
        ↓
Sentence Transformers
        ↓
   Embedding 向量
        ↓
     ChromaDB
        ↓
   Top-K 相似度检索
        ↓
    检索相关资料
        ↓
     DeepSeek API
        ↓
      最终回答
```

## 项目文件说明

| 文件/目录 | 作用 |
| --- | --- |
| `read_pdf.py` | 使用 PyMuPDF 读取 STM32 PDF，并提取页面文本。 |
| `chunk_text.py` | 基础文本切分实验，用于学习长文本 Chunking。 |
| `chunk_test.py` | 句子级 Chunking 测试，观察句子重叠和 Chunk 长度。 |
| `embedding_test.py` | 测试 Sentence Transformers 文本向量化及向量维度。 |
| `similarity_test.py` | 测试文本向量之间的语义相似度。 |
| `chroma_test.py` | 学习 ChromaDB 的 Collection、向量存储和查询。 |
| `deepseek_test.py` | 单独测试 DeepSeek API 调用，便于排查大模型调用问题。 |
| `multilingual_test.py` | 测试多语言 Embedding 模型及跨语言语义表示效果。 |
| `rag.py` | RAG 基础实验，实现 RAG 核心流程的学习与验证。 |
| `rag_re.py` | 基于正则表达式句子切分 + Embedding + ChromaDB 的 RAG 检索实现。 |
| `rag_multilingual.py` | 使用多语言 Embedding 模型进行 RAG 检索的实验。 |
| `rag_deepseek.py` | 将 ChromaDB 检索与 DeepSeek API 结合，实现完整 RAG 智能问答，并支持连续提问。 |
| `requirements.txt` | 项目所需 Python 依赖。 |
| `README.md` | 项目说明、安装方法、运行方法和技术总结。 |
| `.gitignore` | Git 忽略规则，避免提交虚拟环境、API 密钥等文件。 |
| `.env` | 本地保存 DeepSeek API Key 等环境变量，不上传 GitHub。 |
| `.venv/` | Python 虚拟环境，本地运行使用，不上传 GitHub。 |
| `chroma_db/` | ChromaDB 本地持久化向量数据库，不上传 GitHub。 |
| `documents/` | 本地 STM32 技术文档目录，按项目需要准备，不上传 GitHub。 |

## 主要技术

### 1. PDF 文档解析

使用 PyMuPDF 将 STM32 PDF 技术手册转换为可处理的文本。

### 2. Chunking

项目先测试固定字符切分，后进一步实现句子级 Chunking。

固定字符切分可能在技术术语中间产生边界，例如：

```text
12-bit ADC
```

可能被错误切分成：

```text
2-bit ADC
```

因此使用正则表达式按照英文句子边界切分，并设置句子重叠，以减少上下文被截断的问题。

### 3. Embedding

使用：

```text
all-MiniLM-L6-v2
```

将文本转换为 **384 维向量**。

查询时必须使用与建库阶段相同的 Embedding 模型。即使不同模型输出相同维度，也不能认为它们处于相同的向量空间。

### 4. ChromaDB

使用 ChromaDB 保存：

- 文档 Chunk
- Embedding 向量
- Chunk ID

用户提问后，将问题转换为向量，并从数据库中检索 Top-K 相关文本。

由于 ChromaDB 单批次写入存在数量限制，项目采用分批写入建立向量库。

### 5. DeepSeek

将 ChromaDB 检索得到的相关资料作为 Context 放入 Prompt，再调用 DeepSeek API 生成最终回答。

完整流程：

```text
用户问题
   ↓
Query Embedding
   ↓
ChromaDB 检索
   ↓
Top-K 相关文档
   ↓
Context
   ↓
Prompt
   ↓
DeepSeek
   ↓
最终回答
```

## 环境要求

- Windows
- Python 3.12+
- Git
- VS Code

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/lla1527901431-create/RAG.git
cd RAG
```

### 2. 创建虚拟环境

```powershell
python -m venv .venv
```

激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. 安装依赖

```powershell
pip install -r requirements.txt
```

## 配置 DeepSeek API

在项目根目录创建 `.env`：

```text
DEEPSEEK_API_KEY=你的_API_Key
```

不要把真实 API Key 写入 Python 代码，也不要上传到 GitHub。

## 运行示例

```powershell
python read_pdf.py
python chunk_test.py
python embedding_test.py
python similarity_test.py
python chroma_test.py
python rag_re.py
python rag_deepseek.py
```

运行 `rag_deepseek.py` 后，可以连续输入问题，例如：

```text
STM32的ADC分辨率是多少？
```

输入：

```text
exit
```

退出程序。

## 开发过程中解决的问题

### Chunking 边界问题

固定字符切分可能从技术术语中间截断。项目通过句子级 Chunking 和 Sentence Overlap 改善这一问题。

### Embedding 模型不一致

曾测试发现建库和查询使用不同 Embedding 模型会导致检索结果异常。最终统一使用 `all-MiniLM-L6-v2`。

### ChromaDB Batch Size

STM32 文档切分后产生大量 Chunk，一次性写入可能超过 ChromaDB 的批量限制，因此改为分批写入。

## GitHub 安全

以下内容不上传 GitHub：

```text
.env
.venv/
chroma_db/
documents/
```

特别注意：`.env` 中可能包含 DeepSeek API Key，禁止提交真实密钥。

## 后续升级方向

本项目是后续 AI Agent 项目的基础：

```text
RAG
 ↓
RAG Tool
 ↓
Tool Calling
 ↓
Agent Loop
 ↓
多工具协作
 ↓
Memory
 ↓
STM32 AI Agent
```

后续计划学习 LangChain、LangGraph，并加入代码分析、计算器、Web Search 等工具。
