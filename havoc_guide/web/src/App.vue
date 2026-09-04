<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { state, loadAuth, openLogin, getJSON, applyPrefs, toast } from './store'
import LoginModal from './components/LoginModal.vue'
import AvatarMenu from './components/AvatarMenu.vue'
import ProfileView from './components/ProfileView.vue'
import AdminView from './components/AdminView.vue'
import HomeView from './components/HomeView.vue'
import DetailView from './components/DetailView.vue'
import CategoryView from './components/CategoryView.vue'
import AllAugmentsView from './components/AllAugmentsView.vue'
import Pet from './components/Pet.vue'

const ver = ref('')
const hovered = ref(false)
const avatar = computed(() =>
  (state.auth && state.auth.user && state.auth.user.avatar)
    ? state.auth.user.avatar : '/static/preset_avatar.png')

const isLogged = computed(() => !!state.auth)

function onLoginClick() { if (isLogged.value) { toast('已登录（点右上角头像更多操作）') } else { openLogin() } }
function onEnter() { hovered.value = true }
function onLeave() { hovered.value = false; state.avatarMenuOpen = false }
const showAvatarMenu = computed(() => isLogged.value && (state.avatarMenuOpen || hovered.value))
const showLoginPop = computed(() => !isLogged.value && hovered.value)
const showHeader = computed(() => state.view !== 'profile' && state.view !== 'admin')
function goHome() { state.view = 'home'; state.champId = ''; state.cat = '' }

let suppressPush = false

function syncHeaderH() {
  const h = document.querySelector('header')
  if (h) document.documentElement.style.setProperty('--headerh', (h.offsetHeight) + 'px')
}

onMounted(() => {
  loadAuth()
  applyPrefs()
  syncHeaderH()
  window.addEventListener('resize', syncHeaderH)
  getJSON('/api/version').then(d => { if (d && d.game_version) ver.value = '版本 ' + d.game_version }).catch(() => {})
  // 浏览器后退/前进 → 切换视图
  window.addEventListener('popstate', (e) => {
    const s = e.state || {}
    suppressPush = true
    state.view = s.view || 'home'
    state.champId = s.champId || ''
    state.cat = s.cat || ''
    suppressPush = false
  })
  // 首次进入：替换当前历史（replacestate，避免初始多出一条）
  history.replaceState({ view: 'home', champId: '', cat: '' }, '', '#/home')
})
// 视图变化 → 清悬停 + 记录历史（后退可用）
watch(() => state.view, () => {
  hovered.value = false; state.avatarMenuOpen = false
  if (suppressPush) return
  history.pushState({ view: state.view, champId: state.champId, cat: state.cat }, '', '#/' + state.view)
})
</script>

<template>
  <header v-if="showHeader">
    <h1 class="brand titlebtn" @click="goHome">海克斯大乱斗 攻略站</h1>
    <div class="loginwrap" :class="{ logged: isLogged }" @mouseenter="onEnter" @mouseleave="onLeave">
      <button class="loginbtn" @click="onLoginClick">
        <template v-if="isLogged"><img class="login-av" :src="avatar" alt=""></template>
        <template v-else>登录</template>
      </button>
      <div v-if="showLoginPop" class="loginpop"><b>登录后可以：</b><div>· 发表评论</div><div>· 自定义网页背景</div><div>· 锁定 Q 版人物形象</div><div>· 改变网站风格</div></div>
      <AvatarMenu v-if="showAvatarMenu" />
    </div>
  </header>

  <main class="page">
    <HomeView v-if="state.view === 'home'" />
    <DetailView v-else-if="state.view === 'champ'" />
    <CategoryView v-else-if="state.view === 'category'" />
    <AllAugmentsView v-else-if="state.view === 'augments'" />
    <ProfileView v-else-if="state.view === 'profile'" />
    <AdminView v-else-if="state.view === 'admin'" />
  </main>

  <div class="verlabel" v-if="ver">{{ ver }}</div>
  <LoginModal v-if="state.loginOpen" />
  <Pet />
</template>
