# 实验步骤文档生成器

一个基于 Flask 和 DeepSeek API 的实验步骤文档生成工具，能够将实验步骤转换为带有终端模拟输出和截图的 Word 文档。

## 功能特点

- **DeepSeek 模式**：上传实验步骤文件（txt/md），AI 自动生成终端命令输出
- **MD 上传模式**：直接上传包含命令和输出的 Markdown 文件
- **API 密钥管理**：支持在网页中输入和管理 DeepSeek API 密钥，本地存储，一次配置多次使用
- **终端模拟**：生成逼真的终端输出和截图
- **Word 文档生成**：自动将实验步骤、终端输出和截图组装成完整的 Word 文档
- **用户友好界面**：直观的网页界面，支持实时预览

## 技术栈

- **后端**：Flask、Python
- **前端**：HTML、CSS、JavaScript
- **AI**：DeepSeek API
- **文档处理**：python-docx
- **截图生成**：html2image、Pillow

## 安装步骤

### 1. 克隆项目

```bash
git clone <项目地址>
cd lab-doc-generator
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动应用

```bash
# 默认端口 5000
python app.py

# 或指定端口
FLASK_PORT=5001 python app.py
```

## 使用方法

### 方法一：DeepSeek 模式（推荐）

1. 在网页中切换到 "DeepSeek 模式"
2. 输入你的 DeepSeek API 密钥（会自动保存到本地存储）
3. 上传实验步骤文件（支持 .txt 和 .md 格式）
4. 填写用户名和主机名（用于终端预览）
5. 点击 "生成文档" 按钮
6. 等待生成完成后下载 Word 文档

### 方法二：MD 上传模式

1. 在网页中切换到 "MD 上传模式"
2. 复制提示词模板，使用 ChatGPT/Claude 等生成符合格式的 Markdown 文件
3. 上传生成的 Markdown 文件
4. 填写用户名和主机名
5. 点击 "生成文档" 按钮
6. 等待生成完成后下载 Word 文档

## 实验步骤文件格式

### DeepSeek 模式文件格式

```md
# 实验标题

## 步骤1：步骤标题
命令1
命令2

## 步骤2：步骤标题
命令1
命令2
```

### MD 上传模式文件格式（固定格式）

```md
# 实验标题

## 步骤1：步骤标题
**说明：** 步骤的文字描述
```bash
实际命令
```
**输出：**
```
命令执行后的真实输出内容
```

## 步骤2：步骤标题
**说明：** 步骤的文字描述
```bash
实际命令
```
**输出：**
```
命令执行后的真实输出内容
```
```

## API 密钥管理

1. **添加 API 密钥**：在 DeepSeek 模式下的 API 密钥输入框中输入你的 DeepSeek API 密钥
2. **查看 API 密钥**：已配置的 API 密钥会以掩码形式显示（只显示首尾各4个字符）
3. **释放 API 密钥**：点击 "释放API" 按钮可以清除已存储的 API 密钥
4. **自动保存**：API 密钥会自动保存到浏览器的本地存储中，下次访问时无需重新输入

## 注意事项

- DeepSeek API 密钥需要从 DeepSeek 官网获取
- 生成文档时，AI 模拟终端输出可能需要 1-2 分钟时间
- 上传的文件大小限制为 5MB
- 最多支持 50 个实验步骤

## 目录结构

```
lab-doc-generator/
├── static/            # 静态文件
│   └── terminal.css   # 样式文件
├── templates/         # 模板文件
│   └── index.html     # 主页面
├── output/            # 生成的文档和截图
├── app.py             # Flask 主应用
├── deepseek_client.py # DeepSeek API 客户端
├── docx_builder.py    # Word 文档生成
├── md_parser.py       # Markdown 解析器
├── screenshot.py      # 截图生成
├── step_parser.py     # 步骤解析器
├── requirements.txt   # 依赖项
└── README.md          # 项目说明
```

## 故障排除

- **API 调用失败**：检查 API 密钥是否正确，网络连接是否正常
- **截图生成失败**：检查 html2image 是否正常工作，可能需要安装浏览器
- **文档生成失败**：检查输入文件格式是否正确，步骤数量是否超过限制

## 许可证

MIT License
