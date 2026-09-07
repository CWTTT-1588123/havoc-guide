<template>
  <view class="pagebox">
    <view class="login-card panel">
      <view class="ltabs">
        <text class="ltab" :class="{ on: tab === 'code' }" @tap="switchTab('code')">验证码注册</text>
        <text class="lsep">|</text>
        <text class="ltab" :class="{ on: tab === 'pwd' }" @tap="switchTab('pwd')">密码登录</text>
      </view>

      <!-- 验证码注册 -->
      <view v-if="tab === 'code' && !showForgot" class="lbody">
        <view class="lrow">
          <text class="lprefix">邮箱</text>
          <input v-model="f.lacct" class="lin" type="text" placeholder="请输入邮箱" />
          <text class="lget" :class="{ disable: getBtn.disable }" @tap="getCode()">{{ getBtn.text }}</text>
        </view>
        <view class="lrow">
          <text class="lprefix">验证码</text>
          <input v-model="f.lcode" class="lin" type="text" placeholder="请输入验证码" />
        </view>
        <view class="lhint" v-if="codeHint" :style="{ color: codeHintColor }">{{ codeHint }}</view>
        <view class="lrow">
          <text class="lprefix">设置密码</text>
          <input v-model="f.lpwd" class="lin" :password="!showPwd.lpwd" placeholder="请至少输入六位数" />
          <text class="leye" @tap="toggleEye('lpwd')">{{ showPwd.lpwd ? '隐藏' : '显示' }}</text>
        </view>
        <view class="lrow">
          <text class="lprefix">确认密码</text>
          <input v-model="f.lpwd2" class="lin" :password="!showPwd.lpwd2" placeholder="再次输入密码" />
          <text class="leye" @tap="toggleEye('lpwd2')">{{ showPwd.lpwd2 ? '隐藏' : '显示' }}</text>
        </view>
        <button class="lsubmit" :disabled="regBtn.disable" @tap="doLogin()">{{ regBtn.text }}</button>
        <view class="ltip">验证码将发送到你邮箱，请查收后填入</view>
      </view>

      <!-- 密码登录 / 忘记密码 -->
      <view v-if="tab === 'pwd'" class="lbody">
        <template v-if="!showForgot">
          <view class="lrow">
            <text class="lprefix">账号</text>
            <input v-model="f.lpacct" class="lin" type="text" placeholder="邮箱或绑定手机号" />
            <text class="lforgot" @tap="gotoForgot()">忘记密码?</text>
          </view>
          <view class="lrow">
            <text class="lprefix">密码</text>
            <input v-model="f.lppwd" class="lin" :password="!showPwd.lppwd" placeholder="请输入密码" />
            <text class="leye" @tap="toggleEye('lppwd')">{{ showPwd.lppwd ? '隐藏' : '显示' }}</text>
          </view>
          <view class="lbtns">
            <button class="lreg" @tap="switchTab('code')">注册</button>
            <button class="llogin" @tap="pwdLogin()">登录</button>
          </view>
        </template>

        <template v-else>
          <view class="lrow">
            <text class="lprefix">账号</text>
            <input v-model="f.ffacct" class="lin" type="text" placeholder="请输入注册邮箱" />
          </view>
          <view class="lrow">
            <text class="lprefix">验证码</text>
            <input v-model="f.ffcode" class="lin" type="text" placeholder="请输入验证码" />
            <text class="lget" :class="{ disable: ffGetBtn.disable }" @tap="forgotSend()">{{ ffGetBtn.text }}</text>
          </view>
          <view class="lhint" v-if="forgotHint" :style="{ color: forgotHintColor }">{{ forgotHint }}</view>
          <view class="lrow">
            <text class="lprefix">新密码</text>
            <input v-model="f.ffpwd" class="lin" :password="!showPwd.ffpwd" placeholder="至少6位" />
            <text class="leye" @tap="toggleEye('ffpwd')">{{ showPwd.ffpwd ? '隐藏' : '显示' }}</text>
          </view>
          <view class="lrow">
            <text class="lprefix">确认</text>
            <input v-model="f.ffpwd2" class="lin" :password="!showPwd.ffpwd2" placeholder="再次输入新密码" />
            <text class="leye" @tap="toggleEye('ffpwd2')">{{ showPwd.ffpwd2 ? '隐藏' : '显示' }}</text>
          </view>
          <view class="lbtns">
            <button class="lreg" @tap="switchTab('pwd')">返回登录</button>
            <button class="llogin" @tap="doReset()">重置密码</button>
          </view>
        </template>
      </view>
    </view>
  </view>
