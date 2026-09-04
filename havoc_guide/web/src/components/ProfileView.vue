<script setup>
import { ref, reactive, computed } from 'vue'
import {
  state, loadPrefs, savePrefs, applyPrefs, apiAuth, logout, goHome, toast,
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

// 背景
const bgImg = ref('')

// 桌宠锁定
const petSel = ref((prefs.pets || []).slice())
// 主题
const themeSel = ref(prefs.theme || 'light')

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
function startDrag(e) { dragging = true; dragStart = { x: e.clientX, y: e.clientY }; dragStartPos = bgPos.value }
function onDrag(e) {
  if (!dragging) return
  const rect = e.currentTarget.getBoundingClientRect()
  const dx = (e.clientX - dragStart.x) / rect.width * 100
  const dy = (e.clientY - dragStart.y) / rect.height * 100
  const [sx, sy] = parsePos(dragStartPos)
  const cx = Math.max(0, Math.min(100, Math.round(sx + dx)))
  const cy = Math.max(0, Math.min(100, Math.round(sy + dy)))
  bgPos.value = cx + '% ' + cy + '%'
}
function endDrag() { dragging = false }
function confirmBg() { setBgImg(bgPreview.value, bgPos.value); bgPreview.value = ''; refreshPrefs(); toast('背景已设置') }

function togglePet(file) { petSel.value = petSel.value.includes(file) ? petSel.value.filter(x => x !== file) : petSel.value.concat([file]) }
function confirmPets() { const p = loadPrefs(); p.pets = petSel.value.slice(); savePrefs(p); applyPrefs(); refreshPrefs(); toast('已锁定 Q 版形象') }

function pickTheme(t) { themeSel.value = t }
function confirmTheme() { saveTheme(themeSel.value); refreshPrefs(); toast('主题已切换') }

async function onLogout() { await logout() }
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
        <div class="pc-accbtns">
          <button class="pc-btn" @click="document.getElementById('pcFile').click()">更换头像</button>
          <button class="pc-btn" @click="form = form === 'pwd' ? '' : 'pwd'; pwdN=''; pwdN2=''">更改密码</button>
          <button class="pc-btn" @click="form = form === 'phone' ? '' : 'phone'; phoneV = u.phone || ''">{{ u && u.phone ? '修改手机号' : '绑定手机号' }}</button>
          <button class="pc-btn" @click="form = form === 'name' ? '' : 'name'; nameV=u.name">更改用户名</button>
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

      <!-- 自定义背景预览：拖动图片选择要显示的区域 -->
      <div v-if="bgPreview" class="bgpreview-wrap">
        <div class="bgpreview"
             :style="{ backgroundImage: 'url(' + bgPreview + ')', backgroundPosition: bgPos }"
             @mousedown="startDrag" @mousemove="onDrag" @mouseup="endDrag" @mouseleave="endDrag">
          <span class="bgprev-hint">在框内拖动图片，选择网站要显示的部分（预览）</span>
        </div>
        <div class="pc-okrow">
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
      <div class="pc-okrow">
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

  </div>
</template>
