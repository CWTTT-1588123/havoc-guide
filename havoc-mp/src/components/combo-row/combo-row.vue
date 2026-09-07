<template>
  <view class="itemrow">
    <view class="l">
      <aug-chip v-for="(m, i) in c.augment_meta" :key="i" :name="m.name" :quality="m.quality" :icon="m.icon" size="lg" />
    </view>
    <view class="r">
      <text class="winrate" :class="{ low: c.wr < 0.45 }">{{ pct }}</text>
      <text class="num">{{ c.games }}场</text>
    </view>
  </view>
</template>

<script>
import { fmtPct } from '../../data'

export default {
  name: 'ComboRow',
  props: { c: { type: Object, default: () => ({}) } },
  computed: { pct() { return fmtPct(this.c.wr) } },
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
.itemrow .num { font-size: 30rpx; color: #111; font-weight: 700; }
</style>
