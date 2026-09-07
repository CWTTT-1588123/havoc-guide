import { reactive } from 'vue'

export const state = reactive({
  auth: null,        // { token, user } 或 null
  loginOpen: false,
  loginPop: false,   // 手机端「登录后可以」弹层（点击登录按钮切换，非悬浮）
  avatarMenuOpen: false,
  view: 'home',      // 'home' | 'profile' | 'admin' | 'champ' | 'category' | 'augments'
  cat: '',           // 当前分类（view==='category' 时）
  champId: '',       // 当前英雄 id（view==='champ' 时）
  petLock: null,     // 锁定的桌宠列表（Q版）
  q: '',             // 全局搜索关键字（顶栏搜索框 <-> 首页列表共用）
  section: { cid: '', key: '' },  // 详情页"更多"跳转的板块（view==='section'）
  chatOpen: false,   // AI 聊天窗是否打开
  petTick: 0,        // 每 +1 = 触发一次桌宠随机语录气泡（页面切换/点标题时随机触发）
  petGender: 'm',    // 当前桌宠性别：'m'=男(专业人设) / 'f'=女(活泼人设)
  bgLayer: null,     // 自定义背景图层 {img, pos}（fixed 全屏层，手机也固定大小）
})

// Q 版桌宠名单
export const PET_IMGS = [
  ['ashe_pet.png','艾希','f'],['leesin_pet.png','盲僧','m'],['ahri_pet.png','阿狸','f'],['missfortune_pet.png','女枪','f'],
  ['ezreal_pet.png','伊泽瑞尔','m'],['lux_pet.png','拉克丝','f'],['riven_pet.png','锐雯','f'],['orianna_pet.png','发条','f'],
  ['sona_pet.png','琴女','f'],['yasuo_pet.png','亚索','m'],['annie_pet.png','安妮','f'],
]
export const BG_PRESETS = [
  {name:'默认', css:''},
  {name:'天空蓝', css:'linear-gradient(180deg,#eaf4ff,#aecff5)'},
  {name:'樱花粉', css:'linear-gradient(180deg,#fdeff3,#f2c3d4)'},
  {name:'薄荷绿', css:'linear-gradient(180deg,#eef9f2,#bfe6cc)'},
  {name:'浅紫', css:'linear-gradient(180deg,#f3effc,#cfbcf0)'},
  {name:'暖杏', css:'linear-gradient(180deg,#fdf3e9,#f5d6ba)'},
  {name:'晴空青', css:'linear-gradient(180deg,#e6f7ff,#b3e0f5)'},
]
export const DARK_PRESETS = [
  {name:'默认深色', css:''},
  {name:'深空黑', css:'linear-gradient(180deg,#000000,#080a12)'},
  {name:'夜幕蓝', css:'linear-gradient(180deg,#0b1226,#15233f)'},
  {name:'暗金', css:'linear-gradient(180deg,#141220,#241f33)'},
  {name:'深紫', css:'linear-gradient(180deg,#140f26,#231740)'},
  {name:'墨绿', css:'linear-gradient(180deg,#0c1a16,#152922)'},
  {name:'暗红', css:'linear-gradient(180deg,#1a0e14,#2c1720)'},
]

function prefsKey() { return 'dsh_prefs_' + (state.auth && state.auth.user ? state.auth.user.id : 'guest') }
export function loadPrefs() { try { return JSON.parse(localStorage.getItem(prefsKey())) || {} } catch (e) { return {} } }
export function savePrefs(p) { localStorage.setItem(prefsKey(), JSON.stringify(p)); if (state.auth && state.auth.token) { apiAuth('prefs', p) } }

export function applyPrefs() {
  const p = loadPrefs()
  const dark = p.theme === 'dark'
  document.documentElement.classList.toggle('dark', dark)
  // 背景：自定义图片走 fixed 全屏层（电脑/手机都固定大小）；预设渐变走 body
  const set = dark ? DARK_PRESETS : BG_PRESETS
  const matched = p.bg && set.some(x => x.css === p.bg)
  if (p.bgImg) {
    state.bgLayer = { img: p.bgImg, pos: p.bgPos || 'center' }
    document.body.style.background = 'transparent'
  } else {
    state.bgLayer = null
    document.body.style.background = matched ? p.bg : ''
  }
  // 桌宠锁定
  const newLock = (state.auth && Array.isArray(p.pets) && p.pets.length) ? p.pets.slice() : null
  window.__petLock = newLock
  state.petLock = newLock
}

