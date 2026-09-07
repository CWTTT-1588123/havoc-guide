<template>
  <view class="pagebox">
    <!-- 未登录 -->
    <view v-if="!u" class="panel login-tip">
      <view class="tip-title">登录后可以</view>
      <view class="tip-line">· 发表评论</view>
      <view class="tip-line">· 更换头像 / 修改资料</view>
      <button class="btn primary tip-btn" @tap="goLogin">登录 / 注册</button>
    </view>

    <!-- 已登录 -->
    <template v-else>
      <!-- 账号卡 -->
      <view class="panel acc">
        <image class="acc-av" :src="avatar" mode="aspectFill" @tap="pickAvatar" />
        <view class="acc-info">
          <view class="acc-name">{{ u.name }}</view>
          <view class="acc-sub">{{ u.contact }}<text v-if="u.phone">　·　手机 {{ u.phone }}</text></view>
          <view class="acc-role">{{ u.is_admin ? '管理员' : '普通用户' }}</view>
        </view>
        <view class="acc-btns">
          <button class="btn" @tap="pickAvatar">更换头像</button>
          <button class="btn" @tap="form = form === 'pwd' ? '' : 'pwd'">更改密码</button>
          <button class="btn" @tap="form = form === 'phone' ? '' : 'phone'">{{ u.phone ? '修改手机号' : '绑定手机号' }}</button>
          <button class="btn" @tap="form = form === 'name' ? '' : 'name'">更改用户名</button>
          <button class="btn" @tap="form = form === 'email' ? '' : 'email'">更换邮箱</button>
          <button class="btn danger" @tap="onLogout">退出登录</button>
        </view>
      </view>

      <!-- 表单区 -->
      <view v-if="form" class="panel form">
        <view class="form-t">{{ FORM_TITLES[form] }}</view>

        <template v-if="form === 'pwd'">
          <input v-model="pwdN" class="form-in" password placeholder="新密码（至少4位）" />
          <input v-model="pwdN2" class="form-in" password placeholder="确认新密码" />
          <view class="form-btns">
            <button class="btn primary" @tap="savePwd">保存</button>
            <button class="btn" @tap="form = ''">取消</button>
          </view>
        </template>

        <template v-else-if="form === 'name'">
          <input v-model="nameV" class="form-in" placeholder="新的用户名" />
          <view class="form-btns">
            <button class="btn primary" @tap="saveName">保存</button>
            <button class="btn" @tap="form = ''">取消</button>
          </view>
        </template>

        <template v-else-if="form === 'phone'">
          <view class="form-tip">绑定后可用该手机号登录（一个手机号只能绑定一个账号）</view>
          <input v-model="phoneV" class="form-in" type="number" placeholder="输入11位手机号" />
          <view class="form-btns">
            <button class="btn primary" @tap="savePhone">{{ u.phone ? '保存修改' : '确认绑定' }}</button>
            <button v-if="u.phone" class="btn danger" @tap="unbindPhone">解绑</button>
            <button class="btn" @tap="form = ''">取消</button>
          </view>
        </template>

        <template v-else-if="form === 'email'">
          <view class="form-tip">将向新邮箱发送验证码，验证通过后新邮箱即成为登录邮箱</view>
          <input v-model="emailV" class="form-in" placeholder="输入新邮箱地址" />
          <view class="form-crow">
            <input v-model="codeV" class="form-in" placeholder="邮箱验证码" />
            <button class="btn" :disabled="codeSending" @tap="sendEmailCode">{{ codeSending ? '已发送' : '获取验证码' }}</button>
          </view>
          <view class="form-btns">
            <button class="btn primary" @tap="saveEmail">保存</button>
            <button class="btn" @tap="form = ''">取消</button>
          </view>
        </template>

        <template v-else-if="form === 'avatar'">
          <view class="form-tip">已选择图片，确认后上传为新头像</view>
          <image v-if="avatarPreview" class="avatar-prev" :src="avatarPreview" mode="aspectFill" />
          <view class="form-btns">
            <button class="btn primary" @tap="uploadAvatar">确认上传</button>
            <button class="btn" @tap="cancelAvatar">取消</button>
          </view>
        </template>
      </view>
    </template>

    <site-foot />
  </view>
</template>

<script>
import { ref, computed } from 'vue'
import { state, loadAuth, updateAuthUser, toast, alertMsg, confirmMsg, logout } from '../../store'
import { apiAuth, fileToDataURL } from '../../api'

const FORM_TITLES = { pwd: '修改密码', name: '修改用户名', phone: '绑定手机号', email: '更换邮箱', avatar: '预览头像' }

