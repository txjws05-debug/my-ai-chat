from docutils.parsers.rst.directives import uri
from langchain_milvus import Milvus
import logging
from langchain_community.embeddings import DashScopeEmbeddings
from pygments.lexer import default

from pymilvus import connections,utility
from sqlalchemy.testing.plugin.plugin_base import logging

from  document_loader import load_and_split_docs
from config import (
DASHSCOPE_API_KEY,
EMBEDDING_MODEL,
MIlLVUS_URI,
DOC_COLLECTION_NAME
)
#把文本转换为向量
def get_embeddings():
    return DashScopeEmbeddings(
        model=EMBEDDING_MODEL,
        dashscope_api_key=DASHSCOPE_API_KEY
    )
#判断Milvus中的db_01数据库中是否有指定集合
def check_collection_exists(collection_name):
    connections.connect(alias="db_01",uri=MIlLVUS_URI)
    return utility.has_collection(collection_name)
#首次运行把文档写入Milvus向量库中
def build_knowledge_vector_db(embeddings):
    split_dos=load_and_split_docs()
    vector_db=Milvus.from_documents(
        documents=split_dos,
        embedding=embeddings,
        connections_args={"uri":MIlLVUS_URI},
        collection_name=DOC_COLLECTION_NAME
    )
    logging.info(f"知识向量库构建完成")
    return vector_db
#非首次运行直接加载Milvus里面已经存在的知识库集合
def load_knowledge_vector_db(embeddings)
    vector_db=Milvus(
        embedding_function=embeddings,
        connection_args={"uri":MIlLVUS_URI},
        collection_name=DOC_COLLECTION_NAME
    )
def init_vector_db():
    embeddings=get_embeddings()
    if check_collection_exists(DOC_COLLECTION_NAME):
        logging.info("已经有知识库，直接加载")
        load_knowledge_vector_db(embeddings)
    else:
        print("首次运行，开始构建数据库")
        return build_knowledge_vector_db(embeddings)
