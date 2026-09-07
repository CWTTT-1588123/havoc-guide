<template>
  <view class="pagebox">
    <!-- 搜索行 + 登录按钮 -->
    <view class="toprow">
      <view class="sbar">
        <input v-model="state.q" class="sb-in" type="text" placeholder="搜索英雄（可搜外号）" confirm-type="search" />
        <text v-if="state.q" class="sb-clear" @tap="state.q = ''">✕</text>
      </view>
      <button class="btn loginbtn" :class="{ logged: isLogged }" @tap="onLogin">
        <image v-if="isLogged" class="login-av" :src="avatar" mode="aspectFill" />
        <text v-else>登录</text>
      </button>
    </view>

    <!-- 排序工具栏 -->
    <view class="toolbar">
      <button class="btn" :class="{ active: sort === 'wilson' }" @tap="setSort('wilson')">综合胜率</button>
      <button class="btn" :class="{ active: sort === 'wr' }" @tap="setSort('wr')">纯胜率</button>
      <button class="btn" :class="{ active: sort === 'games' }" @tap="setSort('games')">场次</button>
      <button class="btn" @tap="toggleAsc">{{ ascending ? '降序▼' : '升序▲' }}</button>
      <button class="btn primary" @tap="goAugments">所有符文</button>
      <button class="btn" @tap="goCategories">英雄分类</button>
    </view>

    <!-- 排行榜卡片列表（手机端：纵向卡片，无横向滚动） -->
    <view class="listwrap">
      <view v-for="(c, i) in cur" :key="c.id" class="rowcard" @tap="goChamp(c.id)">
        <view class="rowmain">
          <image class="avatar" :src="imgOf(c)" mode="aspectFill" @error="imgErr(c)" />
          <text class="cname">{{ c.name }}</text>
          <view class="rankbadge" :class="rkClass(i)">{{ rankOf(i) }}</view>
        </view>
        <view class="rowaugs">
          <aug-chip v-for="b in c.best3 || []" :key="b.name" :name="b.name" :quality="b.quality" :icon="b.icon" size="sm" />
        </view>
      </view>
      <view v-if="!loaded" class="empty">加载中…</view>
      <view v-else-if="!cur.length" class="empty">没有找到匹配的英雄</view>
    </view>

    <!-- 分页 -->
    <view class="pager" v-if="pages > 1">
      <button class="pgbtn" :disabled="page <= 1" @tap="setPage(page - 1)">‹</button>
      <text class="pginfo">第 {{ page }} / {{ pages }} 页 · 共 {{ total }} 个英雄</text>
      <button class="pgbtn" :disabled="page >= pages" @tap="setPage(page + 1)">›</button>
    </view>

    <site-foot />
    <aug-desc-modal />
  </view>
</template>

<script>
import { state, AV_FALLBACK } from '../../store'
import { getJSON } from '../../api'
import { NAME_NICKS } from '../../nicknames'

