import logging
from urllib import response

from fastapi import FastAPI,APIRouter
from openai.types.beta import assistant
from  pydantic import BaseModel
from typing import Any
#导入对话链创建函数
from  chat_chain import creat_chat_chain
from session_store import create_session,load_session,save_session,list_session,delete_session
#开启日志，方便看请求记录
logging.basicConfig(level=logging.INFO)

#初始化FastAPI应用
app=FastAPI(title="知识库ai助手")

#路由分组，所有/api开头的接口都放在这个router里

router=APIRouter()
#定义统一返回格式，前端所有的接口都返回这个结构
class ApiResponse(BaseModel):
    code:int=200
    message:str=""
    data:Any=None

#定义chat接口的请求头格式
class ChatRequest(BaseModel):
    session_id:str
    message:str
chain=None

#FastAPI启动时自动执行
@app.on_event("startup")
def startup():
    global chain
    chain=creat_chat_chain()
    logging.info("服务启动完成访问http://localhost:5173 即可聊天")
#新建会话
@router.post("/api/sessions")
def create_session_api()-> ApiResponse:
    logging.info("创建会话")
    session_id=create_session()
    return ApiResponse(code=200,message="创建会话成功",data=session_id)

#核心聊天接口
#读历史->调大模型->把新问他存回历史
@router.post("/api/chat")
def chat(request:ChatRequest) ->ApiResponse:
    logging.info(f"与AI交互：{request.session_id}:{request.message}")
    #从Redis加载这个会话之前的所有聊天记录
    session_data=load_session(request.session_id)
    #调用RAG对话链，把用户问题发给大模型，自动检索知识库
    response=chain.invoke(
        {"intput":request.message},
        config={"configurable":{"session_id":request.session_id}}
    )
    ai_response=response.content
    #把本次用户问题和AI回答追加到历史记录里面存回Redis
    session_data["messages"].append({"role":"user","content":request.message})
    session_data["messages"].append({"role":"assistant","content":ai_response})
    save_session(request.session_id,session_data)
    return ApiResponse(code=200,message="获取AI回复成功",data=ai_response)

#从左侧会话来获取完整的聊天记录
@router.get("/api/sessions/{session_id")
def get_session_detail(session_id:str) ->ApiResponse:
    logging.info(f"获取指定的会话信息{session_id}")
    session_data=load_session(session_id)
    return  ApiResponse(code=200,message="获取会话信息成功",data=session_data)

@router.delete("/api/sessions/{session_id}")
def delete_session_api(session_id:str)->ApiResponse:
    logging.info("删除指定会话")
    delete_session(session_id)
    return   ApiResponse(code=200,message="删除会话信息成功",data=None)



