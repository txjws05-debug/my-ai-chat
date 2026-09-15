import logging
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from typing import Any
import json

from sympy import false

# 导入对话链和会话操作函数
from chat_chain import create_chat_chain
from session_store import create_session, load_session, save_session,list_sessions, delete_session
from fastapi.responses import StreamingResponse
# 开启日志
logging.basicConfig(level=logging.INFO)

# 初始化FastAPI
app = FastAPI(title="知识库AI助手")
router = APIRouter()

# 统一返回格式
class ApiResponse(BaseModel):
    code: int = 200
    message: str = ""
    data: Any = None

# 聊天接口请求体
class ChatRequest(BaseModel):
    session_id: str
    message: str

chain = None

# 服务启动时初始化对话链
@app.on_event("startup")
def startup():
    global chain
    chain = create_chat_chain()
    logging.info("服务启动完成，访问 http://localhost:5173 即可聊天")

# 新建会话
@router.post("/api/sessions")
def create_session_api() -> ApiResponse:
    logging.info("创建会话")
    session_id = create_session()
    return ApiResponse(code=200, message="创建会话成功", data=session_id)

# 核心聊天接口
@router.post("/api/chat")
async def chat(request: ChatRequest) -> ApiResponse:
    print(f"与AI交互 流式输出：\n\n")
    session_data=load_session(request.session_id)
    async def generate():
        full_text=""
        async for chunk in chain.astream(
                {"input":request.message},
                config={"configurable":{"session_id":request.session_id}}
        ):
            piece=chunk.content
            full_text+=piece
            yield f"data:{json.dumps({'content':piece},ensure_ascii=False)}\n\n"
            #流结束，回答攒齐了再存历史
        session_data["messages"].append({"role":"user","content":request.message})
        session_data["messages"].append({"role":"assistant","content":full_text})
        yield "data:[DONE]\n\n"
        save_session(request.session_id,session_data)
    return StreamingResponse(generate(),media_type="text/event-stream")


# 获取会话列表
@router.get("/api/sessions")
def get_sessions_list() -> ApiResponse:
    logging.info("获取会话列表")
    return ApiResponse(code=200, message="获取会话列表成功", data=list_sessions())

# 获取指定会话详情
@router.get("/api/sessions/{session_id}")
def get_session_detail(session_id: str) -> ApiResponse:
    logging.info(f"获取指定的会话信息：{session_id}")
    session_data = load_session(session_id)
    return ApiResponse(code=200, message="获取会话信息成功", data=session_data)

# 删除会话
@router.delete("/api/sessions/{session_id}")
def delete_session_api(session_id: str) -> ApiResponse:
    logging.info(f"删除指定会话")
    delete_session(session_id)
    return ApiResponse(code=200, message="删除会话信息成功", data=None)

# 注册路由
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
