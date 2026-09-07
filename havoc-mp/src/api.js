// API 封装：uni.request 包装，指向线上后端 https://haikelol.com
// 注意：小程序无浏览器同源限制，无需 CORS；域名需在小程序后台配 request 合法域名。

export const BASE = 'https://haikelol.com'
const AUTH_KEY = 'dsh_auth'

function req(url, opts = {}) {
  let token = ''
  try { token = (uni.getStorageSync(AUTH_KEY) || {}).token || '' } catch (e) {}
  return new Promise((resolve, reject) => {
    uni.request({
      url: /^https?:\/\//.test(url) ? url : BASE + url,
      method: opts.method || 'GET',
      data: opts.data,
      header: Object.assign(
        { 'Content-Type': 'application/json' },
        token ? { Authorization: 'Bearer ' + token } : {},
        opts.header || {}
      ),
      success: r => resolve({ status: r.statusCode, data: r.data }),
      fail: e => reject(e),
    })
  })
}

export function getJSON(url) { return req(url).then(r => r.data) }
export function postJSON(url, data) { return req(url, { method: 'POST', data }) }
export function apiAuth(path, data) { return req('/api/auth/' + path, { method: 'POST', data }) }
export function adminApi(path, data) { return req('/api/admin/' + path, { method: data ? 'POST' : 'GET', data }) }

// —— 符文名 → 描述 缓存（点符文卡弹窗显示效果说明）——
let descMap = null
export async function ensureAugDesc() {
  if (descMap) return descMap
  try {
    descMap = {}
    const g = await getJSON('/api/augments_all')
    ;(g || []).forEach(gr => (gr.items || []).forEach(a => { if (a.name) descMap[a.name] = a.desc || '' }))
  } catch (e) { descMap = {} }
  return descMap
}
export function getAugDesc(name) { return (descMap || {})[name] || '' }

// 头像上传：本地文件路径 → base64 dataURL（与网页版一致的接口格式）
export function fileToDataURL(filePath) {
  return new Promise((resolve, reject) => {
    uni.getFileSystemManager().readFile({
      filePath,
      encoding: 'base64',
      success: res => resolve('data:image/png;base64,' + res.data),
      fail: reject,
    })
  })
}
