<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  state, loadPrefs, savePrefs, applyPrefs, apiAuth, apiRoot, logout, goHome, toast,
  PET_IMGS, BG_PRESETS, DARK_PRESETS, setBg, setBgImg, clearBg, saveTheme, updateAuthUser,
} from '../store'

const u = computed(() => state.auth && state.auth.user)
const prefs = ref(loadPrefs())
const dk = computed(() => prefs.value.theme === 'dark')
const bgs = computed(() => (dk.value ? DARK_PRESETS : BG_PRESETS))
function refreshPrefs() { prefs.value = loadPrefs() }

const avatar = computed(() => (u.value && u.value.avatar) ? u.value.avatar : '/static/preset_avatar.png')
const contact = computed(() => u.value ? (u.value.contact + (u.value.phone ? '　·　手机 ' + u.value.phone : '')) : '')

// 账号表单
const form = ref('')                       // '' | 'avatar' | 'pwd' | 'name' | 'phone'
const pwdN = ref(''); const pwdN2 = ref('')
const nameV = ref('')
const phoneV = ref('')
const avatarPreview = ref('')
const emailV = ref('')
const codeV = ref('')
const codeSending = ref(false)

// 背景
const bgImg = ref('')

// 桌宠锁定
const petSel = ref(((prefs.value && prefs.value.pets) || []).slice())
// 主题
const themeSel = ref((prefs.value && prefs.value.theme) || 'light')
// AI 助手自定义人设（存服务器，聊天时后端读取）
const aiPrompt = ref('')
async function loadAiPrompt() {
  const r = await apiAuth('prefs', {})
  if (r.ok && r.prefs) aiPrompt.value = r.prefs.aiPrompt || ''
}
async function saveAiPrompt() {
  const r = await apiAuth('prefs', { aiPrompt: aiPrompt.value })
  if (r.ok) { toast('AI 人设已保存，去聊天试试吧') } else { alert(r.error || '保存失败') }
}
async function resetAiPrompt() {
  aiPrompt.value = ''
  await saveAiPrompt()
}

// 收信箱（官方公告弹窗：左侧版本列表，右侧版本内容；未读角标，选中即读）
const anns = ref([])
const unread = ref(0)
const inboxOpen = ref(false)
const annSel = ref(null)
const annCur = computed(() => anns.value.find(a => a.id === annSel.value) || null)
async function loadAnns() {
  const r = await apiRoot('announcements')
  if (r.ok) { anns.value = r.announcements || []; unread.value = r.unread || 0 }
}
function openInbox() {
  inboxOpen.value = true
  const firstUnread = anns.value.find(a => !a.read)
  annSel.value = (firstUnread || anns.value[0] || {}).id || null
}
function closeInbox() { inboxOpen.value = false }
async function selectAnn(a) {
  annSel.value = a.id
  if (!a.read) {
    const r = await apiRoot('announcements/' + a.id + '/read', {}, 'POST')
    if (r.ok) { a.read = true; unread.value = (r.unread != null ? r.unread : Math.max(0, unread.value - 1)) }
  }
}

function back() { goHome() }

function pickAvatar(e) {
  const f = e.target.files[0]; if (!f) return
  const rd = new FileReader()
  rd.onload = () => { avatarPreview.value = rd.result; form.value = 'avatar' }
  rd.readAsDataURL(f)
  e.target.value = ''
}
async function uploadAvatar() {
  if (!avatarPreview.value) return
  const r = await apiAuth('avatar', { avatar: avatarPreview.value })
  if (r.ok) { updateAuthUser({ ...u.value, avatar: r.avatar }); avatarPreview.value = ''; form.value = ''; toast('头像已更新') }
  else { alert(r.error || '上传失败') }
}