// —— auth ——
export function loadAuth() { try { state.auth = JSON.parse(localStorage.getItem('dsh_auth')) || null } catch (e) { state.auth = null } }
export function saveAuth(a) {
  state.auth = a
  if (a) { localStorage.setItem('dsh_auth', JSON.stringify(a)) } else { localStorage.removeItem('dsh_auth') }
  applyPrefs()
  if (a && a.token) { loadServerPrefs() }
}
function updateAuthUser(user) { if (state.auth) { state.auth.user = user; saveAuth(state.auth) } }

export async function apiAuth(path, body) {
  const r = await fetch('/api/auth/' + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(state.auth && state.auth.token ? { Authorization: 'Bearer ' + state.auth.token } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  })
  const data = await r.json().catch(() => ({}))
  if (r.status === 401 && state.auth) { saveAuth(null) }
  return data
}
export async function getJSON(url) { const r = await fetch(url); return r.json() }

export async function loadServerPrefs() {
  if (!state.auth || !state.auth.token) return
  try {
    const r = await apiAuth('prefs')
    if (r.ok && r.prefs) {
      // 服务端偏好 + 本地偏好合并（bgPos 等服务端不存的字段保留本地值）
      const merged = Object.assign({}, loadPrefs(), r.prefs)
      localStorage.setItem(prefsKey(), JSON.stringify(merged))
      applyPrefs()
    }
  } catch (e) {}
}

export function openLogin() { state.loginOpen = true; state.loginPop = false }
export function closeLogin() { state.loginOpen = false }
export function goHome() { state.view = 'home'; state.q = ''; state.champId = ''; state.cat = '' }
export function openAvatarMenu() { state.avatarMenuOpen = true }
export function closeAvatarMenu() { state.avatarMenuOpen = false }
export function toggleTheme() {
  const p = loadPrefs(); p.theme = p.theme === 'dark' ? 'light' : 'dark'; savePrefs(p); applyPrefs()
}

export async function logout() {
  await apiAuth('logout', {})
  saveAuth(null)
  try { localStorage.removeItem('dsh_prefs_guest') } catch (e) {}
  document.documentElement.classList.remove('dark')
  document.body.style.background = ''
  delete window.__petLock
  state.avatarMenuOpen = false
  state.view = 'home'
}

// —— 个人中心背景/主题 ——
export function setBg(css) { const p = loadPrefs(); p.bg = css; p.bgImg = ''; savePrefs(p); applyPrefs() }
export function setBgImg(dataUrl, pos) { const p = loadPrefs(); p.bgImg = dataUrl; p.bgPos = pos || 'center'; p.bg = ''; savePrefs(p); applyPrefs() }
export function clearBg() { const p = loadPrefs(); p.bgImg = ''; p.bg = ''; savePrefs(p); applyPrefs() }
export function saveTheme(t) { const p = loadPrefs(); p.theme = t; savePrefs(p); applyPrefs() }

// —— 管理后台 ——
export async function adminApi(path, body, method) {
  const r = await fetch('/api/admin/' + path, {
    method: method || (body ? 'POST' : 'GET'),
    headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + (state.auth && state.auth.token) },
    body: body ? JSON.stringify(body) : undefined,
  })
  return r.json()
}

// —— 通用带登录态的 /api/ 请求（收信箱等非 auth/admin 前缀接口）——
export async function apiRoot(path, body, method) {
  const r = await fetch('/api/' + path, {
    method: method || (body ? 'POST' : 'GET'),
    headers: { 'Content-Type': 'application/json', ...(state.auth && state.auth.token ? { Authorization: 'Bearer ' + state.auth.token } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  })
  const data = await r.json().catch(() => ({}))
  if (r.status === 401 && state.auth) { saveAuth(null) }
  return data
}

export { updateAuthUser }

// 轻量 toast
let toastEl
export function toast(msg) {
  if (!toastEl) { toastEl = document.createElement('div'); toastEl.className = 'toast'; document.body.appendChild(toastEl) }
  toastEl.textContent = msg
  toastEl.classList.add('show')
  clearTimeout(toastEl._t)
  toastEl._t = setTimeout(() => toastEl.classList.remove('show'), 1800)
}
