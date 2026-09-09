<template>
  <view class="pagebox" v-if="d">
    <view class="detail">
      <!-- 头部 -->
      <view class="dhead">
        <image class="dimg" :src="imgFailed ? AV_FALLBACK : d.image" mode="aspectFill" @error="onImgErr" />
        <view>
          <view class="dtitle">{{ d.name }}</view>
          <view class="dsub">整体胜率 <text class="bigwr">{{ fmtPct(d.overall.wr) }}</text> · {{ d.overall.games }} 场</view>
        </view>
      </view>

      <!-- 板块导航 -->
      <view class="secnav" v-if="sects.length">
        <button v-for="s in sects" :key="s.key" class="navbtn" @tap="jumpTo(s.key)">{{ s.title }}</button>
        <button class="navbtn" @tap="jumpTo('comments')">评论区</button>
      </view>

      <!-- 各数据板块 -->
      <view v-for="s in sects" :key="s.key" class="sec" :id="'sec-' + s.key">
        <view class="sechead"><text>{{ s.title }}</text></view>
        <view class="cap">{{ s.caption }}</view>

        <!-- 最优单个符文：品质分档，每档两列卡片 -->
        <template v-if="s.key === 'augments'">
          <view v-for="(g, gi) in d.augments_by_quality" :key="gi" class="aqblock">
            <view class="cq">{{ g.quality }}</view>
            <view class="aqgrid">
              <single-card v-for="(a, ai) in g.items.slice(0, 5)" :key="ai" :item="a" :index="ai" />
            </view>
          </view>
        </template>

        <!-- 最优符文组合 -->
        <view v-else-if="s.key === 'combos'" class="list">
          <combo-row v-for="(c, i) in d.combos.slice(0, 6)" :key="i" :c="c" />
        </view>

        <!-- 搭配增益 -->
        <view v-else-if="s.key === 'synergy'" class="list">
          <synergy-row v-for="(x, i) in d.synergy.slice(0, 6)" :key="i" :s="x" />
        </view>

        <!-- 核心出装 -->
        <view v-else-if="s.key === 'builds'" class="list">
          <build-row v-for="(x, i) in d.builds.slice(0, 6)" :key="i" :b="x" />
        </view>

        <!-- 克制推荐 -->
        <view v-else-if="s.key === 'counters'" class="list">
          <counter-row v-for="(x, i) in d.counters.slice(0, 6)" :key="i" :s="x" />
        </view>

        <view v-if="s.hasMore" class="secmore">
          <button class="arrow" @tap="goMore(s.key)">更多 ›</button>
        </view>
        <view class="secend"></view>
      </view>

      <!-- 评论区 -->
      <view class="sec" id="sec-comments">
        <view class="sechead"><text>评论区</text></view>
        <view class="cap">说说你对 {{ d.name }} 符文/出装的看法</view>
        <view class="comment-box">
          <view v-if="state.auth" class="comrow">
            <textarea v-model="commentText" class="com-in" placeholder="写点什么吧…" :maxlength="1000" auto-height />
            <button class="btn primary com-send" @tap="postComment">发表</button>
          </view>
          <view v-else class="com-login">
            <text>登录后可以评论</text>
            <button class="btn" @tap="goLogin">去登录</button>
          </view>
          <view class="com-list">
            <view v-if="!comments.length" class="empty">还没有评论，来发第一条吧</view>
            <view v-for="(c, i) in comments" :key="i" class="com-item">
              <view class="com-name">{{ c.name }}</view>
              <view class="com-text">{{ c.text }}</view>
              <view class="com-time">{{ fmtTs(c.ts) }}</view>
            </view>
          </view>
        </view>
        <view class="secend"></view>
      </view>
    </view>

    <site-foot />
    <aug-desc-modal />
  </view>

  <view v-else class="pagebox"><view class="empty">加载中…</view></view>
</template>

<script>
import { state, AV_FALLBACK, toast, alertMsg, handle401 } from '../../store'
import { getJSON, postJSON } from '../../api'
import { fmtPct, fmtTs } from '../../data'

export default {
  data() {
    return {
      state,
      cid: '',
      d: null,
      comments: [],
      commentText: '',
      imgFailed: false,
    }
  },
  computed: {
    sects() {
      if (!this.d) return []
      const x = this.d
      const out = []
      if (x.augments_by_quality && x.augments_by_quality.length) {
        out.push({ key: 'augments', title: '最优单个符文', caption: '该英雄带这个符文胜率最高（按品质分档）', hasMore: x.augments_by_quality.some(g => g.items.length > 5) })
      }
      if (x.combos && x.combos.length) out.push({ key: 'combos', title: '最优符文套路', caption: '这几个符文一起带的胜率', hasMore: x.combos.length > 6 })
      if (x.synergy && x.synergy.length) out.push({ key: 'synergy', title: '搭配增益', caption: '这两个符文一起带，胜率比该英雄平均▲高/▼低', hasMore: x.synergy.length > 6 })
      if (x.builds && x.builds.length) out.push({ key: 'builds', title: '核心出装', caption: '该英雄这流派常见的核心三件套', hasMore: x.builds.length > 6 })
      if (x.counters && x.counters.length) out.push({ key: 'counters', title: '克制推荐', caption: '敌方是这类阵容时，选这个符文克制（▲ 克制加成 / ▼ 反被压制）', hasMore: x.counters.length > 6 })
      return out
    },
  },
  onLoad(options) {
    this.cid = (options && options.id) || state.champId || ''
    if (!this.cid) { uni.navigateBack(); return }
    this.load()
  },
  onShareAppMessage() {
    return {
      title: (this.d ? this.d.name + ' ' : '') + '海克斯大乱斗符文胜率 · 海克斯大乱斗攻略站',
      path: '/pages/champ/champ?id=' + this.cid,
    }
  },
  methods: {
    fmtPct, fmtTs,
    async load() {
      try {
        this.d = await getJSON('/api/champion/' + this.cid)
        if (!this.d || !this.d.overall) { alertMsg('暂无该英雄数据'); return }
        uni.setNavigationBarTitle({ title: this.d.name })
        await this.loadComments()
      } catch (e) {
        toast('网络异常，请稍后重试')
      }
    },
    async loadComments() {
      try {
        const r = await getJSON('/api/champion/' + this.cid + '/comments')
        this.comments = (r.comments || []).slice().reverse()
      } catch (e) {}
    },
    async postComment() {
      const t = this.commentText.trim()
      if (!t) { toast('请输入评论内容'); return }
      const r = await postJSON('/api/champion/' + this.cid + '/comments', { text: t })
      if (r.status === 200 && r.data.ok) {
        this.commentText = ''
        await this.loadComments()
        toast('评论已发布')
      } else {
        handle401(r.status)
        alertMsg((r.data && r.data.error) || '发送失败')
      }
    },
    goMore(k) { uni.navigateTo({ url: '/pages/section/section?cid=' + this.cid + '&key=' + k }) },
    goLogin() { uni.navigateTo({ url: '/pages/login/login' }) },
    onImgErr() { this.imgFailed = true },
    jumpTo(key) {
      uni.pageScrollTo({ selector: '#sec-' + key, duration: 300 })
    },
  },
}
</script>

<style>
/* 单个符文品质分档：每档标题 + 两列卡片 */
.aqblock { margin-bottom: 28rpx; }
.aqblock:last-child { margin-bottom: 0; }
.cq { color: var(--gold); font-size: 34rpx; font-weight: 600; margin-bottom: 20rpx; }
.aqgrid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20rpx; }

.list { display: flex; flex-direction: column; gap: 20rpx; }
</style>
