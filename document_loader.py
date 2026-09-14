import logging

from langchain_classic import text_splitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, Docx2txtLoader, \
    UnstructuredMarkdownLoader
{
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader
}
#字符分割器
from langchain_text_splitters import RecursiveCharacterTextSplitter
#从配置文件中导入参数
from config import DOCS_DIR,CHUNK_SIZE,CHUNK_OVERLAP

#获取文档内的知识库内容并分割
def load_and_split_docs():
    logging.info("正在加载本地文档...")
    loaders=[
        DirectoryLoader(DOCS_DIR,glob="**/*.txt",loader_cls=TextLoader,Loader_kwargs={"autodetect_endconding":True}),
        DirectoryLoader(DOCS_DIR,glob="**/*.pdf",loader_cls=PyPDFLoader),
        DirectoryLoader(DOCS_DIR,glob="**/*.docs",loader_cls=Docx2txtLoader),
        DirectoryLoader(DOCS_DIR,glob="**/*.pdf",loader_cls=UnstructuredMarkdownLoader)
    ]
    docs=[]
    for loader in loaders:
        docs.extend(loader.load())
    logging.info(f"共加载到{len(docs)}个原始文档")
    #分割
    text_splitter=RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""]
    )
    split_docs=text_splitter.split_documents(docs)
    logging.info(f"切分完成共生成{len(split_docs)}个文本块")
    return split_docs
