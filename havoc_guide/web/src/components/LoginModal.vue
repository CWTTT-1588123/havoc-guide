<script setup>
import { ref, reactive } from 'vue'
import { state, closeLogin, saveAuth, apiAuth, toast } from '../store'

const EYE_OPEN = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/></svg>'
const EYE_CLOSED = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M4 20 L20 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
const EMAIL_RE = /^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/

// 当前标签页：'code'=验证码注册 | 'pwd'=密码登录（内部再切换 forgot 忘记密码视图）
const tab = ref('code')
const showForgot = ref(false)

const f = reactive({
  lacct: '', lcode: '', lpwd: '', lpwd2: '',
  lpacct: '', lppwd: '',
  ffacct: '', ffcode: '', ffpwd: '', ffpwd2: '',
})
const showPwd = reactive({ lpwd: false, lpwd2: false, lppwd: false, ffpwd: false, ffpwd2: false })

const codeHint = ref(''); const codeHintColor = ref('var(--red)')
const forgotHint = ref(''); const forgotHintColor = ref('var(--red)')
const getBtn = ref({ disable: false, text: '获取验证码' })
const ffGetBtn = ref({ disable: false, text: '获取验证码' })
const regBtn = ref({ disable: false, text: '注册' })

function typeOf(k) { return showPwd[k] ? 'text' : 'password' }
function toggleEye(k) { showPwd[k] = !showPwd[k] }

function switchTab(t) { tab.value = t; showForgot.value = false; clearInputs() }
function gotoForgot() { showForgot.value = true; clearInputs() }

function clearInputs() {
  Object.keys(f).forEach(k => { f[k] = '' })
  Object.keys(showPwd).forEach(k => { showPwd[k] = false })
  codeHint.value = ''; forgotHint.value = ''
  getBtn.value = { disable: false, text: '获取验证码' }
  ffGetBtn.value = { disable: false, text: '获取验证码' }
  regBtn.value = { disable: false, text: '注册' }
}

async function getCode() {
  const acct = f.lacct.trim()
  if (!acct) { alert('请先输入邮箱'); return }
  if (!EMAIL_RE.test(acct)) { codeHintColor.value = 'var(--red)'; codeHint.value = '邮箱输入错误，请检查格式'; return }
  const r = await apiAuth('send_code', { contact: acct })
  if (r.ok) {
    codeHintColor.value = '#18c66a'
    codeHint.value = '验证码已发送到 ' + acct + '，请查收邮箱'
    setTimeout(() => { codeHint.value = '' }, 1500)
    getBtn.value = { disable: true, text: '已发送' }
    setTimeout(() => { getBtn.value = { disable: false, text: '获取验证码' } }, 10000)
  } else {
    codeHintColor.value = 'var(--red)'; codeHint.value = r.error || '发送失败'
  }
}

async function doLogin() {
  const contact = f.lacct.trim(), code = f.lcode.trim(), pw = f.lpwd, pw2 = f.lpwd2
  if (!contact || !code) { alert('请输入邮箱和验证码'); return }
  if (pw.length < 6) { alert('请至少输入六位密码'); return }
  if (pw !== pw2) { alert('两次密码不一致'); return }
  regBtn.value = { disable: true, text: '注册中…' }
  const body = { contact, code, password: pw }
  let r = await apiAuth('register', body)
  if (r.error === '该邮箱已注册，请直接登录') { r = await apiAuth('login', body) }
  regBtn.value = { disable: false, text: '注册' }
  if (r.ok) { saveAuth({ token: r.token, user: r.user }); closeLogin(); toast('注册成功，欢迎 ' + r.user.name) }
  else { alert(r.error || '操作失败') }
}

async function pwdLogin() {
  const contact = f.lpacct.trim(), pw = f.lppwd
  if (!contact || !pw) { alert('请输入账号和密码'); return }
  const r = await apiAuth('login', { contact, password: pw })
  if (r.ok) { saveAuth({ token: r.token, user: r.user }); closeLogin(); alert('欢迎回来，' + r.user.name) }
  else { alert(r.error || '登录失败') }
}

