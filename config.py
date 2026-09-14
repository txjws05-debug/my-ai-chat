"""
全局配置文件
所有参数集中管理，方便修改
"""
import os

# DashScope（阿里云百炼）API配置
DASHSCOPE_API_KEY =os.getenv("aliyun")
CHAT_MODEL = "qwen-plus"
EMBEDDING_MODEL = "text-embedding-v3"

# Milvus向量数据库连接配置
MILVUS_URI = "http://127.0.0.1:19530"
DOC_COLLECTION_NAME = "knowledge_docs"

# 文档处理配置
DOCS_DIR = "./docs"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
