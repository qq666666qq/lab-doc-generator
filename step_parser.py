"""
解析 txt/md 中的实验步骤和命令
"""
import re


def parse_steps(content: str) -> list[dict]:
    """
    解析文本内容，提取步骤和命令。

    支持格式：
    - "1. 标题" / "步骤一：标题" / "Step 1: 标题"
    - 命令在标题下方（可隔空行）
    - 代码块 ``` 中的命令
    - 缩进内容视为命令

    返回格式：
    [{"step": 1, "title": "xxx", "command": "xxx"}, ...]
    """
    # 预处理：去除 BOM、nbsp、统一换行
    content = content.replace("\ufeff", "")
    content = content.replace("\u00a0", " ")
    content = content.replace("\r\n", "\n")

    lines = content.split("\n")

    # 第一轮：识别所有步骤标题
    steps = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        step_info = _match_step_title(stripped)
        if step_info:
            steps.append({
                "line_idx": i,
                "step": step_info["num"],
                "title": step_info["title"],
                "command": "",
            })

    # 第二轮：为每个步骤查找命令
    for idx, s in enumerate(steps):
        if s["command"]:
            continue

        # 确定搜索范围：从当前步骤标题行到下一个步骤标题行（或文件末尾）
        start = s["line_idx"] + 1
        end = steps[idx + 1]["line_idx"] if idx + 1 < len(steps) else len(lines)

        command = _find_command(lines, start, end)
        s["command"] = command

    # 重新编号：按出现顺序连续编号 1, 2, 3, ...
    # 解决原文中分节导致编号重复（如两个"1."）的问题
    for i, s in enumerate(steps):
        s["step"] = i + 1

    return steps


def _match_step_title(text: str) -> dict | None:
    """
    判断一行是否是步骤标题。
    返回 {"num": int, "title": str} 或 None。

    排除纯中文大标题："一、Ubuntu/Debian系列" 这种
    """
    # 模式1: "1. 标题" "1、标题" "1: 标题"
    m = re.match(r"^(\d+)\s*[.、:：]\s*(.+)$", text)
    if m:
        num = int(m.group(1))
        title = m.group(2).strip()
        # 标题不能太短或为空
        if title and len(title) >= 2:
            return {"num": num, "title": title}

    # 模式2: "步骤一：标题" "步骤 1：标题"
    m = re.match(r"^步骤\s*(?:(\d+)|([一二三四五六七八九十]+))\s*[.、:：]?\s*(.*)$", text)
    if m:
        if m.group(1):
            num = int(m.group(1))
        else:
            num = _cn_to_int(m.group(2))
        title = m.group(3).strip()
        if title and len(title) >= 2:
            return {"num": num, "title": title}

    # 模式3: "Step 1: 标题"
    m = re.match(r"^[Ss]tep\s*(\d+)\s*[:：]\s*(.+)$", text)
    if m:
        return {"num": int(m.group(1)), "title": m.group(2).strip()}

    return None


def _find_command(lines: list[str], start: int, end: int) -> str:
    """
    在指定范围内查找命令。
    跳过空行和纯空格行，取第一个非空内容作为命令。
    如果有代码块，优先取代码块内容。
    """
    in_code_block = False
    code_lines = []

    for i in range(start, min(end, len(lines))):
        line = lines[i]
        stripped = line.strip()

        # 代码块标记
        if stripped.startswith("```"):
            if in_code_block:
                # 结束代码块
                if code_lines:
                    return "\n".join(code_lines).strip()
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # 跳过空行
        if not stripped:
            continue

        # 跳过看起来像标题的行（步骤编号、章节标题）
        if _match_step_title(stripped):
            continue

        # 跳过纯中文大标题："一、xxx" "二、xxx"
        if re.match(r"^[一二三四五六七八九十]+、", stripped):
            continue

        # 跳过 markdown 标题
        if stripped.startswith("#"):
            continue

        # 跳过注释行
        if stripped.startswith("//") or stripped.startswith("--"):
            continue

        # 找到了非空内容，作为命令
        if _looks_like_command(stripped):
            return stripped

        # 即使不像命令也返回（用户可能写的是非标准命令）
        return stripped

    # 代码块残留
    if code_lines:
        return "\n".join(code_lines).strip()

    return ""


def _looks_like_command(text: str) -> bool:
    """判断一行文本是否看起来像命令"""
    cmd_prefixes = [
        "apt", "yum", "dnf", "pip", "npm", "docker", "systemctl",
        "cd ", "ls", "mkdir", "rm ", "cp ", "mv ", "chmod", "chown",
        "cat ", "echo", "wget", "curl", "git", "ssh", "scp",
        "sudo", "su ", "exit", "export", "source", "python",
        "java", "node", "make", "cmake", "gcc", "g++",
        "tar ", "zip", "unzip", "service", "firewall",
        "which", "whereis", "find", "grep", "sed", "awk",
        "mount", "df ", "du ", "free", "top", "ps ", "kill",
        "netstat", "ip ", "ifconfig", "ping", "traceroute",
        "openssl", "ssh-keygen", "useradd", "passwd",
        "systemctl", "journalctl", "crontab",
    ]
    text_lower = text.lower()
    return any(text_lower.startswith(p) for p in cmd_prefixes)


def _cn_to_int(cn: str) -> int:
    """中文数字转整数"""
    mapping = {
        "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
        "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    }
    if len(cn) == 1:
        return mapping.get(cn, 1)
    if cn[0] == "十" and len(cn) == 2:
        return 10 + mapping.get(cn[1], 0)
    if len(cn) == 2 and cn[1] == "十":
        return mapping.get(cn[0], 1) * 10
    return mapping.get(cn, 1)


if __name__ == "__main__":
    test = """Linux安装Python实验步骤

一、Ubuntu/Debian系列

1. 更新软件源

apt-get update

2. 安装Python3和pip3

apt-get install -y python3 python3-pip

3. 验证安装

python3 --version

4. 升级pip3

pip3 install --upgrade pip

5. 测试运行

python3 -c "print('hello')"

二、CentOS/RHEL系列

1. 安装Python3

yum install -y python3

2. 安装pip3

yum install -y python3-pip

3. 验证安装

python3 --version

4. 升级pip3

pip3 install --upgrade pip

5. 测试运行

python3 -c "print('hello')"
"""
    steps = parse_steps(test)
    for s in steps:
        print(f"步骤{s['step']}: {s['title']} → {s['command']}")
    print(f"\n共 {len(steps)} 个步骤")