async function forgotSend() {
  const acct = f.ffacct.trim()
  if (!acct) { alert('请输入注册邮箱'); return }
  if (!EMAIL_RE.test(acct)) { forgotHintColor.value = 'var(--red)'; forgotHint.value = '邮箱输入错误，请检查格式'; return }
  ffGetBtn.value = { disable: true, text: '发送中…' }
  forgotHint.value = ''
  const r = await apiAuth('forgot', { contact: acct })
  ffGetBtn.value = { disable: false, text: '获取验证码' }
  if (r.ok) {
    forgotHintColor.value = '#18c66a'
    forgotHint.value = '重置验证码已发送到 ' + acct + '，请查收邮箱'
    setTimeout(() => { forgotHint.value = '' }, 2000)
  } else {
    forgotHintColor.value = 'var(--red)'; forgotHint.value = r.error || '发送失败'
  }
}

async function doReset() {
  const acct = f.ffacct.trim(), code = f.ffcode.trim(), a = f.ffpwd, b = f.ffpwd2
  if (!acct || !code) { alert('请输入邮箱和验证码'); return }
  if (a.length < 6) { alert('新密码至少6位'); return }
  if (a !== b) { alert('两次密码不一致'); return }
  const r = await apiAuth('reset', { contact: acct, code, password: a })
  if (r.ok) { toast('密码已重置，请用新密码登录'); clearInputs(); switchTab('pwd') }
  else { alert(r.error || '重置失败') }
}
</script>

<template>
  <div class="login-ov">
    <div class="login-card">
      <button class="lclose" @click="closeLogin()">✕</button>

      <div class="ltabs">
        <span class="ltab" :class="{ on: tab === 'code' }" @click="switchTab('code')">验证码注册</span>
        <span class="lsep"></span>
        <span class="ltab" :class="{ on: tab === 'pwd' }" @click="switchTab('pwd')">密码登录</span>
      </div>

      <!-- 验证码注册 -->
      <div v-if="tab === 'code' && !showForgot" class="lbody">
        <div class="lrow"><span class="lprefix">邮箱</span><input v-model="f.lacct" class="lin" placeholder="请输入邮箱"><button class="lget" :class="{ disable: getBtn.disable }" @click="getCode()">{{ getBtn.text }}</button></div>
        <div class="lrow"><span class="lprefix">验证码</span><input v-model="f.lcode" class="lin" placeholder="请输入验证码"><span class="lhint" :style="{ color: codeHintColor }">{{ codeHint }}</span></div>
        <div class="lrow"><span class="lprefix">设置密码</span><input v-model="f.lpwd" class="lin" :type="typeOf('lpwd')" placeholder="请至少输入六位数"><button class="leye" :class="{ on: showPwd.lpwd }" @click="toggleEye('lpwd')" v-html="showPwd.lpwd ? EYE_OPEN : EYE_CLOSED"></button></div>
        <div class="lrow"><span class="lprefix">确认密码</span><input v-model="f.lpwd2" class="lin" :type="typeOf('lpwd2')" placeholder="再次输入密码"><button class="leye" :class="{ on: showPwd.lpwd2 }" @click="toggleEye('lpwd2')" v-html="showPwd.lpwd2 ? EYE_OPEN : EYE_CLOSED"></button></div>
        <button class="lsubmit" :disabled="regBtn.disable" @click="doLogin()">{{ regBtn.text }}</button>
        <div class="ltip">验证码将发送到你邮箱，请查收后填入</div>
      </div>

      <!-- 密码登录 / 忘记密码 -->
      <div v-if="tab === 'pwd'" class="lbody">
        <template v-if="!showForgot">
          <div class="lrow"><span class="lprefix">账号</span><input v-model="f.lpacct" class="lin" placeholder="邮箱或绑定手机号"><span class="lforgot" @click="gotoForgot()">忘记密码?</span></div>
          <div class="lrow"><span class="lprefix">密码</span><input v-model="f.lppwd" class="lin" :type="typeOf('lppwd')" placeholder="请输入密码"><button class="leye" :class="{ on: showPwd.lppwd }" @click="toggleEye('lppwd')" v-html="showPwd.lppwd ? EYE_OPEN : EYE_CLOSED"></button></div>
          <div class="lbtns"><button class="lreg" @click="switchTab('code')">注册</button><button class="llogin" @click="pwdLogin()">登录</button></div>
        </template>

        <template v-else>
          <div class="lrow"><span class="lprefix">账号</span><input v-model="f.ffacct" class="lin" placeholder="请输入注册邮箱"></div>
          <div class="lrow"><span class="lprefix">验证码</span><input v-model="f.ffcode" class="lin" placeholder="请输入验证码"><button class="lget" :class="{ disable: ffGetBtn.disable }" @click="forgotSend()">{{ ffGetBtn.text }}</button></div>
          <div class="lrow"><span class="lhint" :style="{ color: forgotHintColor }">{{ forgotHint }}</span></div>
          <div class="lrow"><span class="lprefix">新密码</span><input v-model="f.ffpwd" class="lin" :type="typeOf('ffpwd')" placeholder="至少6位"><button class="leye" :class="{ on: showPwd.ffpwd }" @click="toggleEye('ffpwd')" v-html="showPwd.ffpwd ? EYE_OPEN : EYE_CLOSED"></button></div>
          <div class="lrow"><span class="lprefix">确认</span><input v-model="f.ffpwd2" class="lin" :type="typeOf('ffpwd2')" placeholder="再次输入新密码"><button class="leye" :class="{ on: showPwd.ffpwd2 }" @click="toggleEye('ffpwd2')" v-html="showPwd.ffpwd2 ? EYE_OPEN : EYE_CLOSED"></button></div>
          <div class="lbtns"><button class="lreg" @click="switchTab('pwd')">返回登录</button><button class="llogin" @click="doReset()">重置密码</button></div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-ov { position:fixed; inset:0; z-index:100000; background:rgba(10,15,28,.55); display:flex; align-items:center; justify-content:center; }
