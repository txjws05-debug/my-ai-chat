"""
会话存储模块
所有会话元数据和聊天记录都持久化存储到Redis
"""
import json
import time
from datetime import datetime
from typing import Dict, List
import redis

# 连接本地Redis，decode_responses=True表示返回字符串无需手动转码
r = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)

# Redis Key前缀
SESSION_PREFIX = "chat:session:"
SESSION_LIST_KEY = "chat:sessions"


def create_session() -> str:
    """新建空会话，返回会话ID"""
    session_id = f"sess_{int(time.time() * 1000)}"
    # 会话标题使用当前时间戳
    title = datetime.now().strftime("%y-%m-%d_%H-%M-%S_%f")[:-3]
    create_time = time.strftime("%Y-%m-%d %H:%M:%S")

    session_data = {
        "session_id": session_id,
        "title": title,
        "create_time": create_time,
        "messages": []
    }

    r.set(f"{SESSION_PREFIX}{session_id}", json.dumps(session_data, ensure_ascii=False))
    r.lpush(SESSION_LIST_KEY, session_id)
    return session_id


def load_session(session_id: str) -> Dict:
    """加载指定会话的完整数据，包含所有历史消息"""
    data = r.get(f"{SESSION_PREFIX}{session_id}")
    if not data:
        raise Exception("会话不存在")
    return json.loads(data)


def save_session(session_id: str, session_data: Dict):
    """更新保存会话数据"""
    r.set(f"{SESSION_PREFIX}{session_id}", json.dumps(session_data, ensure_ascii=False))


def list_sessions() -> List[Dict]:
    """获取所有会话简要列表，用于侧边栏展示"""
    session_ids = r.lrange(SESSION_LIST_KEY, 0, -1)
    sessions = []
    for sid in session_ids:
        data = json.loads(r.get(f"{SESSION_PREFIX}{sid}"))
        sessions.append({
            "session_id": data["session_id"],
            "title": data["title"],
            "create_time": data["create_time"]
        })
    return sessions


def delete_session(session_id: str):
    """删除指定会话"""
    r.delete(f"{SESSION_PREFIX}{session_id}")
    r.lrem(SESSION_LIST_KEY, 0, session_id)
