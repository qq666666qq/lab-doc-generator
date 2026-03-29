"""
解析固定格式 MD 文件，提取步骤（含命令和输出）

固定格式：
# 实验标题

## 步骤1：步骤标题
**说明：** 步骤的文字描述
```bash
实际命令
```
**输出：**
```
命令执行后的输出内容
```
"""
import re


def parse_md_steps(content: str) -> list[dict]:
    """
    解析固定格式 MD 文件，提取步骤列表。

    每个步骤必须包含：
    - ## 步骤N：标题
    - **说明：** 描述文字
    - ```bash ... ``` 命令代码块
    - **输出：** ``` ... ``` 输出代码块

    返回格式：
    [{"step": 1, "title": "xxx", "command": "xxx", "output": "xxx", "description": "xxx"}, ...]
    """
    # 预处理
    content = content.replace("\ufeff", "")
    content = content.replace("\u00a0", " ")
    content = content.replace("\r\n", "\n")

    # 按 ## 步骤 拆分
    # 先提取实验标题（可选）
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)

    # 按步骤标题行拆分
    step_pattern = re.compile(
        r"^##\s*步骤\s*(\d+)\s*[：:]\s*(.+)$",
        re.MULTILINE,
    )

    step_matches = list(step_pattern.finditer(content))
    if not step_matches:
        return []

    steps = []
    for idx, match in enumerate(step_matches):
        step_num = int(match.group(1))
        step_title = match.group(2).strip()

        # 当前步骤内容范围
        start = match.end()
        end = step_matches[idx + 1].start() if idx + 1 < len(step_matches) else len(content)
        section = content[start:end]

        # 提取说明
        description = _extract_description(section)

        # 提取命令（第一个 bash 代码块）
        command = _extract_code_block(section, lang_hint="bash")

        # 提取输出
        output = _extract_output(section)

        steps.append({
            "step": step_num,
            "title": step_title,
            "command": command,
            "output": output,
            "description": description,
        })

    # 重新编号确保连续
    for i, s in enumerate(steps):
        s["step"] = i + 1

    return steps


def _extract_description(section: str) -> str:
    """提取 **说明：** 后面的文字"""
    m = re.search(r"\*\*说明：?\*\*\s*(.+?)(?:\n|$)", section)
    if m:
        return m.group(1).strip()
    return ""


def _extract_code_block(section: str, lang_hint: str = "bash") -> str:
    """提取指定语言的代码块内容"""
    # 先尝试找 bash/shell 代码块
    pattern = re.compile(rf"```{lang_hint}\s*\n(.*?)```", re.DOTALL)
    m = pattern.search(section)
    if m:
        return m.group(1).strip()

    # 如果没找到带语言标记的，找第一个代码块（跳过输出块）
    # 输出块在 **输出：** 之后，所以只在输出标记之前找
    output_pos = section.find("**输出")
    search_area = section[:output_pos] if output_pos != -1 else section

    pattern2 = re.compile(r"```\w*\s*\n(.*?)```", re.DOTALL)
    m2 = pattern2.search(search_area)
    if m2:
        return m2.group(1).strip()

    return ""


def _extract_output(section: str) -> str:
    """提取 **输出：** 后面的代码块内容"""
    m = re.search(r"\*\*输出：?\*\*\s*\n\s*```\s*\n(.*?)```", section, re.DOTALL)
    if m:
        return m.group(1).strip()

    # 也尝试 **输出：** 同行接代码块
    m2 = re.search(r"\*\*输出：?\*\*.*?```\s*\n(.*?)```", section, re.DOTALL)
    if m2:
        return m2.group(1).strip()

    return ""


def md_steps_to_deepseek_format(steps: list[dict]) -> list[dict]:
    """
    将 MD 步骤转为 DeepSeek 模式兼容的格式（供 docx_builder 使用）

    DeepSeek 格式: [{"step": N, "title": "xxx", "command": "xxx"}]
    """
    return [
        {
            "step": s["step"],
            "title": s["title"],
            "command": s["command"],
        }
        for s in steps
    ]


if __name__ == "__main__":
    test_md = """# 实验：Linux安装Python

## 步骤1：检查系统版本
**说明：** 查看当前Linux发行版信息
```bash
cat /etc/os-release
```
**输出：**
```
NAME="Ubuntu 22.04.3 LTS"
VERSION="22.04.3 LTS (Jammy Jellyfish)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 22.04.3 LTS"
```

## 步骤2：更新软件源
**说明：** 更新apt包管理器缓存
```bash
sudo apt update
```
**输出：**
```
Hit:1 http://archive.ubuntu.com/ubuntu jammy InRelease
Get:2 http://archive.ubuntu.com/ubuntu jammy-updates InRelease [119 kB]
Get:3 http://archive.ubuntu.com/ubuntu jammy-security InRelease [110 kB]
Fetched 229 kB in 1s (229 kB/s)
Reading package lists... Done
Building dependency tree... Done
```

## 步骤3：安装Python3
**说明：** 使用apt安装Python3
```bash
sudo apt install -y python3
```
**输出：**
```
Reading package lists... Done
Building dependency tree... Done
python3 is already the newest version (3.10.6-1~22.04)
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
```
"""
    steps = parse_md_steps(test_md)
    for s in steps:
        print(f"步骤{s['step']}: {s['title']}")
        print(f"  说明: {s['description']}")
        print(f"  命令: {s['command']}")
        print(f"  输出: {s['output'][:50]}...")
        print()
    print(f"共 {len(steps)} 个步骤")
