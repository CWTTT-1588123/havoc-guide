<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { state, loadAuth, openLogin, goHome, getJSON, applyPrefs, toast } from './store'
import LoginModal from './components/LoginModal.vue'
import AvatarMenu from './components/AvatarMenu.vue'
import ProfileView from './components/ProfileView.vue'
import AdminView from './components/AdminView.vue'
import HomeView from './components/HomeView.vue'
import DetailView from './components/DetailView.vue'
import CategoryView from './components/CategoryView.vue'
import AllAugmentsView from './components/AllAugmentsView.vue'
import SectionView from './components/SectionView.vue'
import Pet from './components/Pet.vue'
import ChatBot from './components/ChatBot.vue'

const ver = ref('')
const icp = ref('')
const hovered = ref(false)
const avatar = computed(() =>
  (state.auth && state.auth.user && state.auth.user.avatar)
    ? state.auth.user.avatar : '/static/preset_avatar.png')

const isLogged = computed(() => !!state.auth)

function onLoginClick() { if (isLogged.value) { state.view = 'profile' } else { openLogin() } }
function onEnter() { hovered.value = true }
function onLeave() { hovered.value = false; state.avatarMenuOpen = false }
const showAvatarMenu = computed(() => isLogged.value && (state.avatarMenuOpen || hovered.value))
const showLoginPop = computed(() => !isLogged.value && hovered.value)
const showHeader = computed(() => state.view !== 'profile' && state.view !== 'admin')

let suppressPush = false

