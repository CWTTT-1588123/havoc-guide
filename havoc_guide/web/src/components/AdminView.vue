<script setup>
import { ref, computed, onMounted } from 'vue'
import { state, adminApi, goHome, toast } from '../store'

const users = ref([])
const comments = ref([])
const stats = ref(null)
const anns = ref([])
const annTitle = ref('')
const annContent = ref('')
const annVer = ref('')
const tab = ref('users')   // 'users' | 'stats' | 'comments' | 'anns'
const me = computed(() => state.auth && state.auth.user)
const meOwner = computed(() => !!(me.value && me.value.owner))

async function load() {
  const d = await adminApi('users')
  if (d.ok) { users.value = d.users } else { alert(d.error || '加载失败') }
  const c = await adminApi('comments')
  if (c.ok) { comments.value = c.comments } else { alert(c.error || '评论加载失败') }
  const s = await adminApi('stats')
  if (s.ok) { stats.value = s } else { alert(s.error || '统计加载失败') }
  const a = await adminApi('announcements')
  if (a.ok) { anns.value = a.announcements } else { alert(a.error || '公告加载失败') }
}

function back() { goHome() }

function fmtTs(ts) { return new Date((ts || 0) * 1000).toLocaleString() }

function roleBadge(u) {
  if (u.owner) return '<span class="q 黄金">主管理员</span>'
  if (u.is_admin) return '<span class="q 黄金">管理员</span>'
  return '<span class="q 白银">普通</span>'
}

async function setRole(u, val) {
  const r = await adminApi('user/' + u.id, { is_admin: val ? 1 : 0 })
  if (r.ok) { toast(val ? '已设为管理员' : '已降为普通'); load() } else { alert(r.error || '操作失败') }
}
// 重置密码：手机浏览器不支持 window.prompt 弹输入框 → 改用站内弹窗
const pwdU = ref(null)
const pwdVal = ref('')
function resetPwd(u) { pwdU.value = u; pwdVal.value = '' }
async function confirmPwd() {
  const p = pwdVal.value
  if (p.length < 6) { alert('密码至少6位'); return }
  const r = await adminApi('user/' + pwdU.value.id, { password: p })
  if (r.ok) { toast('密码已重置'); pwdU.value = null; pwdVal.value = ''; load() }
  else { alert(r.error || '重置失败') }
}
async function del(u) {
  if (!confirm('确定删除用户 ' + (u.name || u.contact) + '？')) return
  const r = await adminApi('delete/' + u.id, {}, 'POST')
  if (r.ok) { toast('已删除'); load() } else { alert(r.error || '删除失败') }
}

async function delComment(c) {
  if (!confirm('确定删除该评论？\n\n' + c.name + '：' + c.text.slice(0, 50))) return
  const r = await adminApi('comment/' + c.id + '/delete', {}, 'POST')
  if (r.ok) { toast('评论已删除'); load() } else { alert(r.error || '删除失败') }
}

// —— 公告管理（发布后全站用户收信箱可见）——
async function publishAnn() {
  const title = annTitle.value.trim(), content = annContent.value.trim()
  if (!title || !content) { alert('标题和内容都不能为空'); return }
  const r = await adminApi('announcement', { title, content, ver: annVer.value.trim() }, 'POST')
  if (r.ok) { toast('公告已发布，全站用户收信箱可见'); annTitle.value = ''; annContent.value = ''; annVer.value = ''; load() }
  else { alert(r.error || '发布失败') }
}
async function delAnn(a) {
  if (!confirm('确定删除公告「' + a.title + '」？')) return
  const r = await adminApi('announcement/' + a.id + '/delete', {}, 'POST')
  if (r.ok) { toast('公告已删除'); load() } else { alert(r.error || '删除失败') }
}

