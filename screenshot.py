"""
终端截图 - 使用 Pillow 直接渲染，支持中文
"""
import os
import uuid
from PIL import Image, ImageDraw, ImageFont


# 颜色配置
COLORS = {
    "bg": (30, 30, 30),
    "header_bg": (51, 51, 51),
    "dot_red": (255, 95, 86),
    "dot_yellow": (255, 189, 46),
    "dot_green": (39, 201, 63),
    "prompt": (39, 201, 63),
    "command": (240, 240, 240),
    "output": (204, 204, 204),
    "title_text": (153, 153, 153),
}

FONT_SIZE = 15
LINE_HEIGHT = 24
HEADER_HEIGHT = 40
PADDING = 18


def _get_font(size: int = FONT_SIZE):
    """获取支持中文的等宽字体"""
    # 优先使用 Noto Sans CJK（支持中文）
    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Light.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _text_width(font, text: str) -> int:
    """计算文本宽度"""
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0] if bbox else len(text) * 9


def render_screenshot(
    command: str,
    output: str,
    user: str = "root",
    host: str = "server",
    output_dir: str = "output",
) -> str:
    """
    渲染终端截图（Pillow 直接绘制，支持中文）
    """
    os.makedirs(output_dir, exist_ok=True)

    font = _get_font()

    # 构建显示行
    prompt_text = f"{user}@{host}:~$"
    full_prompt_cmd = f"{prompt_text} {command}"  # prompt + command 合在一起算宽度

    display_lines = []
    # 第一行：prompt + command（在同一行）
    display_lines.append(("prompt_cmd", prompt_text, command))
    # 后续：output 按行拆分
    if output:
        for ol in output.split("\n"):
            display_lines.append(("output", ol, ""))

    # 计算最大文本宽度
    max_width = 0
    for line_type, part1, part2 in display_lines:
        if line_type == "prompt_cmd":
            w = _text_width(font, f"{part1} {part2}")
        else:
            w = _text_width(font, part1)
        max_width = max(max_width, w)

    img_width = max(650, max_width + PADDING * 2 + 20)
    content_height = HEADER_HEIGHT + len(display_lines) * LINE_HEIGHT + PADDING * 2
    img_height = max(120, content_height)

    # 创建图像
    img = Image.new("RGB", (img_width, img_height), COLORS["bg"])
    draw = ImageDraw.Draw(img)

    # 标题栏
    draw.rectangle(
        [(0, 0), (img_width, HEADER_HEIGHT)],
        fill=COLORS["header_bg"],
    )

    # 三色圆点
    dot_y = HEADER_HEIGHT // 2
    dot_r = 6
    for i, color in enumerate([COLORS["dot_red"], COLORS["dot_yellow"], COLORS["dot_green"]]):
        cx = 22 + i * 24
        draw.ellipse([cx - dot_r, dot_y - dot_r, cx + dot_r, dot_r + dot_y], fill=color)

    # 标题栏文字
    draw.text((22 + 3 * 24 + 12, dot_y - 8), f"{user}@{host}", fill=COLORS["title_text"], font=font)

    # 绘制内容
    y = HEADER_HEIGHT + PADDING

    for line_type, part1, part2 in display_lines:
        if line_type == "prompt_cmd":
            # 先画 prompt（绿色）
            draw.text((PADDING, y), part1, fill=COLORS["prompt"], font=font)
            # 再画 command（白色），紧跟在 prompt 后面，加一个空格间距
            prompt_w = _text_width(font, part1)
            draw.text((PADDING + prompt_w + 8, y), part2, fill=COLORS["command"], font=font)
        else:
            # output 行
            draw.text((PADDING, y), part1, fill=COLORS["output"], font=font)

        y += LINE_HEIGHT

    # 保存
    filename = f"terminal_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(output_dir, filename)
    img.save(filepath, "PNG")
    return filepath


if __name__ == "__main__":
    path = render_screenshot(
        command="python3 --version",
        output="Python 3.8.10",
        user="root",
        host="服务器",
        output_dir="/tmp/test_cn",
    )
    import os
    print(f"截图: {path} ({os.path.getsize(path)} bytes)")