export default {
  setup() {
    const u = computed(() => state.auth && state.auth.user)
    const avatar = computed(() => (u.value && u.value.avatar) ? u.value.avatar : '/static/preset_avatar.png')

    const form = ref('')
    const pwdN = ref(''); const pwdN2 = ref('')
    const nameV = ref('')
    const phoneV = ref('')
    const emailV = ref(''); const codeV = ref(''); const codeSending = ref(false)
    const avatarPreview = ref('')

    function goLogin() { uni.navigateTo({ url: '/pages/login/login' }) }

    async function pickAvatar() {
      const res = await uni.chooseImage({ count: 1, sizeType: ['compressed'] })
      const path = res.tempFilePaths && res.tempFilePaths[0]
      if (!path) return
      avatarPreview.value = await fileToDataURL(path)
      form.value = 'avatar'
    }
    function cancelAvatar() { avatarPreview.value = ''; form.value = '' }
    async function uploadAvatar() {
      if (!avatarPreview.value) return
      const r = await apiAuth('avatar', { avatar: avatarPreview.value })
      if (r.data && r.data.ok) {
        updateAuthUser({ ...u.value, avatar: r.data.avatar })
        avatarPreview.value = ''; form.value = ''
        toast('头像已更新')
      } else { alertMsg((r.data && r.data.error) || '上传失败') }
    }

    async function savePwd() {
      const a = pwdN.value, b = pwdN2.value
      if (a.length < 4) { alertMsg('密码至少4位'); return }
      if (a !== b) { alertMsg('两次密码不一致'); return }
      const r = await apiAuth('password', { password: a })
      if (r.data && r.data.ok) { form.value = ''; toast('密码已修改') }
      else { alertMsg((r.data && r.data.error) || '修改失败') }
    }
    async function saveName() {
      const n = nameV.value.trim()
      if (!n) { alertMsg('请输入用户名'); return }
      const r = await apiAuth('name', { name: n })
      if (r.data && r.data.ok) { updateAuthUser({ ...u.value, name: r.data.name }); form.value = ''; toast('用户名已更新') }
      else { alertMsg((r.data && r.data.error) || '修改失败') }
    }
    async function savePhone() {
      const p = phoneV.value.trim()
      if (!/^1[3-9]\d{9}$/.test(p)) { alertMsg('请输入正确的手机号（1开头11位）'); return }
      const r = await apiAuth('phone', { phone: p })
      if (r.data && r.data.ok) { updateAuthUser({ ...u.value, phone: r.data.phone }); form.value = ''; toast('手机号已绑定') }
      else { alertMsg((r.data && r.data.error) || '绑定失败') }
    }
    async function unbindPhone() {
      if (!(await confirmMsg('确定解绑当前手机号？'))) return
      const r = await apiAuth('phone', { phone: '' })
      if (r.data && r.data.ok) { updateAuthUser({ ...u.value, phone: '' }); form.value = ''; toast('已解绑手机号') }
      else { alertMsg((r.data && r.data.error) || '解绑失败') }
    }
    async function sendEmailCode() {
      const em = emailV.value.trim()
      if (!em || !em.includes('@')) { alertMsg('请输入正确的邮箱地址'); return }
      const r = await apiAuth('email_code', { email: em })
      if (r.data && r.data.ok) { codeSending.value = true; toast('验证码已发送，请查收邮箱') }
      else { alertMsg((r.data && r.data.error) || '发送失败'); codeSending.value = false }
    }
    async function saveEmail() {
      const em = emailV.value.trim()
      if (!em || !em.includes('@')) { alertMsg('请输入正确的邮箱地址'); return }
      if (!codeV.value.trim()) { alertMsg('请输入验证码'); return }
      const r = await apiAuth('email', { email: em, code: codeV.value.trim() })
      if (r.data && r.data.ok) {
        updateAuthUser({ ...u.value, contact: r.data.contact })
        form.value = ''; emailV.value = ''; codeV.value = ''; codeSending.value = false
        toast('邮箱已更换，下次可用新邮箱登录')
      } else { alertMsg((r.data && r.data.error) || '更换失败') }
    }

    async function onLogout() {
      if (!(await confirmMsg('确定退出登录？'))) return
      await logout()
      toast('已退出登录')
    }

    return {
      u, avatar, form, FORM_TITLES,
      pwdN, pwdN2, nameV, phoneV, emailV, codeV, codeSending, avatarPreview,
      goLogin, pickAvatar, cancelAvatar, uploadAvatar,
      savePwd, saveName, savePhone, unbindPhone, sendEmailCode, saveEmail, onLogout,
    }
  },
  onShow() { loadAuth() },
}
</script>

<style>
.login-tip { padding: 40rpx 32rpx; }
.tip-title { font-size: 38rpx; font-weight: 700; color: var(--blue); margin-bottom: 16rpx; }
.tip-line { font-size: 32rpx; color: var(--txt); line-height: 1.8; }
.tip-btn { margin-top: 28rpx; }

.acc { padding: 32rpx; display: flex; flex-direction: column; align-items: center; gap: 20rpx; margin-bottom: 24rpx; }
.acc-av { width: 144rpx; height: 144rpx; border-radius: 50%; box-shadow: 0 0 0 6rpx var(--blue); }
.acc-info { text-align: center; }
.acc-name { font-size: 40rpx; font-weight: 700; }
.acc-sub { font-size: 30rpx; color: var(--sub); margin-top: 6rpx; }
.acc-role { display: inline-block; margin-top: 10rpx; background: #fdf6e0; border: 1rpx solid #e0ca86; color: #8a6d1a; padding: 2rpx 20rpx; border-radius: 16rpx; font-size: 26rpx; font-weight: 600; }
.acc-btns { display: flex; flex-wrap: wrap; gap: 16rpx; justify-content: center; }

.form { padding: 32rpx; margin-bottom: 24rpx; display: flex; flex-direction: column; gap: 20rpx; }
.form-t { font-size: 34rpx; font-weight: 700; }
.form-tip { color: var(--sub); font-size: 28rpx; }
.form-in {
  background: #fff;
  border: 1rpx solid var(--line);
  color: var(--txt);
  padding: 20rpx 24rpx;
  border-radius: 20rpx;
  font-size: 32rpx;
}
.form-crow { display: flex; gap: 16rpx; align-items: center; }
.form-crow .form-in { flex: 1; }
.form-btns { display: flex; gap: 20rpx; }
.avatar-prev { width: 160rpx; height: 160rpx; border-radius: 50%; }
</style>