function actionsFor(u) {
  const self = u.contact === me.value.contact
  if (self) return '<span style="color:var(--sub);font-size:20px;">当前账号</span>'
  let b = ''
  if (meOwner.value) {
    b += u.is_admin ? `<button class="pc-btn" onclick="__do('set0','${u.id}')">降为普通</button>` : `<button class="pc-btn" onclick="__do('set1','${u.id}')">设为管理员</button>`
    b += ` <button class="pc-btn" onclick="__do('pwd','${u.id}')">重置密码</button>`
    b += ` <button class="pc-btn danger" onclick="__do('del','${u.id}')">删除</button>`
  } else {
    b += u.is_admin ? '<span style="color:var(--sub);font-size:20px;">仅主管理员可操作</span>'
                     : `<button class="pc-btn" onclick="__do('pwd','${u.id}')">重置密码</button> <button class="pc-btn danger" onclick="__do('del','${u.id}')">删除</button>`
  }
  return b
}
// 由模板 v-html 回调（因为 v-html 里的 onclick 需全局函数）
window.__do = (kind, id) => {
  const u = users.value.find(x => x.id === id); if (!u) return
  if (kind === 'set0') setRole(u, 0)
  else if (kind === 'set1') setRole(u, 1)
  else if (kind === 'pwd') resetPwd(u)
  else if (kind === 'del') del(u)
}

onMounted(load)
</script>

<template>
  <div class="toolbar">
    <button class="btn" @click="back">返回</button>
  </div>
  <div class="adm-tabs">
    <button class="btn" :class="{ active: tab === 'users' }" @click="tab = 'users'">用户管理</button>
    <button class="btn" :class="{ active: tab === 'stats' }" @click="tab = 'stats'">访问统计</button>
    <button class="btn" :class="{ active: tab === 'comments' }" @click="tab = 'comments'">评论管理</button>
    <button class="btn" :class="{ active: tab === 'anns' }" @click="tab = 'anns'">公告管理</button>
  </div>

  <div v-if="tab === 'users'" class="detail">
    <h3 class="sechead"><span>用户管理</span></h3>
    <table id="tbl">
      <thead><tr><th>用户</th><th>账号</th><th>角色</th><th>注册时间</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td><div class="champline"><img v-if="u.avatar" class="avatar" :src="u.avatar"><span>{{ u.name || '—' }}</span></div></td>
          <td>{{ u.contact }}</td>
          <td v-html="roleBadge(u)"></td>
          <td>{{ new Date((u.created || 0) * 1000).toLocaleDateString() }}</td>
          <td v-html="actionsFor(u)"></td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="tab === 'stats'" class="detail">
    <h3 class="sechead"><span>访问统计</span></h3>
    <div v-if="stats" class="pv-box">
      <div class="pv-big">
        <div class="pv-card"><b>{{ stats.total }}</b><span>总浏览量</span></div>
        <div class="pv-card"><b>{{ stats.today }}</b><span>今日浏览</span></div>
        <div class="pv-card"><b>{{ stats.desktop }}</b><span>桌面浏览（今日 {{ stats.today_desktop }}）</span></div>
        <div class="pv-card"><b>{{ stats.mobile }}</b><span>手机浏览（今日 {{ stats.today_mobile }}）</span></div>
      </div>
      <div class="pv-cols">
        <div>
          <h4>近 14 天</h4>
          <table id="tbl"><thead><tr><th>日期</th><th>浏览</th></tr></thead>
            <tbody><tr v-for="d in stats.days" :key="d.day"><td>{{ d.day }}</td><td>{{ d.count }}</td></tr></tbody>
          </table>
        </div>
        <div>
          <h4>页面分布</h4>
          <table id="tbl"><thead><tr><th>页面</th><th>浏览</th></tr></thead>
            <tbody><tr v-for="v in stats.by_view" :key="v.view"><td>{{ v.view }}</td><td>{{ v.count }}</td></tr></tbody>
          </table>
        </div>
      </div>
      <p class="muted pv-note">* 管理员已登录的设备浏览自动排除；未登录设备（如未登录的手机）仍会正常计入——手机看站时登录一下管理员账号即可不计入。</p>
    </div>
    <div v-else class="empty">统计加载中…</div>
  </div>

  <div v-if="tab === 'comments'" class="detail">
    <h3 class="sechead"><span>评论管理</span></h3>
    <div v-if="!comments.length" class="empty">暂无评论</div>
    <table v-else id="tbl">
      <thead><tr><th>时间</th><th>英雄</th><th>用户</th><th>内容</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="c in comments" :key="c.id">
          <td>{{ fmtTs(c.ts) }}</td>
          <td>{{ c.champ_name }}</td>
          <td>{{ c.name }}<span class="muted" v-if="c.contact">（{{ c.contact }}）</span></td>
          <td class="com-cell">{{ c.text }}</td>
          <td><button class="pc-btn danger" @click="delComment(c)">删除</button></td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="tab === 'anns'" class="detail">
    <h3 class="sechead"><span>公告管理</span></h3>
    <div class="ann-form">
      <div class="pc-form-tip">发布新公告后，全站所有登录用户的收信箱都会收到并显示未读角标。版本号会显示在用户收信箱左侧列表中，留空则自动使用当前站点版本。</div>
      <div class="ann-verrow">
        <input v-model="annVer" class="pc-form-in ann-ver-in" maxlength="20" placeholder="版本号（如 v1.4.0，留空=当前版本）">
        <input v-model="annTitle" class="pc-form-in" maxlength="60" placeholder="公告标题（60字内）">
      </div>
      <textarea v-model="annContent" class="pc-form-in ann-text" rows="6" maxlength="2000" placeholder="公告内容（2000字内），支持换行"></textarea>
      <div class="pc-form-btns"><button class="pc-btn ok" @click="publishAnn">发布公告</button></div>
    </div>
    <div v-if="!anns.length" class="empty">暂无公告</div>
    <div v-else class="ann-list">
      <div v-for="a in anns" :key="a.id" class="ann-item">
        <div class="ann-item-main">
          <span class="ann-t">{{ a.title }}</span>
          <span class="muted ann-time">{{ fmtTs(a.created) }}</span>
        </div>
        <button class="pc-btn danger" @click="delAnn(a)">删除</button>
      </div>
    </div>
  </div>

  <!-- 重置密码弹窗（替代 prompt，手机可用） -->
  <div v-if="pwdU" class="ann-ov" @click.self="pwdU = null">
    <div class="ann-card pwd-card">
      <div class="ann-pop-head">
        <span>重置密码</span>
        <button class="ann-x" @click="pwdU = null">✕</button>
      </div>
      <div class="pc-form-tip pwd-tip">为 <b>{{ pwdU.name || pwdU.contact }}</b> 设置新密码（至少6位）</div>
      <input v-model="pwdVal" class="pc-form-in" type="password" placeholder="输入新密码（至少6位）">
      <div class="ann-pop-btns">
        <button class="pc-btn ok" @click="confirmPwd">确定重置</button>
        <button class="pc-btn" @click="pwdU = null">取消</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.adm-tabs { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:16px; }
