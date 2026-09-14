"""
文档加载与切分模块
负责读取本地docs目录下的多格式文档，并切分为适合向量检索的文本块
"""
import logging
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import DOCS_DIR, CHUNK_SIZE, CHUNK_OVERLAP


def load_and_split_docs():
    """加载docs目录下所有文档并切分"""
    logging.info("正在加载本地文档...")

    loaders = [
        DirectoryLoader(DOCS_DIR, glob="**/*.txt", loader_cls=TextLoader,
                        loader_kwargs={"autodetect_encoding": True}),
        DirectoryLoader(DOCS_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader),
        DirectoryLoader(DOCS_DIR, glob="**/*.docx", loader_cls=Docx2txtLoader),
        DirectoryLoader(DOCS_DIR, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader),
    ]

    docs = []
    for loader in loaders:
        docs.extend(loader.load())

    logging.info(f"共加载到{len(docs)}个原始文档")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""]
    )
    split_docs = text_splitter.split_documents(docs)
    logging.info(f"切分完成，共生成{len(split_docs)}个文本块")
    return split_docs
