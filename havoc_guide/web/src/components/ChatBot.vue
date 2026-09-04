<script setup>
import { ref, nextTick, watch } from 'vue'
import { state, openLogin } from '../store'

function greeting() {
  if (!state.auth) {
    return state.petGender === 'f'
      ? '要先登录才能跟我聊天哦～登录后我陪你聊符文出装、陪你唠嗑！(๑•̀ㅂ•́)و✧'
      : '登录后即可与我交流。我是大乱斗数据分析师，可为您解答英雄、符文、出装等问题。'
  }
  return '嗨～我是「小海克斯」！有什么英雄、符文、出装问题都可以问我哦～'
}

const msgs = ref([{ role: 'assistant', content: greeting() }])
const input = ref('')
const loading = ref(false)
const listEl = ref(null)

watch(() => state.auth, () => { msgs.value = [{ role: 'assistant', content: greeting() }] })

async function scrollBottom() {
  await nextTick()
  if (listEl.value) listEl.value.scrollTop = listEl.value.scrollHeight
}

async function send() {
  const t = input.value.trim()
  if (!t || loading.value) return
  if (!state.auth) { openLogin(); return }
  msgs.value.push({ role: 'user', content: t })
  input.value = ''
  loading.value = true
  scrollBottom()
  msgs.value.push({ role: 'assistant', content: '' })
  // 通过响应式数组按索引更新，确保逐字实时渲染（不能拿原始对象引用直接改）
  const lastMsg = () => msgs.value[msgs.value.length - 1]
  try {
    const r = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(state.auth && state.auth.token ? { Authorization: 'Bearer ' + state.auth.token } : {}),
      },
      body: JSON.stringify({ messages: msgs.value.slice(0, -1).slice(-12), persona: state.petGender === 'f' ? 'cute' : 'pro' }),
    })
    if (!r.ok || !r.body) throw new Error('bad response')
    const reader = r.body.getReader()
    const decoder = new TextDecoder()
    let buf = ''
    for (;;) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      let idx
      while ((idx = buf.indexOf('\n\n')) >= 0) {
        const chunk = buf.slice(0, idx); buf = buf.slice(idx + 2)
        for (const line of chunk.split('\n')) {
          if (!line.startsWith('data: ')) continue
          try {
            const d = JSON.parse(line.slice(6))
            if (d.text) lastMsg().content += d.text
            if (d.error) lastMsg().content += '（' + d.error + '）'
            scrollBottom()
          } catch (e) {}
        }
      }
    }
    if (!lastMsg().content) lastMsg().content = '（没有收到回复，请重试）'
  } catch (e) {
    if (!lastMsg().content) lastMsg().content = '（网络出问题了，请稍后再试）'
  }
  loading.value = false
  scrollBottom()
}

function close() { state.chatOpen = false }

watch(() => state.chatOpen, async v => { if (v) scrollBottom() })
</script>

<template>
  <div class="chatwin">
    <div class="chat-head">
      <span class="chat-title">小海克斯 · 攻略站 AI 助手</span>
      <button class="chat-close" @click="close">✕</button>
    </div>
    <div class="chat-body" ref="listEl">
      <div v-for="(m, i) in msgs" :key="i" class="chat-msg" :class="m.role">
        <div class="bubble">{{ m.content }}</div>
      </div>
    </div>
    <div class="chat-input-row">
      <template v-if="state.auth">
        <input v-model="input" class="chat-in" placeholder="问问英雄/符文/出装…" @keyup.enter="send">
        <button class="chat-send" :disabled="loading" @click="send">发送</button>
      </template>
      <button v-else class="chat-send full" @click="openLogin()">登录后开始聊天</button>
    </div>
  </div>
</template>

<style scoped>
.chatwin { position:fixed; right:22px; bottom:120px; width:420px; max-width:92vw; height:min(60vh, 560px); background:#fff; border:1px solid var(--line); border-radius:18px; box-shadow:0 16px 48px rgba(0,0,0,.28); display:flex; flex-direction:column; overflow:hidden; z-index:100050; }
html.dark .chatwin { background:#141c2e; }
.chat-head { display:flex; align-items:center; justify-content:space-between; padding:12px 16px; background:linear-gradient(135deg,#2c4a72,#4a6a94); color:#fff; }
.chat-title { font-size:21px; font-weight:700; }
.chat-close { border:0; background:transparent; color:#fff; font-size:22px; cursor:pointer; line-height:1; }
.chat-close:hover { opacity:.8; }
.chat-body { flex:1; overflow-y:auto; padding:14px; display:flex; flex-direction:column; gap:10px; }
.chat-msg { display:flex; }
.chat-msg.user { justify-content:flex-end; }
.chat-msg.assistant { justify-content:flex-start; }
.bubble { max-width:82%; padding:10px 14px; border-radius:14px; font-size:21px; line-height:1.5; white-space:pre-wrap; word-break:break-word; }
.chat-msg.user .bubble { background:linear-gradient(135deg,#2c4a72,#4a6a94); color:#fff; border-bottom-right-radius:4px; }
.chat-msg.assistant .bubble { background:var(--panel2); border:1px solid var(--line); color:var(--txt); border-bottom-left-radius:4px; }
html.dark .chat-msg.assistant .bubble { background:#1c2536; }
.bubble.typing { color:var(--sub); }
.chat-input-row { display:flex; gap:8px; padding:10px 12px; border-top:1px solid var(--line); }
.chat-in { flex:1; background:var(--panel2); border:1px solid var(--line); color:var(--txt); padding:10px 14px; border-radius:10px; font-size:21px; outline:none; }
.chat-in:focus { border-color:var(--blue); }
.chat-send { background:linear-gradient(135deg,#2c4a72,#4a6a94); color:#fff; border:0; border-radius:10px; padding:0 20px; font-size:21px; font-weight:600; cursor:pointer; }
.chat-send:hover { filter:brightness(1.1); }
.chat-send:disabled { opacity:.6; cursor:default; }
.chat-send.full { width:100%; padding:12px 0; }
</style>
