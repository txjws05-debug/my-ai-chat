# 后端镜像：FastAPI + LangChain + 通义千问
FROM python:3.11-slim

# unstructured 等文档解析依赖需要 libmagic
RUN apt-get update && apt-get install -y --no-install-recommends libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先装依赖，利用构建缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝项目代码与知识库文档（docs/）
COPY . .

EXPOSE 8000

CMD ["python", "api.py"]