</template>

<script>
import { reactive, ref } from 'vue'
import { saveAuth, toast, alertMsg } from '../../store'
import { apiAuth } from '../../api'

const EMAIL_RE = /^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/

export default {
  setup() {
    const tab = ref('code')
    const showForgot = ref(false)
    const f = reactive({ lacct: '', lcode: '', lpwd: '', lpwd2: '', lpacct: '', lppwd: '', ffacct: '', ffcode: '', ffpwd: '', ffpwd2: '' })
    const showPwd = reactive({ lpwd: false, lpwd2: false, lppwd: false, ffpwd: false, ffpwd2: false })
    const codeHint = ref(''); const codeHintColor = ref('#b31212')
    const forgotHint = ref(''); const forgotHintColor = ref('#b31212')
    const getBtn = ref({ disable: false, text: '获取验证码' })
    const ffGetBtn = ref({ disable: false, text: '获取验证码' })
    const regBtn = ref({ disable: false, text: '注册' })

    function toggleEye(k) { showPwd[k] = !showPwd[k] }
    function clearInputs() {
      Object.keys(f).forEach(k => { f[k] = '' })
      Object.keys(showPwd).forEach(k => { showPwd[k] = false })
      codeHint.value = ''; forgotHint.value = ''
      getBtn.value = { disable: false, text: '获取验证码' }
      ffGetBtn.value = { disable: false, text: '获取验证码' }
      regBtn.value = { disable: false, text: '注册' }
    }
    function switchTab(t) { tab.value = t; showForgot.value = false; clearInputs() }
    function gotoForgot() { showForgot.value = true; clearInputs() }

    async function getCode() {
      const acct = f.lacct.trim()
      if (!acct) { alertMsg('请先输入邮箱'); return }
      if (!EMAIL_RE.test(acct)) { codeHintColor.value = '#b31212'; codeHint.value = '邮箱输入错误，请检查格式'; return }
      const r = await apiAuth('send_code', { contact: acct })
      if (r.data && r.data.ok) {
        codeHintColor.value = '#18c66a'
        codeHint.value = '验证码已发送到 ' + acct + '，请查收邮箱'
        setTimeout(() => { codeHint.value = '' }, 2000)
        getBtn.value = { disable: true, text: '已发送' }
        setTimeout(() => { getBtn.value = { disable: false, text: '获取验证码' } }, 10000)
      } else {
        codeHintColor.value = '#b31212'
        codeHint.value = (r.data && r.data.error) || '发送失败'
      }
    }

    async function doLogin() {
      const contact = f.lacct.trim(), code = f.lcode.trim(), pw = f.lpwd, pw2 = f.lpwd2
      if (!contact || !code) { alertMsg('请输入邮箱和验证码'); return }
      if (pw.length < 6) { alertMsg('请至少输入六位密码'); return }
      if (pw !== pw2) { alertMsg('两次密码不一致'); return }
      regBtn.value = { disable: true, text: '注册中…' }
      const body = { contact, code, password: pw }
      let r = await apiAuth('register', body)
      if (r.data && r.data.error === '该邮箱已注册，请直接登录') { r = await apiAuth('login', body) }
      regBtn.value = { disable: false, text: '注册' }
      if (r.data && r.data.ok) {
        saveAuth({ token: r.data.token, user: r.data.user })
        toast('注册成功，欢迎 ' + r.data.user.name)
        setTimeout(() => uni.navigateBack(), 600)
      } else {
        alertMsg((r.data && r.data.error) || '操作失败')
      }
    }

    async function pwdLogin() {
      const contact = f.lpacct.trim(), pw = f.lppwd
      if (!contact || !pw) { alertMsg('请输入账号和密码'); return }
      const r = await apiAuth('login', { contact, password: pw })
      if (r.data && r.data.ok) {
        saveAuth({ token: r.data.token, user: r.data.user })
        toast('欢迎回来，' + r.data.user.name)
        setTimeout(() => uni.navigateBack(), 600)
      } else {
        alertMsg((r.data && r.data.error) || '登录失败')
      }
    }

    async function forgotSend() {
      const acct = f.ffacct.trim()
      if (!acct) { alertMsg('请输入注册邮箱'); return }
      if (!EMAIL_RE.test(acct)) { forgotHintColor.value = '#b31212'; forgotHint.value = '邮箱输入错误，请检查格式'; return }
      ffGetBtn.value = { disable: true, text: '发送中…' }
      forgotHint.value = ''
      const r = await apiAuth('forgot', { contact: acct })
      ffGetBtn.value = { disable: false, text: '获取验证码' }
      if (r.data && r.data.ok) {
        forgotHintColor.value = '#18c66a'
        forgotHint.value = '重置验证码已发送到 ' + acct + '，请查收邮箱'
        setTimeout(() => { forgotHint.value = '' }, 3000)
      } else {
        forgotHintColor.value = '#b31212'
        forgotHint.value = (r.data && r.data.error) || '发送失败'
      }
    }

    async function doReset() {
      const acct = f.ffacct.trim(), code = f.ffcode.trim(), a = f.ffpwd, b = f.ffpwd2
      if (!acct || !code) { alertMsg('请输入邮箱和验证码'); return }
      if (a.length < 6) { alertMsg('新密码至少6位'); return }
      if (a !== b) { alertMsg('两次密码不一致'); return }
      const r = await apiAuth('reset', { contact: acct, code, password: a })
      if (r.data && r.data.ok) { toast('密码已重置，请用新密码登录'); clearInputs(); switchTab('pwd') }
      else { alertMsg((r.data && r.data.error) || '重置失败') }
    }

    return {
      tab, showForgot, f, showPwd, codeHint, codeHintColor, forgotHint, forgotHintColor,
      getBtn, ffGetBtn, regBtn,
      toggleEye, clearInputs, switchTab, gotoForgot, getCode, doLogin, pwdLogin, forgotSend, doReset,
    }
  },
}
</script>

