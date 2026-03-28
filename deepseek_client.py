"""
DeepSeek API 调用封装
"""
import os
from openai import OpenAI


def get_client() -> OpenAI:
    """获取 DeepSeek 客户端"""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        raise ValueError("请设置 DEEPSEEK_API_KEY 环境变量")
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )


def simulate_output(command: str) -> str:
    """
    调用 DeepSeek 生成命令的模拟终端输出

    Args:
        command: Linux 命令

    Returns:
        模拟的终端输出文本
    """
    client = get_client()

    system_prompt = (
        "你是一个 Linux 终端模拟器。请返回以下命令在 Linux 系统中的合理输出。"
        "只返回输出内容本身，不要包含命令本身、不要解释、不要用代码块包裹。"
        "输出应该像真实终端一样，包含合理的系统信息。"
        "如果命令会产生多行输出，请保持合理长度（10-30行）。"
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"命令：{command}"},
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    output = response.choices[0].message.content.strip()

    # 去掉可能被包裹的代码块标记
    if output.startswith("```"):
        lines = output.split("\n")
        if lines[-1].strip() == "```":
            output = "\n".join(lines[1:-1])
        else:
            output = "\n".join(lines[1:])

    return output


if __name__ == "__main__":
    print(simulate_output("docker --version"))
