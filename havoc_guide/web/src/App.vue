<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { state, loadAuth, openLogin, goHome, getJSON, applyPrefs, apiRoot, toast } from './store'
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
const police = ref('')
const hovered = ref(false)
const avatar = computed(() =>
  (state.auth && state.auth.user && state.auth.user.avatar)
    ? state.auth.user.avatar : '/static/preset_avatar.png')

const isLogged = computed(() => !!state.auth)

// 登录按钮：电脑端直接开登录页；手机端先弹「登录后可以」弹层（底部有登录/注册按钮）
function onLoginClick() {
  if (isLogged.value) { state.view = 'profile'; return }
  if (hoverOK) { openLogin(); return }
  state.loginPop = !state.loginPop
}
function popToLogin() { state.loginPop = false; openLogin() }
function onEnter() { hovered.value = true }
function onLeave() { hovered.value = false; state.avatarMenuOpen = false }
const showAvatarMenu = computed(() => isLogged.value && (state.avatarMenuOpen || hovered.value))
// 电脑端：悬浮显示；手机端：点击切换显示（防触屏悬停态卡住）
const showLoginPop = computed(() => !isLogged.value && (hoverOK ? hovered.value : state.loginPop))
const showHeader = computed(() => state.view !== 'profile' && state.view !== 'admin')

let suppressPush = false

