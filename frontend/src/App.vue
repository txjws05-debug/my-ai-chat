<!-- ==============================================
  Vue3前端主页面
  布局：左边会话列表，右边聊天窗口，底部输入框
  ============================================== -->
<template>
  <div class="app-container">
    <!-- 左侧边栏：会话列表 -->
    <aside class="sidebar">
      <!-- 新建会话按钮 -->
      <button class="new-chat-btn" @click="createNewSession">+ 新建会话</button>
      <div class="session-list">
        <!-- 循环渲染所有会话 -->
        <div
          v-for="s in sessions"
          :key="s.session_id"
          class="session-item"
          :class="{active: s.session_id === currentSessionId}"
          @click="switchSession(s.session_id)"
        >
          <span class="session-title">{{ s.title }}</span>
          <!-- 点×删除会话，.stop阻止冒泡，不然点×也会触发切换会话 -->
          <button class="delete-btn" @click.stop="deleteSession(s.session_id)">×</button>
        </div>
      </div>
    </aside>

    <!-- 右侧主聊天区域 -->
    <main class="chat-main">
      <header class="header">知识库AI助手</header>
      <!-- 消息展示区，ref用来操作滚动条 -->
      <div class="chat-messages" ref="chatRef">
        <div v-for="(msg, i) in currentMessages" :key="i" class="message" :class="msg.role">
          {{ msg.content }}
        </div>
      </div>
      <!-- 底部输入区 -->
      <div class="input-area">
        <input v-model="input" @keyup.enter="sendMessage" placeholder="输入你的问题...">
        <button @click="sendMessage">发送</button>
      </div>
    </main>
  </div>
</template>

<script setup>
// Vue3组合式API导入
import { ref, onMounted, nextTick } from 'vue'
// axios用来发HTTP请求调后端接口
import axios from 'axios'

// 响应式状态定义
const sessions = ref([])          // 所有会话列表
const currentSessionId = ref('')   // 当前正在聊天的会话ID
const currentMessages = ref([])    // 当前会话的消息列表
const input = ref('')              // 输入框里的内容
const chatRef = ref(null)          // 消息区DOM引用，用来自动滚到底部

// 页面刚加载的时候自动执行：拉取所有会话列表，默认打开第一个
onMounted(async () => {
  const res = await axios.get('/api/sessions')
  sessions.value = res.data.data
  if (sessions.value.length > 0) {
    await switchSession(sessions.value[0].session_id)
  } else {
    // 没有会话就自动新建一个
    await createNewSession()
  }
})

// 新建会话：调后端接口创建，然后切到新会话
const createNewSession = async () => {
  const res = await axios.post('/api/sessions')
  const sessionId = res.data.data
  await switchSession(sessionId)
  // 刷新左边会话列表
  const listRes = await axios.get('/api/sessions')
  sessions.value = listRes.data.data
}

// 切换会话：点击左边某个会话时，加载这个会话的所有历史消息
const switchSession = async (sessionId) => {
  currentSessionId.value = sessionId
  const res = await axios.get(`/api/sessions/${sessionId}`)
  currentMessages.value = res.data.data.messages
  // 等DOM渲染完，自动把聊天框滚到最底部
  await nextTick()
  chatRef.value.scrollTop = chatRef.value.scrollHeight
}

// 删除会话：调后端删接口，然后刷新列表
const deleteSession = async (sessionId) => {
  await axios.delete(`/api/sessions/${sessionId}`)
  const res = await axios.get('/api/sessions')
  sessions.value = res.data.data
  // 如果删的是当前正在看的会话，就自动切到第一个，或者新建一个
  if (currentSessionId.value === sessionId) {
    if (sessions.value.length > 0) {
      await switchSession(sessions.value[0].session_id)
    } else {
      await createNewSession()
    }
  }
}

// 发送消息：先把用户消息显示在界面上，再用fetch流式读取AI回复
const sendMessage = async () => {
  if (!input.value.trim() || !currentSessionId.value) return
  const question = input.value
  input.value = ''
  // 先把用户消息加到界面上
  currentMessages.value.push({ role: 'user', content: question })
  // 先放一个空的AI气泡占位，流式内容会逐字追加进来
  currentMessages.value.push({ role: 'assistant', content: '' })
  await nextTick()
  chatRef.value.scrollTop = chatRef.value.scrollHeight

  // 用fetch发请求（axios不支持流式响应，必须用fetch）
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: currentSessionId.value,
      message: question
    })
  })

  // 请求失败就把占位气泡改成错误提示
  if (!res.ok) {
    currentMessages.value[currentMessages.value.length - 1].content = '（请求失败，请检查后端服务是否启动）'
    return
  }

  const aiIndex = currentMessages.value.length - 1

  // 情况1：后端是流式接口（text/event-stream），边收边渲染
  if ((res.headers.get('content-type') || '').includes('text/event-stream')) {
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      // SSE消息以空行分隔，一条条解析
      const parts = buffer.split('\n\n')
      buffer = parts.pop() // 最后一段可能没接收完，留到下一次
      for (const part of parts) {
        const line = part.trim()
        if (!line.startsWith('data:')) continue
        const data = line.slice(5).trim()
        if (data === '[DONE]') continue // 后端发的流结束标记
        try {
          const obj = JSON.parse(data)
          currentMessages.value[aiIndex].content += obj.content || ''
        } catch (e) { /* 偶发解析失败就跳过这一块 */ }
      }
      // 每收到一块就滚到底部，让用户看着字一个个蹦出来
      await nextTick()
      chatRef.value.scrollTop = chatRef.value.scrollHeight
    }
  } else {
    // 情况2：后端还是老的一次性JSON接口（后端没改之前兜底用），整体显示
    const data = await res.json()
    currentMessages.value[aiIndex].content = data.data
  }

  await nextTick()
  chatRef.value.scrollTop = chatRef.value.scrollHeight
}
</script>

<style scoped>
/* 页面整体布局，左右两栏 */
.app-container {
  display: flex;
  height: 100vh;
}
/* 左侧深色边栏 */
.sidebar {
  width: 260px;
  background: #2f2f2f;
  color: #fff;
  padding: 16px;
  display: flex;
  flex-direction: column;
}
/* 新建会话按钮 */
.new-chat-btn {
  width: 100%;
  padding: 12px;
  background: #42b883;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 16px;
  font-size: 14px;
}
/* 会话列表区域，超出可滚动 */
.session-list {
  flex: 1;
  overflow-y: auto;
}
/* 单个会话项 */
.session-item {
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}
.session-item:hover {
  background: #444;
}
/* 当前选中的会话高亮 */
.session-item.active {
  background: #42b883;
}
/* 删除按钮 */
.delete-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  opacity: 0.6;
}
.delete-btn:hover {
  opacity: 1;
}
/* 右侧主聊天区 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}
.header {
  background: #fff;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  font-weight: 600;
}
/* 消息列表区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
}
/* 单条消息气泡 */
.message {
  margin-bottom: 16px;
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.5;
}
/* 用户消息靠右，绿色气泡 */
.message.user {
  background: #42b883;
  color: #fff;
  margin-left: auto;
}
/* AI消息靠左，白色气泡 */
.message.assistant {
  background: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
/* 底部输入区 */
.input-area {
  padding: 16px;
  background: #fff;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
}
input {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  display: block;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}
button {
  display: block;
  margin: 12px auto 0;
  padding: 10px 32px;
  background: #42b883;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}
</style>