async function savePwd() {
  const a = pwdN.value, b = pwdN2.value
  if (a.length < 4) { alert('密码至少4位'); return }
  if (a !== b) { alert('两次密码不一致'); return }
  const r = await apiAuth('password', { password: a })
  if (r.ok) { form.value = ''; toast('密码已修改') } else { alert(r.error || '修改失败') }
}
async function saveName() {
  const n = nameV.value.trim()
  if (!n) { alert('请输入用户名'); return }
  const r = await apiAuth('name', { name: n })
  if (r.ok) { updateAuthUser({ ...u.value, name: r.name }); form.value = ''; toast('用户名已更新') } else { alert(r.error || '修改失败') }
}
async function savePhone() {
  const p = phoneV.value.trim()
  if (!/^1[3-9]\d{9}$/.test(p)) { alert('请输入正确的手机号（1开头11位）'); return }
  const r = await apiAuth('phone', { phone: p })
  if (r.ok) { updateAuthUser({ ...u.value, phone: r.phone }); form.value = ''; toast('手机号已绑定') } else { alert(r.error || '绑定失败') }
}
async function unbindPhone() {
  if (!confirm('确定解绑当前手机号？')) return
  const r = await apiAuth('phone', { phone: '' })
  if (r.ok) { updateAuthUser({ ...u.value, phone: '' }); form.value = ''; toast('已解绑手机号') } else { alert(r.error || '解绑失败') }
}

async function sendEmailCode() {
  const em = emailV.value.trim()
  if (!em || !em.includes('@')) { alert('请输入正确的邮箱地址'); return }
  const r = await apiAuth('email_code', { email: em })
  if (r.ok) { codeSending.value = true; toast('验证码已发送，请查收邮箱') }
  else { alert(r.error || '发送失败'); codeSending.value = false }
}
async function saveEmail() {
  const em = emailV.value.trim()
  if (!em || !em.includes('@')) { alert('请输入正确的邮箱地址'); return }
  if (!codeV.value.trim()) { alert('请输入验证码'); return }
  const r = await apiAuth('email', { email: em, code: codeV.value.trim() })
  if (r.ok) {
    updateAuthUser({ ...u.value, contact: r.contact })
    form.value = ''; emailV.value = ''; codeV.value = ''; codeSending.value = false
    toast('邮箱已更换，下次可用新邮箱登录')
  } else { alert(r.error || '更换失败') }
}

function pickBg(css) { setBg(css); refreshPrefs() }
function resetBg() { clearBg(); refreshPrefs() }

// —— 自定义背景：上传 → 预览框拖动选择显示区域 → 确认 ——
const bgPreview = ref('')      // 预览图片(dataUrl)
const bgPos = ref('center')    // 显示区域(百分比)
function onBgImg(e) {
  const f = e.target.files[0]; if (!f) return
  const rd = new FileReader()
  rd.onload = () => { bgPreview.value = rd.result; bgPos.value = 'center' }
  rd.readAsDataURL(f)
  e.target.value = ''
}
let dragging = false, dragStart = null, dragStartPos = null
function parsePos(p) { const m = /([\d.]+)%\s+([\d.]+)%/.exec(p); return m ? [parseFloat(m[1]), parseFloat(m[2])] : [50, 50] }
function dragTo(clientX, clientY, el) {
  const rect = el.getBoundingClientRect()
  const dx = (clientX - dragStart.x) / rect.width * 100
  const dy = (clientY - dragStart.y) / rect.height * 100
  const [sx, sy] = parsePos(dragStartPos)
  const cx = Math.max(0, Math.min(100, Math.round(sx + dx)))
  const cy = Math.max(0, Math.min(100, Math.round(sy + dy)))
  bgPos.value = cx + '% ' + cy + '%'
}
function startDrag(e) { dragging = true; dragStart = { x: e.clientX, y: e.clientY }; dragStartPos = bgPos.value }
function onDrag(e) { if (!dragging) return; dragTo(e.clientX, e.clientY, e.currentTarget) }
function startTouchDrag(e) { const t = e.touches[0]; if (!t) return; dragging = true; dragStart = { x: t.clientX, y: t.clientY }; dragStartPos = bgPos.value }
function onTouchDrag(e) { if (!dragging) return; const t = e.touches[0]; if (t) dragTo(t.clientX, t.clientY, e.currentTarget) }
function endDrag() { dragging = false }
function confirmBg() { setBgImg(bgPreview.value, bgPos.value); bgPreview.value = ''; refreshPrefs(); toast('背景已设置') }

