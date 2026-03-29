"""
实验步骤文档生成器 - Flask 主应用
"""
import os
import re
import uuid
import logging
from flask import Flask, request, render_template, send_file, jsonify

# 读取 .env 文件设置环境变量
def load_env():
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        if key and not os.environ.get(key):
                            os.environ[key] = value

load_env()

from werkzeug.utils import secure_filename
from step_parser import parse_steps
from md_parser import parse_md_steps
from deepseek_client import simulate_output
from screenshot import render_screenshot
from docx_builder import build_docx

app = Flask(__name__)

# 会话安全配置
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB
app.secret_key = os.environ.get("FLASK_SECRET_KEY", uuid.uuid4().hex + uuid.uuid4().hex)

# 安全配置
MAX_STEPS = 50
MAX_STEP_CONTENT = 10000  # 字符
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 单文件最大 5MB
ALLOWED_EXTENSIONS = {".txt", ".md"}
SAFE_NAME_PATTERN = re.compile(r'^[\w\-.]+$')

# 日志配置（不输出到客户端）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _validate_user_host(form):
    """验证并返回 user/host 参数"""
    user = form.get("user", "root").strip()[:32] or "root"
    host = form.get("host", "server").strip()[:64] or "server"
    if not SAFE_NAME_PATTERN.match(user) or not SAFE_NAME_PATTERN.match(host):
        return None, None, "用户名/主机名仅支持字母、数字、下划线、连字符"
    return user, host, None


def _validate_file_extension(filename: str) -> bool:
    """校验文件扩展名白名单"""
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS


def _validate_upload_size(file_data: bytes) -> bool:
    """校验上传文件大小"""
    return len(file_data) <= MAX_UPLOAD_SIZE


def _safe_error(msg: str = "服务器内部错误"):
    """返回安全的错误响应，不泄露内部信息"""
    return jsonify({"error": msg}), 500