// —— 符文效果悬浮提示（全局委托）——
let ttEl, __augdesc = null
function esc(s) { return String(s ?? '').replace(/[&<>"]/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;' }[c])) }
async function ensureDesc() {
  if (__augdesc) return
  try { __augdesc = {}; const g = await getJSON('/api/augments_all'); g.forEach(gr => (gr.items || []).forEach(a => { if (a.name) __augdesc[a.name] = a.desc || '' })) }
  catch (e) { __augdesc = {} }
}
let ttTimer
function showTT(el) {
  clearTimeout(ttTimer)
  const name = el.getAttribute('data-name') || ''
  const d = (__augdesc && __augdesc[name]) || ''
  ttEl.innerHTML = `<b>${esc(name)}</b>${d ? `<div class="ttdesc">${esc(d)}</div>` : ''}`
  ttEl.style.display = 'block'
}
function hideTT() { clearTimeout(ttTimer); ttTimer = setTimeout(() => { ttEl.style.display = 'none' }, 120) }
function moveTT(e) {
  if (ttEl.style.display === 'none') return
  const pad = 12; let x = e.clientX + 16, y = e.clientY + 16
  const r = ttEl.getBoundingClientRect()
  if (x + r.width > innerWidth - pad) x = e.clientX - r.width - 16
  if (y + r.height > innerHeight - pad) y = e.clientY - r.height - 12
  ttEl.style.left = x + 'px'; ttEl.style.top = y + 'px'
}

function syncHeaderH() {
  const h = document.querySelector('header')
  if (h) document.documentElement.style.setProperty('--headerh', (h.offsetHeight) + 'px')
}

onMounted(() => {
  loadAuth()
  applyPrefs()
  syncHeaderH()
  window.addEventListener('resize', syncHeaderH)
  getJSON('/api/site').then(d => { if (d) { if (d.game_version) ver.value = d.game_version; if (d.icp) icp.value = d.icp } }).catch(() => {})
  // 符文效果悬浮提示
  ttEl = document.createElement('div'); ttEl.className = 'tt'; ttEl.style.display = 'none'; document.body.appendChild(ttEl)
  ensureDesc()
  document.addEventListener('mouseover', e => { const el = e.target.closest && e.target.closest('[data-name]'); if (el) showTT(el) })
  document.addEventListener('mousemove', moveTT)
  document.addEventListener('mouseout', e => { const el = e.target.closest && e.target.closest('[data-name]'); if (el && !el.contains(e.relatedTarget)) hideTT() })
  // 浏览器后退/前进 → 切换视图
  window.addEventListener('popstate', (e) => {
    const s = e.state || {}
    suppressPush = true
    state.view = s.view || 'home'
    state.champId = s.champId || ''
    state.cat = s.cat || ''
    suppressPush = false
  })
  // 首次进入：替换当前历史（replacestate，避免初始多出一条）
  history.replaceState({ view: 'home', champId: '', cat: '' }, '', '#/home')
})
// 切换页面/点标题 → 立即换桌宠语录气泡
function titleHome() {
  if (state.view !== 'home') { goHome() }  // 视图变化由下面 watch 触发气泡
  else { state.petTick++ }                 // 已在主页：直接触发一次
}

// 视图变化 → 清悬停 + 记录历史（后退可用）+ 立即换气泡
watch(() => state.view, () => {
  hovered.value = false; state.avatarMenuOpen = false
  state.petTick++
  if (suppressPush) return
  history.pushState({ view: state.view, champId: state.champId, cat: state.cat }, '', '#/' + state.view)
})
</script>

<template>
  <header v-if="showHeader">
    <h1 class="titlebtn" @click="titleHome">
      <img class="lollogo" alt="LoL" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImciIHgxPSIwIiB5MT0iMCIgeDI9IjEiIHkyPSIxIj48c3RvcCBvZmZzZXQ9IjAiIHN0b3AtY29sb3I9IiNmMmQ2ODkiLz48c3RvcCBvZmZzZXQ9Ii41IiBzdG9wLWNvbG9yPSIjYzk5NzFmIi8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjOWM3NDE4Ii8+PC9saW5lYXJHcmFkaWVudD48bGluZWFyR3JhZGllbnQgaWQ9ImIiIHgxPSIwIiB5MT0iMCIgeDI9IjEiIHkyPSIxIj48c3RvcCBvZmZzZXQ9IjAiIHN0b3AtY29sb3I9IiM2M2MwZmYiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiMyYzVhOWEiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0OCIgZmlsbD0idXJsKCNnKSIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iNTAiIHI9IjM5IiBmaWxsPSIjMGUxNjMwIi8+PGNpcmNsZSBjeD0iNTAiIGN5PSI1MCIgcj0iMzYiIGZpbGw9Im5vbmUiIHN0cm9rZT0idXJsKCNnKSIgc3Ryb2tlLXdpZHRoPSIxLjQiIG9wYWNpdHk9Ii41Ii8+PHBhdGggZD0iTTMzIDI0IEw0OCAyNCBMNDggNTYgTDcxIDU2IEw3MSA3MiBMMzMgNzIgWiIgZmlsbD0idXJsKCNnKSIgc3Ryb2tlPSIjN2E1YTEwIiBzdHJva2Utd2lkdGg9IjAuNyIvPjxwb2x5Z29uIHBvaW50cz0iNjAsMzQgNzAsNDMgNjAsNTIgNTAsNDMiIGZpbGw9InVybCgjYikiLz48Y2lyY2xlIGN4PSI2MCIgY3k9IjQzIiByPSIyIiBmaWxsPSIjZGZmMGZmIi8+PHBhdGggZD0iTTM4IDcgaDI0IiBzdHJva2U9InVybCgjZykiIHN0cm9rZS13aWR0aD0iMi42IiBzdHJva2UtbGluZWNhcD0icm91bmQiLz48L3N2Zz4=">
      <span>海克斯大乱斗攻略站</span>
    </h1>
    <div class="sbar">
      <span class="sb-ico"><svg width="22" height="22" viewBox="0 0 24 24" fill="none"><circle cx="10" cy="10" r="7" stroke="currentColor" stroke-width="2"/><path d="M15 15 L20 20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></span>
      <input v-model="state.q" class="sb-in" type="text" autocomplete="off" placeholder="搜索英雄">
      <button class="sb-btn" @click="state.q = ''">搜索</button>
    </div>
    <div class="loginwrap" :class="{ logged: isLogged }" @mouseenter="onEnter" @mouseleave="onLeave">
      <button class="loginbtn" @click="onLoginClick">
        <template v-if="isLogged"><img class="login-av" :src="avatar" alt=""></template>
        <template v-else>登录/注册</template>
      </button>
      <div v-if="showLoginPop" class="loginpop on"><b>登录后可以：</b><div>· 发表评论</div><div>· 自定义网页背景</div><div>· 锁定 Q 版人物形象</div><div>· 改变网站风格</div><div>· 与 AI 助手聊天</div></div>
      <AvatarMenu v-if="showAvatarMenu" />
    </div>
  </header>

  <main class="box">
    <HomeView v-if="state.view === 'home'" />
    <DetailView v-else-if="state.view === 'champ'" />
    <SectionView v-else-if="state.view === 'section'" />
    <CategoryView v-else-if="state.view === 'category'" />
    <AllAugmentsView v-else-if="state.view === 'augments'" />
    <ProfileView v-else-if="state.view === 'profile'" />
    <AdminView v-else-if="state.view === 'admin'" />
  </main>

  <footer class="site-foot">
    <p>本站为<b>非商业性</b>的个人学习/分享站点；英雄联盟及英雄、符文、装备等权利归 <b>Riot Games</b> 所有，数据仅供学习交流，不用于任何商业用途。</p>
    <p>部分图片（含 Q 版形象）来自网络，版权归原作者所有；<b>Q 版形象均来自「堆糖」</b>（<a href="https://www.duitang.com" target="_blank" rel="noopener">duitang.com</a>）。如涉及版权问题，请联系删除。</p>
    <p>联系邮箱：<a href="mailto:19162860223@163.com">19162860223@163.com</a>（版权问题 / 侵权删除请联系）</p>
  </footer>

  <div class="verlabel" v-if="ver">游戏版本 {{ ver }}<span v-if="icp">　·　<a href="https://beian.miit.gov.cn" target="_blank" rel="noopener">{{ icp }}</a></span></div>
  <LoginModal v-if="state.loginOpen" />
  <Pet />
  <ChatBot v-if="state.chatOpen" />
</template>
