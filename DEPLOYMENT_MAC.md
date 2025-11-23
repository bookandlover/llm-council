# macOS 部署指南 - LLM Council

本指南将帮助你在 macOS 系统上部署 LLM Council 项目。

## 项目简介

LLM Council 是一个多 LLM 协作问答系统，包含三个阶段：
1. **Stage 1**: 多个 LLM 独立回答问题
2. **Stage 2**: LLM 之间匿名互评和排名
3. **Stage 3**: 主席 LLM 综合所有答案给出最终结果

## 系统要求

- macOS 10.15 或更高版本
- Python 3.10 或更高版本
- Node.js 16.x 或更高版本
- npm 或 yarn
- 互联网连接（用于访问各 LLM 提供商的原生 API）
- OpenAI、Anthropic 和 Google AI 的 API 密钥

## 详细部署步骤

### 步骤 1: 安装系统依赖

#### 1.1 安装 Homebrew（如果尚未安装）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 1.2 安装 Python 3.10+

检查当前 Python 版本：
```bash
python3 --version
```

如果版本低于 3.10，使用 Homebrew 安装：
```bash
brew install python@3.11
```

#### 1.3 安装 Node.js 和 npm

检查是否已安装：
```bash
node --version
npm --version
```

如果未安装，使用 Homebrew：
```bash
brew install node
```

#### 1.4 安装 uv（Python 包管理工具）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安装后，重启终端或运行：
```bash
source $HOME/.cargo/env
```

验证安装：
```bash
uv --version
```

### 步骤 2: 克隆或下载项目

如果从 Git 仓库克隆：
```bash
cd ~/Projects  # 或你想存放项目的目录
git clone <repository-url>
cd llm-council
```

如果已经有项目文件，直接进入项目目录：
```bash
cd /path/to/llm-council
```

### 步骤 3: 配置环境

#### 3.1 创建 .env 文件

在项目根目录创建 `.env` 文件（可以复制 `.env.example`）：
```bash
cp .env.example .env
```

编辑 `.env` 文件，添加你的各个 API 密钥：
```bash
# OpenAI API Key
OPENAI_API_KEY=sk-...

# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-...

# Google AI API Key (for Gemini)
GOOGLE_API_KEY=AIza...
```

**获取 API 密钥：**

1. **OpenAI API 密钥**
   - 访问：https://platform.openai.com/api-keys
   - 登录或注册账号
   - 创建新的 API 密钥
   - 充值账户余额

2. **Anthropic API 密钥**
   - 访问：https://console.anthropic.com/settings/keys
   - 登录或注册账号
   - 生成 API 密钥
   - 充值账户余额

3. **Google AI API 密钥**
   - 访问：https://aistudio.google.com/app/apikey
   - 使用 Google 账号登录
   - 创建 API 密钥（Gemini API 目前有免费额度）

#### 3.2 配置模型（可选）

编辑 `backend/config.py` 来自定义你的 LLM 委员会：

```python
COUNCIL_MODELS = [
    "openai/gpt-4o",  # OpenAI GPT-4o
    "google/gemini-2.0-flash-exp",  # Google Gemini
    "anthropic/claude-3-5-sonnet-20241022",  # Anthropic Claude 3.5 Sonnet
]

CHAIRMAN_MODEL = "google/gemini-2.0-flash-exp"
```

**可用的模型标识符格式：**
- OpenAI: `openai/gpt-4o`, `openai/gpt-4o-mini`, `openai/gpt-4-turbo` 等
- Anthropic: `anthropic/claude-3-5-sonnet-20241022`, `anthropic/claude-3-5-haiku-20241022`, `anthropic/claude-3-opus-20240229` 等
- Google: `google/gemini-2.0-flash-exp`, `google/gemini-1.5-pro`, `google/gemini-1.5-flash` 等

**注意：**
- 已移除 Grok 模型（不再使用 OpenRouter）
- 确保你有对应提供商的 API 密钥和账户余额
- 模型名称必须与各提供商的官方 API 文档一致

### 步骤 4: 安装项目依赖

#### 4.1 安装后端依赖

在项目根目录：
```bash
uv sync
```

这会根据 `pyproject.toml` 安装所有 Python 依赖：
- FastAPI
- Uvicorn
- python-dotenv
- httpx
- pydantic

#### 4.2 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

这会安装：
- React 19
- Vite
- react-markdown
- 其他开发依赖

### 步骤 5: 运行项目

有两种方式启动项目：

#### 方式 1: 使用启动脚本（推荐）

给脚本添加执行权限（首次运行）：
```bash
chmod +x start.sh
```

运行脚本：
```bash
./start.sh
```

这会自动启动：
- 后端服务器在 `http://localhost:8001`
- 前端开发服务器在 `http://localhost:5173`

#### 方式 2: 手动启动（用于调试）

**终端 1 - 启动后端：**
```bash
uv run python -m backend.main
```

**终端 2 - 启动前端：**
```bash
cd frontend
npm run dev
```

### 步骤 6: 访问应用

在浏览器中打开：
```
http://localhost:5173
```