@app.after_request
def set_security_headers(response):
    """设置安全响应头"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'"
    # 移除服务器指纹
    response.headers.pop("Server", None)
    return response


@app.route("/")
def index():
    """上传页面"""
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """接收文件+参数，生成文档"""
    try:
        # 获取并验证参数
        user, host, err = _validate_user_host(request.form)
        if err:
            return jsonify({"error": err}), 400

        # 获取上传的文件
        if "file" not in request.files:
            return jsonify({"error": "请上传文件"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "未选择文件"}), 400

        # 校验文件扩展名白名单
        safe_name = secure_filename(file.filename)
        if not _validate_file_extension(safe_name):
            return jsonify({"error": "只接受 .txt 和 .md 格式文件"}), 400

        # 读取文件内容并校验大小
        file_data = file.read()
        if not _validate_upload_size(file_data):
            return jsonify({"error": f"文件大小超过限制（最大{MAX_UPLOAD_SIZE // (1024*1024)}MB）"}), 400

        content = file_data.decode("utf-8", errors="replace")

        # 解析步骤
        steps = parse_steps(content)
        if not steps:
            return jsonify({"error": "未解析到有效步骤，请检查文件格式"}), 400

        if len(steps) > MAX_STEPS:
            return jsonify({"error": f"步骤数量超过限制（最多{MAX_STEPS}个）"}), 400

        # 创建本次任务目录
        task_id = uuid.uuid4().hex[:16]
        task_dir = os.path.join(OUTPUT_DIR, task_id)
        os.makedirs(task_dir, exist_ok=True)

        # 处理 API 密钥
        api_key = request.form.get('api_key')
        if api_key:
            # 设置 API 密钥到环境变量
            os.environ['DEEPSEEK_API_KEY'] = api_key

        # 逐条调用 DeepSeek + 截图
        screenshots = []
        results = []

        for i, step in enumerate(steps):
            command = step["command"]

            # 调用 DeepSeek 生成模拟输出
            try:
                output = simulate_output(command)
            except Exception as e:
                logger.warning("DeepSeek 调用失败: %s", type(e).__name__)
                output = "[模拟输出生成失败]"

            # 截图
            try:
                screenshot_path = render_screenshot(
                    command=command,
                    output=output,
                    user=user,
                    host=host,
                    output_dir=task_dir,
                )
                screenshots.append(screenshot_path)
            except Exception as e:
                logger.warning("截图生成失败: %s", type(e).__name__)
                screenshots.append("")
                output += "\n[截图生成失败]"

            results.append({
                "step": step["step"],
                "title": step["title"],
                "command": command,
                "output": output,
            })

        # 组装 Word 文档
        docx_filename = f"lab_report_{task_id}.docx"
        docx_path = os.path.join(OUTPUT_DIR, docx_filename)

        build_docx(
            steps=results,
            screenshots=screenshots,
            user=user,
            host=host,
            output_path=docx_path,
        )

        return jsonify({
            "success": True,
            "filename": docx_filename,
            "steps_count": len(steps),
            "download_url": f"/download/{docx_filename}",
        })

    except Exception as e:
        logger.exception("generate endpoint error")
        return _safe_error()


@app.route("/generate_md", methods=["POST"])
def generate_md():
    """接收 MD 文件，直接使用 MD 中的命令和输出生成文档（不调用 DeepSeek）"""
    try:
        # 获取并验证参数
        user, host, err = _validate_user_host(request.form)
        if err:
            return jsonify({"error": err}), 400

        # 获取上传的文件
        if "md_file" not in request.files:
            return jsonify({"error": "请上传 MD 文件"}), 400

        file = request.files["md_file"]
        if file.filename == "":
            return jsonify({"error": "未选择文件"}), 400

        # 校验文件扩展名
        safe_name = secure_filename(file.filename)
        if not safe_name.lower().endswith(".md"):
            return jsonify({"error": "只接受 .md 格式文件"}), 400

        # 读取文件内容并校验大小
        file_data = file.read()
        if not _validate_upload_size(file_data):
            return jsonify({"error": f"文件大小超过限制（最大{MAX_UPLOAD_SIZE // (1024*1024)}MB）"}), 400

        content = file_data.decode("utf-8", errors="replace")

        # 解析 MD 步骤
        steps = parse_md_steps(content)
        if not steps:
            return jsonify({"error": "未解析到有效步骤，请检查 MD 格式是否符合规范"}), 400

        if len(steps) > MAX_STEPS:
            return jsonify({"error": f"步骤数量超过限制（最多{MAX_STEPS}个）"}), 400

        # 验证步骤内容长度
        for step in steps:
            if len(step.get("command", "")) > MAX_STEP_CONTENT:
                return jsonify({"error": "单个步骤命令内容过长"}), 400
            if len(step.get("output", "")) > MAX_STEP_CONTENT:
                return jsonify({"error": "单个步骤输出内容过长"}), 400

        # 创建本次任务目录
        task_id = uuid.uuid4().hex[:16]
        task_dir = os.path.join(OUTPUT_DIR, task_id)
        os.makedirs(task_dir, exist_ok=True)

        # 逐条生成截图（使用 MD 中自带的输出，不调用 DeepSeek）
        screenshots = []
        results = []

        for i, step in enumerate(steps):
            command = step["command"]
            output = step.get("output", "")

            # 截图
            try:
                screenshot_path = render_screenshot(
                    command=command,
                    output=output,
                    user=user,
                    host=host,
                    output_dir=task_dir,
                )
                screenshots.append(screenshot_path)
            except Exception as e:
                logger.warning("截图生成失败: %s", type(e).__name__)
                screenshots.append("")
                output += "\n[截图生成失败]"

            results.append({
                "step": step["step"],
                "title": step["title"],
                "command": command,
                "output": output,
            })

        # 组装 Word 文档
        docx_filename = f"lab_report_{task_id}.docx"
        docx_path = os.path.join(OUTPUT_DIR, docx_filename)

        build_docx(
            steps=results,
            screenshots=screenshots,
            user=user,
            host=host,
            output_path=docx_path,
        )

        return jsonify({
            "success": True,
            "filename": docx_filename,
            "steps_count": len(steps),
            "download_url": f"/download/{docx_filename}",
        })

    except Exception as e:
        logger.exception("generate_md endpoint error")
        return _safe_error()


@app.route("/download/<filename>")
def download(filename):
    """下载生成的文件"""
    filename = secure_filename(filename)
    # 严格校验：仅允许 lab_report_开头的 docx 文件
    if not filename.startswith("lab_report_") or not filename.endswith('.docx'):
        logger.warning("非法下载请求: %s", filename)
        return jsonify({"error": "非法文件类型"}), 400
    # 校验文件名格式：lab_report_ + 16位hex + .docx
    if not re.match(r'^lab_report_[a-f0-9]{16}\.docx$', filename):
        logger.warning("非法文件名格式: %s", filename)
        return jsonify({"error": "非法文件名"}), 400
    filepath = os.path.realpath(os.path.join(OUTPUT_DIR, filename))
    real_output = os.path.realpath(OUTPUT_DIR)
    if not filepath.startswith(real_output + os.sep) and filepath != real_output:
        logger.warning("路径遍历尝试: %s", filename)
        return jsonify({"error": "非法路径"}), 400
    if not os.path.exists(filepath):
        return jsonify({"error": "文件不存在"}), 404
    return send_file(filepath, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.environ.get("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
