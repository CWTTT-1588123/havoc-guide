<template>
  <view class="aug-chip" :class="[icon ? 'hasicon' : 'plain', 'sz-' + size]" @tap.stop="tap">
    <image v-if="icon && !iconErr" class="aicon" :src="icon" mode="aspectFill" @error="iconErr = true" />
    <view v-else class="aicon ph">✦</view>
    <text class="cname">{{ name }}</text>
    <text v-if="quality" class="q qdark" :class="quality">{{ quality }}</text>
  </view>
</template>

<script>
import { openAugDesc } from '../../store'
import { getAugDesc } from '../../api'

export default {
  name: 'AugChip',
  props: {
    name: { type: String, default: '' },
    quality: { type: String, default: '' },
    icon: { type: String, default: '' },
    size: { type: String, default: 'sm' },   // sm=榜单/分类  lg=详情行
    tappable: { type: Boolean, default: true },
  },
  data() { return { iconErr: false } },
  methods: {
    tap() {
      if (!this.tappable) return
      openAugDesc({ name: this.name, quality: this.quality, icon: this.icon, desc: getAugDesc(this.name) })
    },
  },
}
</script>

<style>
/* 注意：小程序自定义组件样式隔离，app.wxss 的变量/类不会作用到组件内 —— 颜色在此硬编码 */
.aug-chip {
  display: inline-flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.48);
  border: 1rpx solid rgba(70, 90, 150, 0.22);
  padding: 6rpx 20rpx;
  border-radius: 28rpx;
  color: #141a26;
}
.aug-chip.hasicon { background: linear-gradient(160deg, #161d33, #10142a); border-color: rgba(100, 120, 200, 0.35); color: #dfe6f5; }
.aicon { width: 44rpx; height: 44rpx; border-radius: 10rpx; margin-right: 10rpx; flex: none; }
.aicon.ph { display: inline-flex; align-items: center; justify-content: center; border: 1rpx dashed rgba(126, 148, 210, 0.45); background: rgba(255, 255, 255, 0.04); color: rgba(170, 185, 230, 0.6); font-size: 22rpx; }
.cname { font-size: 28rpx; }
.sz-lg { padding: 10rpx 24rpx; border-radius: 26rpx; }
.sz-lg .cname { font-size: 40rpx; }
.sz-lg .aicon { width: 56rpx; height: 56rpx; margin-right: 14rpx; border-radius: 12rpx; }
.sz-lg .q { font-size: 30rpx; line-height: 44rpx; }

/* 品质小字（深色容器内配色） */
.q { display: inline-block; margin-left: 12rpx; padding: 0 14rpx; font-size: 28rpx; line-height: 40rpx; border-radius: 12rpx; border: 1rpx solid; }
.q.白银 { color: #cdd6e4; border-color: #3a4252; background: #2b3240; }
.q.黄金 { color: #e6c24a; border-color: #6a5a20; background: #3a3018; }
.q.棱彩 { color: #d9a8ff; border-color: #6a3a8a; background: #3a2650; }
</style>
