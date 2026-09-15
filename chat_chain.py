"""
对话链模块
负责组装RAG对话流程：大模型 + 知识库检索 + 会话记忆
"""
from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from vector_store import init_vector_db
from config import DASHSCOPE_API_KEY, CHAT_MODEL


def create_chat_chain():
    """创建带RAG和会话记忆的完整对话链"""
    # 初始化通义千问大模型
    llm = ChatTongyi(
        model=CHAT_MODEL,
        dashscope_api_key=DASHSCOPE_API_KEY,
        temperature=0.1,
        streaming = True
    )

    # 初始化Milvus知识库检索器，返回最相关的4个文本块
    vector_db = init_vector_db()
    retriever = vector_db.as_retriever(search_kwargs={"k": 4})

    # 对话提示词模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是智能文档问答助手，请严格根据提供的上下文回答用户问题，不要编造内容。\n\n上下文：{context}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    # 检索知识库相关内容作为上下文
    def get_context(question):
        docs = retriever.invoke(question["input"])
        return "\n\n".join([doc.page_content for doc in docs])

    # 组装基础对话链
    chain = (
        {
            "context": get_context,
            "input": lambda x: x["input"],
            "history": lambda x: x["history"]
        }
        | prompt
        | llm
    )

    # 会话记忆存储
    store = {}

    def get_session_history(session_id: str):
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    # 包装成带记忆的对话链
    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )
    return chain_with_history
