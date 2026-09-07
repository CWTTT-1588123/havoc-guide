<template>
  <view class="itemrow">
    <view class="l">
      <aug-chip v-for="(n, i) in b.item_names" :key="i" :name="n" :icon="(b.item_icons || [])[i]" :tappable="false" size="lg" />
      <text class="num">{{ b.games }}场</text>
    </view>
    <text class="winrate" :class="{ low: b.wr < 0.45 }">{{ pct }}</text>
  </view>
</template>

<script>
import { fmtPct } from '../../data'

export default {
  name: 'BuildRow',
  props: { b: { type: Object, default: () => ({}) } },
  computed: { pct() { return fmtPct(this.b.wr) } },
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
.itemrow .winrate { font-size: 34rpx; color: #12a556; font-weight: 700; flex: none; }
.itemrow .winrate.low { color: #9e1010; }
.itemrow .num { font-size: 30rpx; color: #111; font-weight: 700; }
</style>
