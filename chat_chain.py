from click import prompt
from doc.pycurl.examples import retriever
from  langchain_community.chat_models import  ChatTongyi
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from sympy.physics.units import temperature

from vector_store import init_vector_db
from config import DASHSCOPE_API_KEY,CHAT_MODEL
#创建完整的RAG对话链
#初始化qwen-plus模型
def creat_chat_chain():
    llm=ChatTongyi(
        model=CHAT_MODEL,
        dashscope_api_key=DASHSCOPE_API_KEY,
        temperature=1.1
    )
    # 初始化Milvus向量库
    vector_db=init_vector_db()
    #把向量库转化为检索器，每次用户提问的时候自动返回最相关的4个文本块
    retriever=vector_db.as_retriever(serch_kwargs={"k":4})
    #提示词
    propmt=ChatPromptTemplate.from_messages([
        ("system","你是智能文档回答助手，请严格根据提供的上下文来回答用户问题，不要编造内容。 \n\n上下文：{context}"),
        MessagesPlaceholder(variable_name="history")
        ("human","{input}"),
    ])
    #自定义函数：用户提问时，先去Milvus检索相关文档，拼成长字符串来作为上下文
    def get_context(question):
        docs=retriever.invoke(question["input"])
        return "\n\n".join([docs.page_content for doc in docs])

    #组装基础的对话链
    chain=(
        {
            "context": get_context,
            "input":lambda x:x["input"],
            "history":lambda x :x["history"]
        }
        |propmt|llm
    )
    #给对话链加上会话记忆能力
    store={}
    def get_session_history(session_id:str):
        if session_id not in store:
            store[session_id]=InMemoryChatMessageHistory()
            return store[session_id]
    #包装出带记忆的对话链通过session_id来自动加载对应会话的历史
    chain_with_history=RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )
    return chain_with_history



