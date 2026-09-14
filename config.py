import  os


#DashScope(阿里云百炼)APi配置
DASHSCOPE_API_KEY=os.getenv("aliyun")
CHAT_MODEL="qwen-plus"
EMBEDDING_MODEL="text-embedding-v3"


#Milvus向量数据库配置（Docker部署的本地Milvus）
#默认端口为19530，Docker启动后直接连

MIlLVUS_URI="http://127.0.0.1:19530"
DOC_COLLECTION_NAME="knowledge_docs"

#文档切分配置

DOCS_DIR=".docs"

CHUNK_SIZE="500"
CHUNK_OVERLAP=100