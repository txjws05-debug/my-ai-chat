import json
import time
from datetime import datetime
from typing import Dict,List
import redis
from docutils.nodes import title

#连接redis decode_response=True表示返回字符串不需要手动转码
r=redis.Redis(host="127.0.0.1",port=6379,db=0,decode_responses=True)

#定义redis的key前缀
SESSION_PREFIX="chat:session:"
#存所有会话Id的列表key，用list类型保证新建 的在最强按摩
SESSION_LIST_KEY="chat:sessions"

def create_session()->str :
    session_id=f"sess_{int(time.time()*1000)}"
    title=datetime.now().strftime("%y-%m-%d_%H-%M-%S_%f")[:-3]
    create_time=time.strftime("%Y-%M-%D %H-%M-%S")
    #初始化会话数据结构
    session_data={
        "session_id":session_id,
        "title":title,
        "create_time":create_time,
        "message":[]#空消息列表
    }
    #把会话数据存到redis里用json序列化
    r.set(f"{SESSION_PREFIX}{session_id}",json.dumps(session_data,ensure_ascii=False))
    #把新会话ID插入到列表最前面
    r.lpush(SESSION_LIST_KEY,session_id)
    return session_id
#从redis读数据
def load_session(session_id:str)-> Dict:
    data=r.get(f"{SESSION_PREFIX}{session_id}")
    if not data:
        raise Exception("会话不存在")
    return json.loads(data)
#更新会话数据
def save_session(session_id:str,session_data:Dict):
    r.set(f"{SESSION_PREFIX}{session_id}",json.dumps(session_data,ensure_ascii=False))
#获取会话列表
def list_session()->List[Dict]:
    session_ids=r.lrange(SESSION_LIST_KEY,0,-1)
    sessions=[]
    for sid in session_ids:
        data=json.loads(r.get(f"{SESSION_PREFIX}{sid}"))
        sessions.append({
            "session_id" :data["session_id"],
            "title":data["title"],
            "create_time":data["create_time"]
        })
    return sessions
#删除会话列表
def delete_session(session_id:str):
    r.delete(f"{SESSION_PREFIX}{session_id}")
    r.lrem(SESSION_LIST_KEY,0,session_id)
