# 知识库 AI 助手

基于 RAG 的智能文档问答系统：文档切分向量化存入 Milvus，提问时检索相关知识 + 多轮历史，交给通义千问生成回答，支持流式输出。

## 功能

- RAG 知识库问答，回答基于 `docs/` 目录文档内容
- 多轮对话记忆，会话记录持久化到 Redis
- 流式输出，打字机效果
- 支持 txt / pdf / docx / md
- 会话新建、切换、删除

## 技术栈

FastAPI · LangChain · 通义千问 qwen-plus · Milvus · Redis · Vue3 + Vite · Docker Compose

## 🚀 一键启动（Docker Compose，推荐）

前置条件：安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/) 并启动，配置阿里云百炼 API Key：

```powershell
setx aliyun "sk-你的APIKey"   # 设置后需重新打开终端
```

然后任选一种方式启动：

```bash
# 方式一：双击 start.bat
# 方式二：命令行
docker compose up -d --build
```

启动完成后访问 **http://localhost:8080**（首次构建需几分钟：拉镜像 + 编译前端 + 构建知识库向量库）。

其他常用命令：

```bash
docker compose down        # 停止全部服务
docker compose up -d       # 再次启动（已构建过）
docker compose logs -f backend   # 查看后端日志
```

> 首次启动时后端会自动构建向量库（较慢），并把 `docs/` 目录下的文档作为知识库。之后提问前记得先往 `docs/` 放文档。
> 如果本机 6379 / 19530 / 8000 端口已被占用，请先停掉本地的 Redis 和 Milvus 再启动。

## 💻 本地开发模式

```bash
# 1. 启动 Redis 和 Milvus
docker compose up -d redis milvus

# 2. 安装后端依赖并启动（端口 8000）
pip install -r requirements.txt
python api.py

# 3. 启动前端（端口 5173）
cd frontend && npm install && npm run dev
```

访问 **http://localhost:5173**。

## 项目结构

```
├── docker-compose.yml    # 一键启动编排（Redis + Milvus + 后端 + 前端）
├── start.bat             # Windows 一键启动脚本
├── Dockerfile            # 后端镜像
├── requirements.txt      # 后端依赖
├── api.py                # FastAPI 接口（REST + SSE 流式聊天）
├── chat_chain.py         # RAG 对话链
├── session_store.py      # Redis 会话存储
├── vector_store.py       # Milvus 向量库
├── document_loader.py    # 文档加载与切分
├── config.py             # 全局配置
├── docs/                 # 📚 知识库文档目录
└── frontend/             # Vue3 前端（含 Dockerfile + Nginx 配置）
```

## 配置（config.py）

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `DASHSCOPE_API_KEY` | 环境变量 `aliyun` | 阿里云百炼密钥 |
| `CHAT_MODEL` | `qwen-plus` | 对话大模型 |
| `EMBEDDING_MODEL` | `text-embedding-v3` | 向量模型 |
| `MILVUS_URI` | `http://127.0.0.1:19530` | Milvus 地址（容器内自动覆盖为 `milvus:19530`） |
| `REDIS_HOST` / `REDIS_PORT` | `127.0.0.1` / `6379` | Redis 地址（容器内自动覆盖为 `redis`） |
| `DOC_COLLECTION_NAME` | `knowledge_docs` | 向量库集合名 |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `500` / `100` | 文档切分参数 |

## 接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/sessions` | 新建会话 |
| GET | `/api/sessions` | 会话列表 |
| GET | `/api/sessions/{id}` | 会话详情 |
| POST | `/api/chat` | 聊天（SSE 流式） |
| DELETE | `/api/sessions/{id}` | 删除会话 |