<style>
.login-card { padding: 36rpx 32rpx 44rpx; }
.ltabs { display: flex; align-items: center; justify-content: center; gap: 28rpx; margin-bottom: 40rpx; }
.ltab { color: var(--sub); font-weight: 500; font-size: 38rpx; }
.ltab.on { color: var(--blue); font-weight: 700; }
.lsep { color: var(--line); }
.lbody { display: block; }
.lrow {
  display: flex;
  align-items: center;
  gap: 20rpx;
  border: 1rpx solid var(--line);
  border-radius: 24rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 24rpx;
  background: #fff;
}
.lprefix { color: var(--sub); font-size: 32rpx; white-space: nowrap; }
.lin { flex: 1; font-size: 32rpx; color: var(--txt); min-width: 0; }
.lget { color: var(--blue); font-size: 30rpx; white-space: nowrap; }
.lget.disable { color: var(--sub); }
.leye { color: var(--sub); font-size: 28rpx; white-space: nowrap; }
.lhint { font-size: 28rpx; margin: -12rpx 0 20rpx 24rpx; }
.lforgot { color: var(--blue); font-size: 30rpx; white-space: nowrap; }
.lsubmit {
  display: block;
  width: 100%;
  margin-top: 12rpx;
  padding: 24rpx 0;
  background: linear-gradient(135deg, #2c4a72, #4a6a94);
  color: #fff;
  border-radius: 24rpx;
  font-size: 34rpx;
  font-weight: 700;
  border: 0;
}
.lsubmit::after { border: 0; }
.lsubmit[disabled] { opacity: 0.6; }
.ltip { text-align: center; margin-top: 20rpx; color: var(--sub); font-size: 28rpx; }
.lbtns { display: flex; gap: 24rpx; margin-top: 12rpx; }
.lreg, .llogin {
  flex: 1;
  padding: 22rpx 0;
  border-radius: 24rpx;
  font-size: 34rpx;
  font-weight: 600;
  border: 0;
  margin: 0;
}
.lreg::after, .llogin::after { border: 0; }
.lreg { background: #fff; border: 1rpx solid var(--line); color: var(--txt); }
.llogin { background: linear-gradient(135deg, #2c4a72, #4a6a94); color: #fff; }
</style>
