<template>
  <view class="pagebox">
    <!-- 分支选择条 -->
    <view class="catpick">
      <view v-for="c in cats" :key="c" class="catcard" :class="{ on: state.cat === c }" @tap="pick(c)">
        <text class="ccname">{{ c }}</text>
        <text class="ccnum">{{ CAT_IDS[c].length }}位</text>
      </view>
    </view>

    <!-- 分类横幅 -->
    <view class="cathead panel" v-if="state.cat">
      <view class="catttl">{{ state.cat }} 英雄</view>
      <view class="capsub">{{ meta.desc }} · 共 {{ list.length }} 位 · 按综合胜率排序</view>
    </view>

    <!-- 英雄卡片网格 -->
    <view class="catgrid" v-if="state.cat">
      <view v-for="(c, i) in list" :key="c.id" class="catcard2" @tap="goChamp(c.id)">
        <view class="crank">{{ medal(i) }}</view>
        <view class="crow">
          <image class="cavatar" :src="imgOf(c)" mode="aspectFill" @error="imgErr(c)" />
          <view class="cinfo">
            <view class="cname">{{ c.name }}</view>
            <view class="csub">
              <text class="cwr" :class="{ low: c.wr < 0.45 }">{{ fmtPct(c.wr) }}</text>
              <text class="cnum">{{ c.games }}场</text>
            </view>
          </view>
        </view>
        <view class="caugs">
          <aug-chip v-for="b in c.best3 || []" :key="b.name" :name="b.name" :quality="b.quality" :icon="b.icon" size="sm" />
        </view>
      </view>
      <view v-if="!loaded" class="empty">加载中…</view>
    </view>
    <view v-else class="empty">请点击上方选择一个英雄分支</view>

    <site-foot />
    <aug-desc-modal />
  </view>
</template>

<script>
import { state, AV_FALLBACK } from '../../store'
import { getJSON } from '../../api'
import { CAT_IDS, CAT_META, CATS, fmtPct } from '../../data'

export default {
  data() {
    return {
      state,
      cats: CATS,
      CAT_IDS,
      champs: [],
      loaded: false,
      errs: {},
    }
  },
  computed: {
    meta() { return CAT_META[state.cat] || {} },
    list() {
      const ids = new Set(CAT_IDS[state.cat] || [])
      return this.champs.filter(c => ids.has(c.id)).slice().sort((a, b) => (b.wilson || 0) - (a.wilson || 0))
    },
  },
  onLoad() { this.load() },
  methods: {
    fmtPct,
    async load() {
      try { this.champs = await getJSON('/api/champions') || [] }
      catch (e) { uni.showToast({ title: '网络异常，请稍后重试', icon: 'none' }) }
      this.loaded = true
    },
    pick(c) { state.cat = c },
    medal(i) { return i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : (i + 1) },
    goChamp(id) { uni.navigateTo({ url: '/pages/champ/champ?id=' + id }) },
    imgOf(c) { return this.errs[c.id] ? AV_FALLBACK : c.image },
    imgErr(c) { this.errs = { ...this.errs, [c.id]: true } },
  },
}
</script>

<style>
.catpick { display: flex; flex-wrap: wrap; gap: 16rpx; margin-bottom: 24rpx; }
.catcard {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 14rpx 20rpx;
  border-radius: 20rpx;
  background: var(--panel2);
  border: 1rpx solid var(--line);
}
.catcard.on { border-color: var(--blue); background: rgba(74, 168, 255, 0.12); }
.ccname { font-size: 32rpx; font-weight: 600; }
.ccnum { color: var(--sub); font-size: 26rpx; }

.cathead { padding: 28rpx 32rpx; margin-bottom: 24rpx; }
.catttl { font-size: 44rpx; font-weight: 700; }
.capsub { color: var(--sub); font-size: 28rpx; margin-top: 6rpx; }

.catgrid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20rpx; }
.catcard2 {
  position: relative;
  background: var(--panel);
  border: 1rpx solid var(--line);
  border-radius: 28rpx;
  padding: 24rpx 20rpx;
  box-shadow: 0 12rpx 36rpx rgba(60, 90, 150, 0.08);
}
.crank { position: absolute; top: 14rpx; right: 18rpx; font-size: 34rpx; }
.crow { display: flex; align-items: center; gap: 16rpx; margin-top: 10rpx; }
.cavatar { width: 88rpx; height: 88rpx; border-radius: 24rpx; flex: none; }
.cinfo { min-width: 0; }
.cname { font-size: 32rpx; font-weight: 700; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.csub { margin-top: 4rpx; display: flex; align-items: baseline; gap: 10rpx; flex-wrap: wrap; }
.cwr { font-size: 40rpx; font-weight: 800; color: var(--green); }
.cwr.low { color: var(--red); }
.cnum { font-size: 24rpx; color: var(--sub); }
.caugs { display: flex; flex-direction: column; align-items: flex-start; gap: 10rpx; margin-top: 16rpx; }
</style>