.com-cell { max-width:420px; white-space:pre-wrap; word-break:break-word; font-size:20px; }
.pv-box { margin-bottom:8px; }
.pv-big { display:flex; gap:14px; margin-bottom:16px; flex-wrap:wrap; }
.pv-card { background:var(--panel2); border:1px solid var(--line); border-radius:14px; padding:16px 28px; display:flex; flex-direction:column; align-items:center; gap:4px; }
.pv-card b { font-size:34px; color:var(--gold); }
.pv-card span { font-size:19px; color:var(--sub); }
.pv-cols { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
@media (max-width:768px){ .pv-cols { grid-template-columns:1fr; } }
.pv-cols h4 { margin:0 0 8px; font-size:22px; color:var(--txt); }
.pv-note { font-size:16px; margin-top:10px; }
.ann-form { display:flex; flex-direction:column; gap:12px; max-width:760px; margin-bottom:22px; }
.ann-verrow { display:flex; gap:12px; flex-wrap:wrap; }
.ann-ver-in { max-width:300px; }
.ann-text { resize:vertical; line-height:1.6; }
.ann-list { display:flex; flex-direction:column; gap:10px; }
.ann-item { display:flex; align-items:center; gap:14px; background:var(--panel2); border:1px solid var(--line); border-radius:12px; padding:12px 16px; }
.ann-item-main { flex:1; min-width:0; display:flex; flex-direction:column; gap:4px; }
.ann-t { font-size:21px; font-weight:700; color:var(--txt); }
.ann-time { font-size:16px; }
.pwd-card { width:min(94vw, 460px); }
.pwd-tip { margin-bottom:12px; }
.pwd-tip b { color:var(--txt); }
.pwd-card .pc-form-in { width:100%; }
@media (max-width:768px){
  .ann-item { flex-wrap:wrap; }
  .ann-item-main { flex:1 1 100%; }
  /* 手机：公告版本号+标题改为上下堆叠，各占满一行不再溢出 */
  .ann-verrow { flex-direction:column; }
  .ann-ver-in { max-width:100%; width:100%; }
  .ann-verrow .pc-form-in { width:100%; }
}
</style>
