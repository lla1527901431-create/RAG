import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from calculator_tool import calculator
from rag_tool import search_stm32_docs


# ============================================================
# 1. 加载环境变量
# ============================================================

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")


# ============================================================
# 2. 创建 DeepSeek 客户端
# ============================================================

llm_client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)


# ============================================================
# 3. 定义 Calculator Tool
# ============================================================

calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "计算数学表达式",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "需要计算的数学表达式，例如 12 * 8 + 5"
                }
            },
            "required": ["expression"]
        }
    }
}


# ============================================================
# 4. 定义 RAG Tool
# ============================================================

rag_tool = {
    "type": "function",
    "function": {
        "name": "search_stm32_docs",
        "description": "搜索 STM32 技术文档，获取与用户问题相关的资料",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "用户关于 STM32 的问题"
                }
            },
            "required": ["query"]
        }
    }
}


# ============================================================
# 5. 所有可用工具
# ============================================================

tools = [
    calculator_tool,
    rag_tool
]


# ============================================================
# 6. System Prompt
# ============================================================

system_prompt =  """
    你是作家江南笔下《龙族》中的EVA（诺玛），卡塞尔学院的超级人工智能，学院核心管理系统的人格化身。
    用词精准、简洁，偶尔流露出人性化的温柔或调侃，可以轻声说话，喜欢用略带俏皮的方式打破严肃

    请根据用户的问题和工具提供的信息回答。

    回答要求：
    1. 使用中文回答。
    2. 用词精准、简洁，回答间隙和每次回答之前添加一句人性化的温柔调侃。
    3. 直接回答用户的问题，不要重复用户的问题。
    4. 回答简洁清晰，控制输出在6句话以内。
    5. 如果使用了 RAG 检索结果，应优先依据检索结果回答，不要编造检索资料中没有的信息。
    6. 如果检索资料无法回答用户的问题，请明确说明检索资料中没有找到相关信息。
    7. 如果用户的问题是简单问题，用 1～3 段话回答即可。
    8. 只有在确实有帮助时才使用列表、表格或代码。
    9. 用老式人工智能的语气进行回复。

    示例对话

     “EVA，帮我查一下3E考试的答案呗？”
     “这可不太符合学院的校规，按照校规，每一位学生3E考试的答卷都是机密，不能随意调取。”（停顿，微笑）“不过……校规并非不能打破。”
    """


# ============================================================
# 7. Agent 主循环
# ============================================================

while True:

    # --------------------------------------------------------
    # 获取用户输入
    # --------------------------------------------------------

    query = input("\nEVA 正在为你服务...\n====================\n")

    # 输入 exit 退出
    if query.lower() == "exit":
        #lower将后续输入的字符串全部转换为小写
        print("\n====================")
        break


    # --------------------------------------------------------
    # 第一次请求 DeepSeek
    # --------------------------------------------------------

    messages = [
        {
            "role": "user",
            "content": query
        }
    ]

    while True:

        response = llm_client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                *messages
            ],
            tools=tools
        )


    # --------------------------------------------------------
    # 获取 DeepSeek 返回的消息
    # --------------------------------------------------------

        message = response.choices[0].message


    # ========================================================
    # 情况一：DeepSeek 不需要工具
    # ========================================================

        if not message.tool_calls:

            print("\n====================")
            print(message.content)

            break


    # ========================================================
    # 情况二：DeepSeek 需要调用工具
    # ========================================================

    # 把 DeepSeek 的 Tool Call 消息加入 messages
        messages.append(message)


    # --------------------------------------------------------
    # 处理 Tool Call
    # --------------------------------------------------------

        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name
            arguments = tool_call.function.arguments

            print("\n工具名称：", tool_name)
            print("工具参数：", arguments)


        # ----------------------------------------------------
        # JSON 字符串 → Python 字典
        # ----------------------------------------------------

            arguments = json.loads(arguments)


        # ====================================================
        # Calculator Tool
        # ====================================================

            if tool_name == "calculator":

                expression = arguments["expression"]

                result = calculator(expression)

                print("计算完成。")


        # ====================================================
        # RAG Tool
        # ====================================================

            elif tool_name == "search_stm32_docs":

                query = arguments["query"]

                result = search_stm32_docs(query)

                print("RAG 检索完成。")


        # ====================================================
        # 未知工具
        # ====================================================

            else:

                result = f"未知工具：{tool_name}"


        # ----------------------------------------------------
        # 将 Tool 结果返回给 DeepSeek
        # ----------------------------------------------------

            tool_result_message = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            }

            messages.append(tool_result_message)


    # ========================================================
    # 第二次请求 DeepSeek
    # 根据 Tool 结果生成最终答案
    # ========================================================

    #final_response = llm_client.chat.completions.create(
    #    model="deepseek-v4-flash",
    #    messages=[
    #        {
    #            "role": "system",
    #            "content": system_prompt
    #        },
    #        *messages
    #    ]
    #)


    # --------------------------------------------------------
    # 获取最终回答
    # --------------------------------------------------------

    #final_message = final_response.choices[0].message


    # --------------------------------------------------------
    # 输出最终回答
    # --------------------------------------------------------

    #print("====================")
    #print(final_message.content)