html.dark .login-ov { background:rgba(5,8,16,.6); }
.login-card { position:relative; width:560px; max-width:94vw; background:#fff; border-radius:16px; padding:24px 28px 30px; box-shadow:0 20px 60px rgba(0,0,0,.35); }
html.dark .login-card { background:#141c2e; }
.lclose { position:absolute; top:12px; right:14px; border:0; background:transparent; color:var(--sub); font-size:24px; cursor:pointer; line-height:1; }
.lclose:hover { color:var(--txt); }
.ltabs { display:flex; align-items:center; justify-content:center; gap:14px; margin:2px 0 22px; font-size:27px; }
.ltab { cursor:pointer; color:var(--sub); font-weight:500; white-space:nowrap; flex-shrink:0; }
.ltab.on { color:var(--blue); font-weight:700; }
.lsep { width:1px; height:26px; background:var(--line); }
.lbody { display:block; }
.lrow { display:flex; align-items:center; gap:10px; border:1px solid var(--line); border-radius:12px; padding:12px 16px; margin-bottom:14px; }
.lprefix { color:var(--sub); font-size:23px; white-space:nowrap; }
.lin { flex:1; border:0; outline:0; background:transparent; color:var(--txt); font-size:23px; min-width:0; }
.lget { background:transparent; border:0; color:var(--blue); font-size:22px; cursor:pointer; white-space:nowrap; }
.lget:hover { text-decoration:underline; }
.lget.disable { color:var(--sub); cursor:default; }
.leye { background:transparent; border:0; color:var(--sub); font-size:22px; cursor:pointer; padding:0 4px; line-height:1; display:flex; align-items:center; }
.leye:hover { color:var(--blue); }
.leye.on { color:var(--blue); }
.lhint { font-size:20px; min-width:0; }
.lforgot { color:var(--blue); font-size:22px; cursor:pointer; white-space:nowrap; }
.lsubmit { display:block; width:100%; margin-top:6px; padding:13px 0; background:linear-gradient(135deg,#2c4a72,#4a6a94); color:#fff; border:0; border-radius:12px; font-size:24px; font-weight:700; cursor:pointer; transition:.15s; }
.lsubmit:hover { filter:brightness(1.1); }
.lsubmit:disabled { opacity:.6; cursor:default; }
.lbtns { display:flex; gap:12px; margin-top:6px; }
.lreg, .llogin { flex:1; padding:13px 0; border-radius:12px; font-size:24px; font-weight:600; cursor:pointer; transition:.15s; }
.lreg { background:#fff; border:1px solid var(--line); color:var(--txt); }
.lreg:hover { border-color:var(--blue); color:var(--blue); }
.llogin { background:linear-gradient(135deg,#2c4a72,#4a6a94); color:#fff; border:0; }
.llogin:hover { filter:brightness(1.1); }
.ltip { text-align:center; margin-top:12px; color:var(--sub); font-size:20px; }
</style>
