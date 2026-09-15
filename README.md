# 知识库 AI 助手（my-ai-chat）

基于 **RAG（检索增强生成）** 的智能文档问答系统：把本地文档切分、向量化后存入 Milvus，用户提问时先检索最相关的知识片段，结合多轮对话历史，交给通义千问大模型生成回答，并支持**流式输出**（打字机效果）。

## ✨ 功能特性

- **RAG 知识库问答**：回答严格基于 `docs/` 目录下的文档内容，不依赖模型自身知识，减少幻觉
- **多轮对话记忆**：同一会话自动带上历史上下文
- **流式输出**：回答逐字生成，前端打字机效果，不用干等
- **会话管理**：新建 / 切换 / 删除会话，会话记录持久化到 Redis
- **多格式文档支持**：`.txt` / `.pdf` / `.docx` / `.md`
- **全中文注释**：代码注释完整，适合学习和二次开发

## 🛠 技术栈

| 层次 | 技术 |
| --- | --- |
| 后端框架 | Python 3.11 · FastAPI · Uvicorn |
| 大模型 | 通义千问 `qwen-plus`（阿里云百炼 DashScope） |
| 向量模型 | `text-embedding-v3` |
| 向量数据库 | Milvus |
| 会话存储 | Redis |
| 前端 | Vue 3 · Vite · axios |

## 📁 项目结构

```
my-ai-chat/
├── api.py               # FastAPI 后端接口（REST + SSE 流式聊天）
├── chat_chain.py        # RAG 对话链：检索 + 历史记忆 + 大模型
├── session_store.py     # Redis 会话存储（增删改查）
├── vector_store.py      # Milvus 向量库初始化与构建
├── document_loader.py   # 文档加载与切分
├── config.py            # 全局配置（模型、端口、向量库参数）
├── docs/                # 📚 知识库文档目录（把要问答的文档放这里）
└── frontend/            # Vue3 前端
    ├── src/App.vue      # 主页面（会话列表 + 聊天窗口 + 流式渲染）
    ├── vite.config.js   # 开发代理：/api → localhost:8000
    └── package.json
```

## 🧠 工作原理

```mermaid
flowchart LR
    A[用户提问] --> B[Milvus 检索相关文档片段]
    B --> C[拼接 检索上下文 + 多轮历史 + 当前问题]
    C --> D[通义千问 qwen-plus]
    D --> E[SSE 流式返回]
    E --> F[前端逐字渲染]
    F --> G[回答与问题存入 Redis]
```

首次启动时，系统会把 `docs/` 下的文档自动切分（chunk_size=500、overlap=100）并向量化写入 Milvus 集合 `knowledge_docs`；之后每次提问只检索最相关的 4 个文本块作为上下文。

## ✅ 环境要求

- Python 3.10+
- Node.js 18+（前端）
- Redis（本地 127.0.0.1:6379）
- Milvus（本地 127.0.0.1:19530）
- 阿里云百炼（DashScope）API Key

## 🚀 快速开始

### 1. 配置 API Key

项目通过环境变量 `aliyun` 读取密钥，**推荐用环境变量方式，不要把密钥写进代码**：

```powershell
# Windows PowerShell
setx aliyun "sk-你的APIKey"   # 设置后需重启终端生效

# 或临时生效
$env:aliyun = "sk-你的APIKey"
```

> 也可以直接在 `config.py` 里把 `DASHSCOPE_API_KEY = os.getenv("aliyun")` 改为写死的值，但推送到 GitHub 前务必改回或不要提交。

### 2. 安装后端依赖

```bash
pip install -r requirements.txt
```

`requirements.txt`（可按需安装）：

```
fastapi
uvicorn[standard]
redis
dashscope
langchain-community
langchain-core
langchain-milvus
langchain-text-splitters
pymilvus
pypdf
docx2txt
unstructured
```

### 3. 启动 Redis 和 Milvus

**Redis**（任选其一）：

```bash
# Docker 方式
docker run -d --name redis -p 6379:6379 redis

# Windows 也可使用 WSL2 或 Memurai
```

**Milvus**（Docker 独立部署，推荐）：

```bash
docker run -d --name milvus \
  -p 19530:19530 -p 9091:9091 \
  -e ETCD_USE_EMBED=true \
  -e ETCD_DATA_DIR=/var/lib/milvus/etcd \
  -e COMMON_STORAGETYPE_LOCAL=true \
  -v milvus_data:/var/lib/milvus \
  milvusdb/milvus:v2.4.17
```

### 4. 放入知识库文档

把要问答的文档（`.txt` / `.pdf` / `.docx` / `.md`）放进 `docs/` 目录。首次启动后端时会自动构建向量库。

### 5. 启动后端

```bash
python api.py
```

首次启动会看到"构建知识库"日志（文档越多越久），之后自动加载已有向量库。后端默认监听 `http://localhost:8000`。

### 6. 启动前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 **http://localhost:5173** 即可开始对话。

## 💬 使用说明

1. 左侧 **+ 新建会话** 开始新的对话；点会话项切换历史会话；点 `×` 删除会话
2. 底部输入问题，按回车或点发送
3. 回答会**逐字流式显示**，且严格基于知识库内容作答

## 🔌 API 接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/sessions` | 新建会话 |
| GET | `/api/sessions` | 获取会话列表 |
| GET | `/api/sessions/{session_id}` | 获取会话详情（含历史消息） |
| POST | `/api/chat` | 聊天，SSE 流式返回（`text/event-stream`） |
| DELETE | `/api/sessions/{session_id}` | 删除会话 |

## ⚙️ 配置说明（config.py）

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `DASHSCOPE_API_KEY` | 环境变量 `aliyun` | 阿里云百炼密钥 |
| `CHAT_MODEL` | `qwen-plus` | 对话大模型 |
| `EMBEDDING_MODEL` | `text-embedding-v3` | 向量化模型 |
| `MILVUS_URI` | `http://127.0.0.1:19530` | Milvus 地址 |
| `DOC_COLLECTION_NAME` | `knowledge_docs` | 向量库集合名 |
| `DOCS_DIR` | `./docs` | 知识库文档目录 |
| `CHUNK_SIZE` | `500` | 文档切分块大小（字符） |
| `CHUNK_OVERLAP` | `100` | 切分块重叠长度 |

## ❓ 常见问题

**Q：回答不是逐字出现的，等很久一次性出来？**
新版 langchain-core 必须给 `ChatTongyi` 显式传 `streaming=True` 才会走流式路由，确认 `chat_chain.py` 中模型创建带有该参数，改完重启后端。

**Q：前端页面能打开，但发消息失败/报错？**
检查后端是否已启动（8000 端口）、Redis 和 Milvus 是否运行、环境变量 `aliyun` 是否配置。

**Q：重启后历史会话丢了？**
会话记录存在 Redis，确认 Redis 服务已启动（`redis-cli ping` 应返回 PONG）。

**Q：首次运行很慢？**
首次启动需要构建知识库向量库（加载文档 + 调用向量模型 + 写入 Milvus），属正常现象，之后启动会直接加载。

## 📌 推送到 GitHub 前

- 确认 `.gitignore` 已忽略 `node_modules/`、`__pycache__/`、`.idea/`、`.env` 等目录
- 确认 `config.py` 中没有写死的 API Key（用环境变量）
