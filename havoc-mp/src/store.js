import { reactive } from 'vue'
import { apiAuth } from './api'

// 全局状态（对应 web/src/store.js，去掉 document/window/localStorage 依赖）
export const state = reactive({
  auth: null,          // { token, user } 或 null
  q: '',               // 全局搜索关键字（首页搜索框）
  cat: '刺客',          // 分类页当前分类
  champId: '',         // 详情页当前英雄 id
  section: { cid: '', key: '' },  // "更多"板块页参数
  augDesc: null,       // 符文说明弹窗 { name, quality, icon, desc }
})

const AUTH_KEY = 'dsh_auth'

export function loadAuth() {
  try { state.auth = uni.getStorageSync(AUTH_KEY) || null } catch (e) { state.auth = null }
}
export function saveAuth(a) {
  state.auth = a
  try { if (a) uni.setStorageSync(AUTH_KEY, a); else uni.removeStorageSync(AUTH_KEY) } catch (e) {}
}
export function updateAuthUser(user) {
  if (state.auth) { state.auth.user = user; saveAuth(state.auth) }
}

// 轻提示 / 弹窗（对应网页版 toast/alert/confirm）
export function toast(msg) { uni.showToast({ title: String(msg || ''), icon: 'none' }) }
export function alertMsg(msg) { uni.showModal({ title: '提示', content: String(msg || ''), showCancel: false }) }
export function confirmMsg(msg) {
  return new Promise(resolve => {
    uni.showModal({
      title: '提示',
      content: String(msg || ''),
      success: r => resolve(!!r.confirm),
      fail: () => resolve(false),
    })
  })
}

// 符文说明弹窗
export function openAugDesc(a) { state.augDesc = a }
export function closeAugDesc() { state.augDesc = null }

export async function logout() {
  try { await apiAuth('logout', {}) } catch (e) {}
  saveAuth(null)
}

// 头像兜底占位图（小程序 image 不支持 svg data-uri，用本地 png）
export const AV_FALLBACK = '/static/avatar_fallback.png'

// 处理 401：登录态失效自动清除
export function handle401(status) {
  if (status === 401 && state.auth) saveAuth(null)
  return status
}