你应该能看到类似 ChatGPT 的界面。

### 步骤 7: 测试运行

1. 在输入框中输入一个问题，例如："什么是量子计算？"
2. 按 Enter 发送（Shift+Enter 换行）
3. 等待三个阶段的响应：
   - **Stage 1**: 查看各个 LLM 的独立回答
   - **Stage 2**: 查看 LLM 之间的互评和排名
   - **Stage 3**: 查看主席 LLM 的综合答案

## 常见问题排查

### 问题 1: `uv: command not found`

**解决方案：**
```bash
# 重新加载 shell 配置
source ~/.zshrc  # 如果使用 zsh
source ~/.bash_profile  # 如果使用 bash

# 或手动添加到 PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

### 问题 2: 后端端口 8001 被占用

**解决方案：**
编辑 `backend/main.py`，修改端口：
```python
uvicorn.run(app, host="0.0.0.0", port=8002)  # 改为其他端口
```

同时更新 `frontend/src/api.js` 中的 API 地址。

### 问题 3: Python 版本不兼容

**解决方案：**
```bash
# 使用 pyenv 管理多个 Python 版本
brew install pyenv
pyenv install 3.11
pyenv local 3.11
```

### 问题 4: API 调用错误

**可能原因：**
- API 密钥错误或缺失
- 账户余额不足
- 网络问题
- 模型名称错误或不可用
- API 速率限制

**解决方案：**
1. 检查 `.env` 文件中的所有 API 密钥是否正确
2. 分别登录各提供商控制台查看余额：
   - OpenAI: https://platform.openai.com/usage
   - Anthropic: https://console.anthropic.com/settings/plans
   - Google AI: https://aistudio.google.com/
3. 查看后端终端输出，确认具体是哪个 API 失败
4. 尝试更换模型配置或移除有问题的模型

### 问题 5: 前端无法连接后端

**检查：**
1. 后端是否正常启动（查看终端输出）
2. CORS 配置是否正确（`backend/main.py` 中的 CORS 设置）
3. 浏览器控制台是否有错误信息

### 问题 6: `Module not found` 错误

**解决方案：**
确保从项目根目录运行，并使用正确的命令：
```bash
# ❌ 错误
cd backend
python main.py

# ✅ 正确
python -m backend.main
# 或使用 uv
uv run python -m backend.main
```

## 项目结构说明

```
llm-council/
├── backend/              # FastAPI 后端
│   ├── main.py          # 主程序和 API 路由
│   ├── config.py        # 模型配置和 API 密钥
│   ├── council.py       # 核心逻辑（3 个阶段）
│   ├── openrouter.py    # 多提供商 API 客户端（OpenAI、Anthropic、Google）
│   └── storage.py       # 会话存储（JSON）
├── frontend/            # React + Vite 前端
│   ├── src/
│   │   ├── App.jsx      # 主应用组件
│   │   ├── components/  # UI 组件
│   │   └── api.js       # API 客户端
│   └── package.json
├── data/                # 自动创建的数据目录
│   └── conversations/   # 会话 JSON 文件
├── .env                 # API 密钥配置（需要创建）
├── .env.example         # API 密钥配置模板
├── pyproject.toml       # Python 依赖
├── start.sh             # 启动脚本
└── README.md            # 英文文档
```

## 性能优化建议

1. **并发处理**: 项目已使用异步并发查询多个 LLM，充分利用网络 IO
2. **模型选择**: 根据需求平衡速度和质量（可以混合使用快速和高质量模型）
   - 快速模型：`gpt-4o-mini`, `gemini-2.0-flash-exp`, `claude-haiku-3.5`
   - 高质量模型：`gpt-4o`, `gemini-1.5-pro`, `claude-sonnet-4.5`
3. **网络**: 确保稳定的互联网连接，各提供商 API 响应时间不同

## 安全注意事项

1. **不要提交 .env 文件**到版本控制系统（已在 `.gitignore` 中配置）
2. **定期检查各提供商的账单**，避免意外高额费用：
   - OpenAI 按 token 计费，查看用量仪表盘
   - Anthropic 按 token 计费，有消息数限制
   - Google Gemini 有免费额度，超出后收费
3. **API 密钥**应该保密，不要分享给他人或提交到公开仓库
4. **设置消费限额**：在各提供商控制台设置每月消费上限，防止意外超支

## 停止服务

- 如果使用 `start.sh`：按 `Ctrl+C`
- 如果手动启动：在两个终端中分别按 `Ctrl+C`

## 数据存储

- 会话数据存储在 `data/conversations/` 目录
- 格式为 JSON 文件
- 可以手动删除或备份

## 下一步

项目已经可以使用了！你可以：
- 修改 `backend/config.py` 尝试不同的模型组合
- 查看 `CLAUDE.md` 了解技术细节
- 根据需要自定义 UI 样式

## 获取帮助

如果遇到问题：
1. 查看终端的错误日志
2. 检查浏览器控制台
3. 参考 CLAUDE.md 中的技术说明
4. 查看项目 README.md

---

**祝你使用愉快！🎉**
