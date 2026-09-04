<script setup>
import { computed } from 'vue'
import { state, toggleTheme, logout, loadPrefs } from '../store'

const u = computed(() => state.auth && state.auth.user)
const avatar = computed(() => (u.value && u.value.avatar) ? u.value.avatar : '/static/preset_avatar.png')
const themeLabel = computed(() => (loadPrefs().theme === 'dark' ? '深色' : '浅色'))

function goProfile() { state.view = 'profile'; state.avatarMenuOpen = false }
function goAdmin() { state.view = 'admin'; state.avatarMenuOpen = false }
async function onLogout() { await logout() }
</script>

<template>
  <div class="avatar-menu">
    <img class="am-av" :src="avatar" alt="">
    <div class="am-name">{{ u ? u.name : '' }}</div>
    <div class="am-badges"><span class="am-admin">{{ u && u.is_admin ? '管理员' : '普通用户' }}</span></div>
    <div class="am-item" @click="goProfile">个人中心 <span class="am-chev">›</span></div>
    <div class="am-item" v-if="u && u.is_admin" @click="goAdmin">管理后台 <span class="am-chev">›</span></div>
    <div class="am-item" @click="toggleTheme()">主题：{{ themeLabel }} <span class="am-chev">›</span></div>
    <div class="am-item logout" @click="onLogout">退出登录 <span class="am-chev">›</span></div>
  </div>
</template>

<style scoped>
.avatar-menu { position:absolute; top:100%; right:0; width:300px; background:#fff; border:1px solid var(--line); border-radius:16px; box-shadow:0 14px 40px rgba(0,0,0,.22); padding-bottom:8px; overflow:hidden; z-index:100000; opacity:1; visibility:visible; transform:none; pointer-events:auto; }
html.dark .avatar-menu { background:#1c2536; }
.avatar-menu::before { content:''; position:absolute; top:-12px; left:0; right:0; height:12px; }
.am-av { width:76px; height:76px; border-radius:50%; object-fit:cover; display:block; margin:20px auto 10px; box-shadow:0 0 0 3px var(--blue); }
.am-name { text-align:center; font-size:27px; font-weight:700; color:var(--txt); }
.am-badges { text-align:center; margin-top:6px; }
.am-admin { background:#ff5a7f; color:#fff; font-size:18px; padding:2px 14px; border-radius:10px; font-weight:600; display:inline-block; }
.am-item { display:flex; align-items:center; gap:10px; padding:12px 22px; color:var(--txt); font-size:23px; cursor:pointer; transition:.12s; }
.am-item:hover { background:rgba(74,168,255,.08); }
.am-chev { margin-left:auto; color:var(--sub); }
.am-item.logout { color:var(--red); }
</style>
