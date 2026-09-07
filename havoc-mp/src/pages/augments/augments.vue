<template>
  <view class="pagebox">
    <view class="detail">
      <view class="dhead">
        <view>
          <view class="dtitle">所有符文</view>
          <view class="dsub">点击品质标题展开该品质全部符文 · 共 {{ total }} 个 · 点击符文卡查看效果说明</view>
        </view>
      </view>

      <view class="qlist">
        <view v-for="(g, i) in qualityItems" :key="g.quality" class="qblock">
          <view class="qhead" :class="{ open: open[g.quality] }" @tap="toggle(g.quality)">
            <text class="qttl">{{ g.quality }} <text class="qnum">{{ (g.items || []).length }}个</text></text>
            <text class="qchev">▼</text>
          </view>
          <view v-if="open[g.quality]" class="augwrap">
            <view class="auggrid">
              <view v-for="(a, j) in g.items || []" :key="j" class="augcard" @tap="showDesc(a)">
                <image v-if="a.icon && !errs[a.name]" class="sicon" :src="a.icon" mode="aspectFill" @error="imgErr(a)" />
                <view v-else class="sicon ph">✦</view>
                <view class="sname">
                  <text class="sn">{{ a.name }}</text>
                  <text v-if="a.quality" class="q qdark" :class="a.quality">{{ a.quality }}</text>
                </view>
                <view class="sdesc">{{ a.desc || '（暂无描述）' }}</view>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <site-foot />
    <aug-desc-modal />
  </view>
</template>

<script>
import { getJSON } from '../../api'
import { openAugDesc } from '../../store'

export default {
  data() {
    return {
      groups: [],
      open: { 白银: true },
      errs: {},
    }
  },
  computed: {
    total() { return this.groups.reduce((n, g) => n + (g.items || []).length, 0) },
    qualityItems() {
      return ['白银', '黄金', '棱彩'].map(q => this.groups.find(x => x.quality === q)).filter(Boolean)
    },
  },
  onLoad() { this.load() },
  methods: {
    async load() {
      try { this.groups = await getJSON('/api/augments_all') || [] }
      catch (e) { uni.showToast({ title: '网络异常，请稍后重试', icon: 'none' }) }
    },
    toggle(q) { this.open[q] = !this.open[q] },
    showDesc(a) { openAugDesc({ name: a.name, quality: a.quality, icon: a.icon, desc: a.desc || '' }) },
    imgErr(a) { this.errs = { ...this.errs, [a.name]: true } },
  },
}
</script>

<style>
.dtitle { font-size: 48rpx; font-weight: 700; }
.dsub { color: var(--sub); font-size: 30rpx; margin-top: 4rpx; }

.qlist { display: flex; flex-direction: column; gap: 24rpx; }
.qblock { border: 1rpx solid rgba(120, 140, 200, 0.28); border-radius: 24rpx; overflow: hidden; }
.qhead {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4rpx;
  height: 100rpx;
  background: rgba(255, 255, 255, 0.42);
  border-bottom: 1rpx solid rgba(120, 140, 200, 0.28);
}
.qttl { font-size: 38rpx; color: var(--gold); font-weight: 700; }
.qnum { font-size: 32rpx; color: var(--sub); margin-left: 16rpx; font-weight: 600; }
.qchev { font-size: 30rpx; color: var(--blue); }
.qhead.open .qchev { transform: rotate(180deg); }

.augwrap { padding: 20rpx; }
.auggrid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20rpx; }
.augcard {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  padding: 24rpx 16rpx;
  min-height: 340rpx;
  background: linear-gradient(160deg, #161d33, #10142a);
  border: 1rpx solid rgba(100, 120, 200, 0.35);
  border-radius: 32rpx;
  text-align: center;
  box-shadow: 0 8rpx 28rpx rgba(30, 45, 95, 0.25);
}
.sicon { width: 128rpx; height: 128rpx; border-radius: 24rpx; }
.sicon.ph { display: flex; align-items: center; justify-content: center; border: 1rpx dashed rgba(126, 148, 210, 0.45); background: rgba(255, 255, 255, 0.04); color: rgba(170, 185, 230, 0.6); font-size: 44rpx; }
.sname { display: flex; flex-direction: column; align-items: center; gap: 6rpx; }
.sn { font-size: 32rpx; font-weight: 600; color: #f2f5fc; }
.sname .q { margin-left: 0; font-size: 26rpx; line-height: 36rpx; }
.sdesc {
  font-size: 28rpx;
  color: #c3cde6;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-all;
}
</style>