export default {
  data() {
    return {
      state,
      champs: [],
      loaded: false,
      sort: 'wilson',
      ascending: false,
      per: 20,
      page: 1,
      errs: {},
    }
  },
  computed: {
    isLogged() { return !!state.auth },
    avatar() { return (state.auth && state.auth.user && state.auth.user.avatar) || '/static/preset_avatar.png' },
    filtered() {
      let list = this.champs
      const t = (state.q || '').trim().toLowerCase()
      if (t) list = list.filter(c => (c._search || '').includes(t))
      return list
    },
    sorted() {
      const sort = this.sort
      return this.filtered.slice().sort((a, b) => (this.ascending ? (a[sort] || 0) - (b[sort] || 0) : (b[sort] || 0) - (a[sort] || 0)))
    },
    total() { return this.sorted.length },
    pages() { return Math.max(1, Math.ceil(this.total / this.per)) },
    cur() {
      let page = this.page
      if (page > this.pages) page = this.pages
      if (page < 1) page = 1
      return this.sorted.slice((page - 1) * this.per, page * this.per)
    },
  },
  watch: {
    'state.q'() { this.page = 1 },
  },
  onLoad() { this.load() },
  onShareAppMessage() { return { title: '海克斯大乱斗攻略站 · 英雄符文胜率排行', path: '/pages/index/index' } },
  methods: {
    async load() {
      try {
        const list = await getJSON('/api/champions')
        this.champs = (list || []).map(c => ({ ...c, _search: ((c.name || '') + ' ' + (NAME_NICKS[c.name] || []).join(' ')).toLowerCase() }))
      } catch (e) {
        uni.showToast({ title: '网络异常，请稍后重试', icon: 'none' })
      }
      this.loaded = true
    },
    setSort(s) { this.sort = s; this.page = 1 },
    toggleAsc() { this.ascending = !this.ascending; this.page = 1 },
    setPage(p) { this.page = p },
    goChamp(id) { uni.navigateTo({ url: '/pages/champ/champ?id=' + id }) },
    goAugments() { uni.switchTab({ url: '/pages/augments/augments' }) },
    goCategories() { uni.navigateTo({ url: '/pages/category/category' }) },
    onLogin() {
      if (state.auth) { uni.switchTab({ url: '/pages/profile/profile' }); return }
      uni.navigateTo({ url: '/pages/login/login' })
    },
    rankOf(i) { return (this.page - 1) * this.per + i + 1 },
    rkClass(i) { const r = this.rankOf(i); return r === 1 ? 'r1' : r === 2 ? 'r2' : r === 3 ? 'r3' : '' },
    imgOf(c) { return this.errs[c.id] ? AV_FALLBACK : c.image },
    imgErr(c) { this.errs = { ...this.errs, [c.id]: true } },
  },
}
</script>

<style>
.toprow { display: flex; gap: 16rpx; align-items: center; margin-bottom: 20rpx; }
.loginbtn { flex: none; padding: 12rpx 28rpx; }
.loginbtn.logged { background: transparent; border: 0; padding: 0; }
.login-av { width: 76rpx; height: 76rpx; border-radius: 50%; box-shadow: 0 0 0 6rpx #2c3a55; }

.listwrap { display: flex; flex-direction: column; gap: 20rpx; }
.rowcard {
  background: var(--panel);
  border: 1rpx solid var(--line);
  border-radius: 28rpx;
  padding: 22rpx 20rpx;
  box-shadow: 0 12rpx 36rpx rgba(60, 90, 150, 0.08);
}
.rowmain { display: flex; align-items: center; gap: 20rpx; }
.avatar { width: 72rpx; height: 72rpx; border-radius: 24rpx; flex: none; }
.cname { font-size: 34rpx; font-weight: 700; flex: 1; min-width: 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.rankbadge {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 76rpx;
  height: 76rpx;
  padding: 0 20rpx;
  border-radius: 38rpx;
  font-size: 34rpx;
  font-weight: 800;
  color: #dfe6f5;
  background: linear-gradient(160deg, #161d33, #10142a);
  border: 1rpx solid rgba(100, 120, 200, 0.35);
  flex: none;
}
.rankbadge.r1 { color: #5a3c00; background: linear-gradient(160deg, #ffe9a8, #f5c84c); border-color: #d9a819; }
.rankbadge.r2 { color: #3a3f47; background: linear-gradient(160deg, #eef1f6, #c8d2e0); border-color: #9fb0c8; }
.rankbadge.r3 { color: #6a3a1a; background: linear-gradient(160deg, #f0cfa8, #d9955a); border-color: #b06a2e; }
.rowaugs { display: flex; flex-direction: column; align-items: flex-start; gap: 10rpx; margin-top: 16rpx; }

.pager { display: flex; align-items: center; justify-content: center; gap: 20rpx; margin-top: 32rpx; }
.pgbtn {
  width: 72rpx; height: 72rpx;
  border-radius: 24rpx;
  background: var(--panel2);
  border: 1rpx solid var(--line);
  color: #111;
  font-size: 40rpx;
  line-height: 1;
  padding: 0;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.pgbtn::after { border: 0; }
.pgbtn[disabled] { opacity: 0.35; }
.pginfo { font-size: 30rpx; color: #111; font-weight: 600; }
</style>