// —— 符文效果说明：电脑端=鼠标悬浮提示（原样），手机端=点击居中弹窗（点外部关闭）——
let tipEl, ttEl, __augdesc = null, hoverOK = false
function esc(s) { return String(s ?? '').replace(/[&<>"]/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;' }[c])) }
async function ensureDesc() {
  if (__augdesc) return
  try { __augdesc = {}; const g = await getJSON('/api/augments_all'); g.forEach(gr => (gr.items || []).forEach(a => { if (a.name) __augdesc[a.name] = a.desc || '' })) }
  catch (e) { __augdesc = {} }
}
let tipTimer
function showTip(el) {
  clearTimeout(tipTimer)
  const name = el.getAttribute('data-name') || ''
  const d = (__augdesc && __augdesc[name]) || ''
  tipEl.innerHTML = `<b>${esc(name)}</b>${d ? `<div class="ttdesc">${esc(d)}</div>` : ''}`
  tipEl.style.display = 'block'
}
function hideTip() { clearTimeout(tipTimer); tipTimer = setTimeout(() => { tipEl.style.display = 'none' }, 120) }
function moveTip(e) {
  if (tipEl.style.display === 'none') return
  const pad = 12; let x = e.clientX + 16, y = e.clientY + 16
  const r = tipEl.getBoundingClientRect()
  if (x + r.width > innerWidth - pad) x = e.clientX - r.width - 16
  if (y + r.height > innerHeight - pad) y = e.clientY - r.height - 12
  tipEl.style.left = x + 'px'; tipEl.style.top = y + 'px'
}
function showAugModal(el) {
  const name = el.getAttribute('data-name') || ''
  const qEl = el.querySelector('.q')
  const q = qEl ? qEl.textContent : ''
  const img = el.querySelector('img')
  const icon = (img && img.src) ? `<img class="tm-icon" src="${img.src}" alt="">` : '<span class="tm-icon ph">✦</span>'
  const d = (__augdesc && __augdesc[name]) || ''
  ttEl.querySelector('.ttcard').innerHTML =
    `${icon}<div class="tm-name">${esc(name)}${q ? `<span class="q ${esc(q)}">${esc(q)}</span>` : ''}</div>` +
    `<div class="tm-desc">${d ? esc(d) : '（暂无描述）'}</div><div class="tm-hint">点击空白处关闭</div>`
  ttEl.style.display = 'flex'
}
function hideAugModal() { ttEl.style.display = 'none' }

function syncHeaderH() {
  const h = document.querySelector('header')
  if (h) document.documentElement.style.setProperty('--headerh', (h.offsetHeight) + 'px')
}

// 深链接：/#/champ/<id> 、 /#/category/<名> → 直接进入对应页面
function routeUrl() {
  if (state.view === 'champ') return '#/champ/' + state.champId
  if (state.view === 'category') return '#/category/' + encodeURIComponent(state.cat)
  return '#/' + state.view
}
function parseHash() {
  const h = (location.hash || '').replace(/^#\/?/, '')
  const cm = h.match(/^champ\/(\d+)/)
  if (cm) { state.champId = cm[1]; state.view = 'champ'; return }
  const ct = h.match(/^category\/(.+)/)
  if (ct) { state.cat = decodeURIComponent(ct[1]); state.view = 'category' }
}

onMounted(() => {
  loadAuth()
  applyPrefs()
  syncHeaderH()
  checkAnnouncements()   // 已登录（记住登录态）→ 检查未读公告
  window.addEventListener('resize', syncHeaderH)
  getJSON('/api/site').then(d => { if (d) { if (d.game_version) ver.value = d.game_version; if (d.icp) icp.value = d.icp; if (d.police) police.value = d.police } }).catch(() => {})
  // 符文说明：电脑（有鼠标）→ 悬浮提示；手机（触摸）→ 点击居中弹窗
  hoverOK = window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches
  tipEl = document.createElement('div'); tipEl.className = 'tt'; tipEl.style.display = 'none'; document.body.appendChild(tipEl)
  ttEl = document.createElement('div'); ttEl.className = 'ttov'; ttEl.style.display = 'none'
  ttEl.innerHTML = '<div class="ttcard"></div>'
  document.body.appendChild(ttEl)
  ensureDesc()
  document.addEventListener('mouseover', e => { if (!hoverOK) return; const el = e.target.closest && e.target.closest('[data-name]'); if (el) showTip(el) })
  document.addEventListener('mousemove', e => { if (hoverOK) moveTip(e) })
  document.addEventListener('mouseout', e => { if (!hoverOK) return; const el = e.target.closest && e.target.closest('[data-name]'); if (el && !el.contains(e.relatedTarget)) hideTip() })
  ttEl.addEventListener('click', e => { if (!(e.target instanceof Element) || !e.target.closest('.ttcard')) hideAugModal() })
  document.addEventListener('keydown', e => { if (e.key === 'Escape') hideAugModal() })
  document.addEventListener('click', e => {
    if (hoverOK) return
    const t = e.target
    const el = (t instanceof Element) && t.closest('[data-name]')
    if (el) {
      e.stopPropagation()   // 点符文卡不再触发所在行/卡片的跳转
      if (state.loginPop) state.loginPop = false
      showAugModal(el)
      return
    }
    // 点「登录后可以」弹层以外区域 → 关闭
    if (state.loginPop && !((t instanceof Element) && t.closest('.loginwrap'))) state.loginPop = false
  }, true)
  // 浏览器后退/前进 → 切换视图
  window.addEventListener('popstate', (e) => {
    const s = e.state || {}
    suppressPush = true
    state.view = s.view || 'home'
    state.champId = s.champId || ''
    state.cat = s.cat || ''
    suppressPush = false
  })
  // 首次进入：解析深链接（如 /#/champ/804）
  parseHash()
  history.replaceState({ view: state.view, champId: state.champId, cat: state.cat }, '', routeUrl())
  trackView()   // 首次访问也打点一次
})
// 切换页面/点标题 → 立即换桌宠语录气泡
function titleHome() {
  if (state.view !== 'home') { goHome() }  // 视图变化由下面 watch 触发气泡
  else { state.petTick++ }                 // 已在主页：直接触发一次
}

// 访问统计打点：每次视图变化上报一次（管理员自己的浏览由后端排除）
function trackView() {
  try {
    fetch('/api/pv', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(state.auth && state.auth.token ? { Authorization: 'Bearer ' + state.auth.token } : {}),
      },
      body: JSON.stringify({ view: state.view }),
    }).catch(() => {})
  } catch (e) {}
}

// —— 官方公告弹窗：登录后若有未读公告，弹出展示；点「我知道了」全部标记已读 ——
const annPop = ref(false)
const popAnns = ref([])
let annChecking = false
async function checkAnnouncements() {
  if (!state.auth || !state.auth.token || annChecking) return
  annChecking = true
  try {
    const r = await apiRoot('announcements')
    if (r.ok) {
      const unreads = (r.announcements || []).filter(a => !a.read)
      if (unreads.length) { popAnns.value = unreads; annPop.value = true }
    }
  } catch (e) {} finally { annChecking = false }
}
async function dismissAnnPop() {
  const list = popAnns.value.slice()
  annPop.value = false
  for (const a of list) {
    try { await apiRoot('announcements/' + a.id + '/read', {}, 'POST') } catch (e) {}
  }
  popAnns.value = []
}

// 视图变化 → 清悬停/登录弹层 + 记录历史（后退可用）+ 立即换气泡 + 访问打点
watch(() => state.view, () => {
  hovered.value = false; state.avatarMenuOpen = false; state.loginPop = false
  state.petTick++
  trackView()
  if (suppressPush) return
  history.pushState({ view: state.view, champId: state.champId, cat: state.cat }, '', routeUrl())
})

// 登录/登出 → 检查未读公告（登录成功立即弹窗）
watch(() => state.auth && state.auth.token, tok => { if (tok) checkAnnouncements() })
</script>

<template>
  <div class="bgfix" v-if="state.bgLayer"
       :style="{ backgroundImage: 'url(' + state.bgLayer.img + ')', backgroundPosition: state.bgLayer.pos }"></div>

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
      <div v-if="showLoginPop" class="loginpop on"><b>登录后可以：</b><div>· 发表评论</div><div>· 自定义网页背景</div><div>· 锁定 Q 版人物形象</div><div>· 改变网站风格</div><div>· 与 AI 助手聊天</div><button class="loginpop-btn" @click="popToLogin">登录 / 注册</button></div>
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
    <p v-if="icp || police" class="beian">
      <span v-if="icp"><a href="https://beian.miit.gov.cn" target="_blank" rel="noopener">{{ icp }}</a></span>
      <span v-if="icp && police">　|　</span>
      <span v-if="police"><a href="https://www.beian.gov.cn" target="_blank" rel="noopener">{{ police }}</a></span>
    </p>
  </footer>

  <div class="verlabel" v-if="ver">游戏版本 {{ ver }}</div>
  <LoginModal v-if="state.loginOpen" />
  <Pet />
  <ChatBot v-if="state.chatOpen" />

  <!-- 官方公告弹窗（登录后未读公告自动弹出） -->
  <div v-if="annPop" class="ann-ov">
    <div class="ann-card">
      <div class="ann-pop-head">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="5.5" width="19" height="13" rx="2.5"/><path d="M3.5 7.5l8.5 6 8.5-6"/></svg>
        <span>官方消息</span>
        <button class="ann-x" @click="dismissAnnPop">✕</button>
      </div>
      <div class="ann-pop-list">
        <div v-for="a in popAnns" :key="a.id" class="ann-pop-item">
          <div class="ann-pop-title">{{ a.title }}</div>
          <div class="ann-pop-body">{{ a.content }}</div>
        </div>
      </div>
      <div class="ann-pop-btns">
        <button class="pc-btn ok" @click="dismissAnnPop">我知道了</button>
      </div>
    </div>
  </div>
</template>
