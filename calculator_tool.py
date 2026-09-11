import math


def calculator(expression: str) -> str:
    """
    计算数学表达式。

    Args:
        expression: 数学表达式，例如 "12 * 8 + 5"

    Returns:
        计算结果
    """

    # 允许使用的数学函数
    allowed_functions = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "abs": abs,
        "pi": math.pi
    }

    try:
        # 计算数学表达式
        result = eval(
            expression,
            {"__builtins__": {}},
            allowed_functions
        )

        # 把计算结果转换成字符串
        return str(result)

    except Exception as e:
        # 如果计算失败，返回错误信息
        return f"计算失败: {e}"