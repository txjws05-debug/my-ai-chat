"""
Milvus向量数据库操作模块
负责知识库向量库的初始化、加载与构建
"""
import logging
from langchain_milvus import Milvus
from langchain_community.embeddings import DashScopeEmbeddings
from pymilvus import connections, utility

from document_loader import load_and_split_docs
from config import (
    DASHSCOPE_API_KEY,
    EMBEDDING_MODEL,
    MILVUS_URI,
    DOC_COLLECTION_NAME
)


def get_embeddings():
    """初始化文本嵌入模型"""
    return DashScopeEmbeddings(
        model=EMBEDDING_MODEL,
        dashscope_api_key=DASHSCOPE_API_KEY
    )


def check_collection_exists(collection_name):
    """判断Milvus中指定集合是否存在"""
    connections.connect(alias="default", uri=MILVUS_URI)
    return utility.has_collection(collection_name)


def build_knowledge_vector_db(embeddings):
    """首次运行：加载本地文档并写入Milvus构建知识库"""
    split_docs = load_and_split_docs()
    vector_db = Milvus.from_documents(
        documents=split_docs,
        embedding=embeddings,
        connection_args={"uri": MILVUS_URI},
        collection_name=DOC_COLLECTION_NAME
    )
    logging.info("知识库向量库构建完成")
    return vector_db


def load_knowledge_vector_db(embeddings):
    """加载已有的知识库集合"""
    vector_db = Milvus(
        embedding_function=embeddings,
        connection_args={"uri": MILVUS_URI},
        collection_name=DOC_COLLECTION_NAME
    )
    return vector_db


def init_vector_db():
    """初始化知识库：存在则直接加载，不存在则新建"""
    embeddings = get_embeddings()
    if check_collection_exists(DOC_COLLECTION_NAME):
        logging.info("检测到已有知识库，直接加载")
        return load_knowledge_vector_db(embeddings)
    else:
        logging.info("首次运行，开始构建知识库")
        return build_knowledge_vector_db(embeddings)
