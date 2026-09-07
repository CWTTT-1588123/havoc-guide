<template>
  <view class="singlecard hasicon" @tap.stop="tap">
    <view class="srank" :class="rkClass">{{ index + 1 }}</view>
    <image v-if="item.icon && !iconErr" class="sicon" :src="item.icon" mode="aspectFill" @error="iconErr = true" />
    <view v-else class="sicon ph">✦</view>
    <view class="sname">
      <text class="sn">{{ item.name }}</text>
      <text v-if="item.quality" class="q qdark" :class="item.quality">{{ item.quality }}</text>
    </view>
    <text class="swr">{{ pct }}</text>
    <text class="snum">{{ item.games }}场</text>
  </view>
</template>

<script>
import { openAugDesc } from '../../store'
import { getAugDesc } from '../../api'
import { fmtPct } from '../../data'

export default {
  name: 'SingleCard',
  props: {
    item: { type: Object, default: () => ({}) },
    index: { type: Number, default: 0 },
  },
  data() { return { iconErr: false } },
  computed: {
    pct() { return fmtPct(this.item.wr) },
    rkClass() { return this.index < 3 ? 'sr' + (this.index + 1) : '' },
  },
  methods: {
    tap() {
      openAugDesc({ name: this.item.name, quality: this.item.quality, icon: this.item.icon, desc: getAugDesc(this.item.name) })
    },
  },
}
</script>

<style>
/* 手机版"扑克牌"卡：两列网格用，排名序号 1金2银3铜 */
.singlecard {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 28rpx 12rpx 18rpx;
  min-height: 340rpx;
  border-radius: 32rpx;
  text-align: center;
}
.singlecard.hasicon {
  background: linear-gradient(160deg, #161d33, #10142a);
  border: 1rpx solid rgba(100, 120, 200, 0.35);
  box-shadow: 0 8rpx 28rpx rgba(30, 45, 95, 0.25);
}
.srank {
  position: absolute;
  top: 12rpx;
  left: 12rpx;
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 800;
  color: #dfe6f5;
  background: rgba(30, 38, 60, 0.85);
  border: 1rpx solid rgba(120, 140, 210, 0.4);
}
.srank.sr1 { color: #5a3c00; background: linear-gradient(160deg, #ffe9a8, #f5c84c); border-color: #d9a819; }
.srank.sr2 { color: #3a3f47; background: linear-gradient(160deg, #eef1f6, #c8d2e0); border-color: #9fb0c8; }
.srank.sr3 { color: #6a3a1a; background: linear-gradient(160deg, #f0cfa8, #d9955a); border-color: #b06a2e; }
.sicon { width: 128rpx; height: 128rpx; border-radius: 24rpx; margin-top: 30rpx; }
.sicon.ph { display: inline-flex; align-items: center; justify-content: center; border: 1rpx dashed rgba(126, 148, 210, 0.45); background: rgba(255, 255, 255, 0.04); color: rgba(170, 185, 230, 0.6); font-size: 44rpx; }
.sname { display: flex; flex-direction: column; align-items: center; gap: 6rpx; }
.sn { font-size: 32rpx; font-weight: 600; color: #f2f5fc; }
.q { display: inline-block; margin-left: 0; padding: 0 14rpx; font-size: 26rpx; line-height: 36rpx; border-radius: 12rpx; border: 1rpx solid; }
.q.白银 { color: #cdd6e4; border-color: #3a4252; background: #2b3240; }
.q.黄金 { color: #e6c24a; border-color: #6a5a20; background: #3a3018; }
.q.棱彩 { color: #d9a8ff; border-color: #6a3a8a; background: #3a2650; }
.swr { font-size: 42rpx; color: #5bd08b; font-weight: 800; }
.snum { font-size: 30rpx; color: #e8edf8; font-weight: 700; }
</style>