function togglePet(file) { petSel.value = petSel.value.includes(file) ? petSel.value.filter(x => x !== file) : petSel.value.concat([file]) }
function confirmPets() { const p = loadPrefs(); p.pets = petSel.value.slice(); savePrefs(p); applyPrefs(); refreshPrefs(); toast('已锁定 Q 版形象') }

function pickTheme(t) { themeSel.value = t }
function confirmTheme() { saveTheme(themeSel.value); refreshPrefs(); toast('主题已切换') }

async function onLogout() { await logout() }

onMounted(() => { loadAiPrompt(); loadAnns() })
</script>

<template>
  <div class="detail">
    <div class="pc-head">
      <button class="btn" @click="back">返回</button>
      <h2>个人中心</h2>
      <span class="pc-hello">{{ u ? u.name : '' }}（{{ u && u.is_admin ? '管理员' : '普通用户' }}）</span>
    </div>

    <!-- 我的账号 -->
    <div class="pc-sec">
      <h3>我的账号</h3>
      <div class="pc-acc">
        <img class="pc-av" :src="avatar" title="点击更换头像" @click="document.getElementById('pcFile').click()">
        <div class="pc-accinfo">
          <div class="pc-accname">{{ u ? u.name : '' }}</div>
          <div class="pc-accsub">{{ contact }}</div>
        </div>
        <button class="pc-mail" :class="{ on: inboxOpen }" title="收信箱" @click="openInbox">
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2.5" y="5.5" width="19" height="13" rx="2.5"></rect>
            <path d="M3.5 7.5l8.5 6 8.5-6"></path>
          </svg>
          <span v-if="unread > 0" class="pc-badge mail-badge">{{ unread > 99 ? '99+' : unread }}</span>
        </button>
        <div class="pc-accbtns">
          <button class="pc-btn" @click="document.getElementById('pcFile').click()">更换头像</button>
          <button class="pc-btn" @click="form = form === 'pwd' ? '' : 'pwd'; pwdN=''; pwdN2=''">更改密码</button>
          <button class="pc-btn" @click="form = form === 'phone' ? '' : 'phone'; phoneV = u.phone || ''">{{ u && u.phone ? '修改手机号' : '绑定手机号' }}</button>
          <button class="pc-btn" @click="form = form === 'name' ? '' : 'name'; nameV=u.name">更改用户名</button>
          <button class="pc-btn" @click="form = form === 'email' ? '' : 'email'; emailV=''; codeV=''; codeSending=false">更换邮箱</button>
          <button v-if="u && u.is_admin" class="pc-btn ok" @click="state.view = 'admin'">管理后台</button>
          <button class="pc-btn danger" @click="onLogout">退出登录</button>
        </div>
        <input id="pcFile" type="file" accept="image/*" hidden @change="pickAvatar">
      </div>

      <div v-if="form === 'pwd'" class="pc-formwrap">
        <div class="pc-form">
          <div class="pc-form-t">修改密码</div>
          <input v-model="pwdN" class="pc-form-in" type="password" placeholder="新密码（至少4位）">
          <input v-model="pwdN2" class="pc-form-in" type="password" placeholder="确认新密码">
          <div class="pc-form-btns"><button class="pc-btn ok" @click="savePwd">保存</button><button class="pc-btn" @click="form=''">取消</button></div>
        </div>
      </div>
      <div v-if="form === 'name'" class="pc-formwrap">
        <div class="pc-form">
          <div class="pc-form-t">修改用户名</div>
          <input v-model="nameV" class="pc-form-in" placeholder="新的用户名">
          <div class="pc-form-btns"><button class="pc-btn ok" @click="saveName">保存</button><button class="pc-btn" @click="form=''">取消</button></div>
        </div>
      </div>
      <div v-if="form === 'phone'" class="pc-formwrap">
        <div class="pc-form">
          <div class="pc-form-t">{{ u && u.phone ? '修改手机号' : '绑定手机号' }}</div>
          <div class="pc-form-tip">绑定后可用该手机号登录（一个手机号只能绑定一个账号）</div>
          <input v-model="phoneV" class="pc-form-in" placeholder="输入11位手机号">
          <div class="pc-form-btns">
            <button class="pc-btn ok" @click="savePhone">{{ u && u.phone ? '保存修改' : '确认绑定' }}</button>
            <button v-if="u && u.phone" class="pc-btn danger" @click="unbindPhone">解绑</button>
            <button class="pc-btn" @click="form=''">取消</button>
          </div>
        </div>
      </div>
      <div v-if="form === 'email'" class="pc-formwrap">
        <div class="pc-form">
          <div class="pc-form-t">更换邮箱</div>
          <div class="pc-form-tip">将向新邮箱发送验证码，验证通过后新邮箱即成为登录邮箱</div>
          <input v-model="emailV" class="pc-form-in" placeholder="输入新邮箱地址">
          <div class="pc-crow">
            <input v-model="codeV" class="pc-form-in" placeholder="邮箱验证码">
            <button class="pc-btn" :disabled="codeSending" @click="sendEmailCode">{{ codeSending ? '已发送' : '获取验证码' }}</button>
          </div>
          <div class="pc-form-btns">
            <button class="pc-btn ok" @click="saveEmail">保存</button>
            <button class="pc-btn" @click="form=''">取消</button>
          </div>
        </div>
      </div>
      <div v-if="form === 'avatar'" class="pc-formwrap">
        <div class="pc-form">
          <div class="pc-form-t">预览头像</div>
          <img class="pc-prev" :src="avatarPreview">
          <div class="pc-form-btns"><button class="pc-btn ok" @click="uploadAvatar">确认上传</button><button class="pc-btn" @click="form=''">取消</button></div>
        </div>
      </div>
    </div>

    <!-- 自定义背景 -->
    <div class="pc-sec">
      <h3>自定义网页背景</h3>
      <div class="pc-bgs">
        <div v-for="b in bgs" :key="b.name" class="pc-bg" :class="{ on: (prefs.bg || '') === b.css, darkpre: dk }"
             :style="{ background: b.css || (dk ? '#0a0e18' : 'var(--panel2)') }" @click="pickBg(b.css)">
          <span>{{ b.name }}</span>
        </div>
      </div>
      <div class="pc-okrow">
        <label class="pc-btn" for="pcBgImg">上传图片背景</label>
        <input id="pcBgImg" type="file" accept="image/*" hidden @change="onBgImg">
        <button class="pc-btn" @click="resetBg">恢复默认</button>
      </div>
    </div>

    <!-- 自定义背景预览弹窗（站点风格）：拖动图片选择显示区域；手机=竖框，电脑=横框 -->
    <div v-if="bgPreview" class="bgmodal-ov" @click.self="bgPreview=''">
      <div class="bgmodal">
        <button class="bgmodal-x" @click="bgPreview=''">✕</button>
        <div class="bgmodal-t">自定义背景预览 <span class="bgmodal-sub">拖动图片，选择要显示的区域</span></div>
        <div class="bgpreview"
             :style="{ backgroundImage: 'url(' + bgPreview + ')', backgroundPosition: bgPos }"
             @mousedown="startDrag" @mousemove="onDrag" @mouseup="endDrag" @mouseleave="endDrag"
             @touchstart.prevent="startTouchDrag" @touchmove.prevent="onTouchDrag" @touchend="endDrag">
        </div>
        <div class="pc-okrow bgmodal-btns">
          <button class="pc-btn ok" @click="confirmBg">确认使用此背景</button>
          <button class="pc-btn" @click="bgPreview=''">取消</button>
        </div>
      </div>
    </div>

    <!-- 锁定 Q 版 -->
    <div class="pc-sec">
      <h3>锁定 Q 版人物形象</h3>
      <div class="pc-pets">
        <div v-for="p in PET_IMGS" :key="p[0]" class="pc-pet" :class="{ on: petSel.includes(p[0]) }" @click="togglePet(p[0])">
          <img :src="'/static/' + p[0]" :alt="p[1]"><span>{{ p[1] }}</span>
        </div>
      </div>
      <div class="pc-okrow pc-okcol">
        <button class="pc-btn ok" @click="confirmPets">确定</button>
        <span class="pc-okhint">点击选中/取消 · 可多选，确定后锁定</span>
      </div>
    </div>

    <!-- 主题 -->
    <div class="pc-sec">
      <h3>改变网站风格</h3>
      <div class="pc-themes">
        <button class="pc-theme" :class="{ on: themeSel !== 'dark' }" @click="pickTheme('light')">浅色</button>
        <button class="pc-theme" :class="{ on: themeSel === 'dark' }" @click="pickTheme('dark')">深色</button>
      </div>
      <div class="pc-okrow"><button class="pc-btn ok" @click="confirmTheme">确定</button></div>
    </div>

    <!-- 编辑 AI 助手（自定义聊天人设） -->
    <div class="pc-sec">
      <h3>编辑 AI 助手</h3>
      <div class="pc-form-tip">写下你希望「小海克斯」成为的样子——性格、口吻、对你的称呼、爱聊的话题……保存后立即生效，收获属于你的专属陪伴。</div>
      <textarea v-model="aiPrompt" class="ai-prompt-in" rows="5" maxlength="1000"
                placeholder="例如：你是一个温柔贴心的姐姐，叫我“宝贝”，说话轻声细语，喜欢听我分享日常，也会认真给我游戏建议，用「～」结尾……"></textarea>
      <div class="pc-okrow">
        <button class="pc-btn ok" @click="saveAiPrompt">保存人设</button>
        <button class="pc-btn" @click="resetAiPrompt">恢复默认</button>
        <span class="pc-okhint">{{ aiPrompt.length }}/1000</span>
      </div>
    </div>

    <!-- 收信箱弹窗：左侧版本列表 + 右侧版本内容 -->
    <div v-if="inboxOpen" class="ann-ov" @click.self="closeInbox">
      <div class="ann-card ann-win">
        <div class="ann-pop-head">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="5.5" width="19" height="13" rx="2.5"/><path d="M3.5 7.5l8.5 6 8.5-6"/></svg>
          <span>收信箱</span>
          <button class="ann-x" @click="closeInbox">✕</button>
        </div>
        <div class="ann-win-body">
          <div class="ann-sides">
            <div v-if="!anns.length" class="empty">暂无消息</div>
            <div v-for="a in anns" :key="a.id" class="ann-side-item" :class="{ on: annSel === a.id }" @click="selectAnn(a)">
              <span v-if="!a.read" class="inbox-dot"></span>
              <span class="ann-side-ver">{{ a.ver || '公告' }}</span>
              <span class="ann-side-title">{{ a.title }}</span>
            </div>
          </div>
          <div class="ann-main">
            <template v-if="annCur">
              <div class="ann-pop-title">{{ annCur.ver ? annCur.ver + ' · ' : '' }}{{ annCur.title }}</div>
              <div class="ann-pop-body">{{ annCur.content }}</div>
            </template>
            <div v-else class="empty">选择左侧版本查看内容</div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
