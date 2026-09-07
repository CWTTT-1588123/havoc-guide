<template>
  <view class="itemrow">
    <view class="l">
      <aug-chip :name="s.aname" :quality="s.aquality" :icon="s.aicon" size="lg" />
      <text class="plus">+</text>
      <aug-chip :name="s.bname" :quality="s.bquality" :icon="s.bicon" size="lg" />
    </view>
    <view class="r">
      <text class="winrate" :class="{ low: s.wr < 0.45 }">{{ pct }}</text>
      <text class="pct">{{ lift }}</text>
    </view>
  </view>
</template>

<script>
import { fmtPct, fmtLift } from '../../data'

export default {
  name: 'SynergyRow',
  props: { s: { type: Object, default: () => ({}) } },
  computed: {
    pct() { return fmtPct(this.s.wr) },
    lift() { return fmtLift(this.s.lift) },
  },
}
</script>

<style>
.itemrow {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24rpx;
  padding: 20rpx 24rpx;
  background: rgba(255, 255, 255, 0.48);
  border: 1rpx solid rgba(70, 90, 150, 0.22);
  border-radius: 24rpx;
}
.itemrow .l { display: flex; gap: 16rpx; flex-wrap: wrap; align-items: center; flex: 1; min-width: 0; }
.itemrow .r { display: flex; gap: 20rpx; align-items: center; white-space: nowrap; flex: none; }
.itemrow .winrate { font-size: 34rpx; color: #12a556; font-weight: 700; }
.itemrow .winrate.low { color: #9e1010; }
.itemrow .plus { color: #38435e; font-size: 36rpx; }
.itemrow .pct { color: #38435e; font-size: 30rpx; }
</style>
