<template>
  <view class="itemrow ctr">
    <view class="l">
      <view class="tag">{{ s.tag }}</view>
      <view class="ctrline">
        <aug-chip :name="s.augment_name" :quality="s.augment_quality" :icon="s.icon" size="lg" />
        <text class="num">{{ s.games }}场</text>
      </view>
    </view>
    <text class="pct">{{ lift }}</text>
  </view>
</template>

<script>
import { fmtLift } from '../../data'

export default {
  name: 'CounterRow',
  props: { s: { type: Object, default: () => ({}) } },
  computed: { lift() { return fmtLift(this.s.lift) } },
}
</script>

<style>
/* 克制推荐：手机端标签一行、符文卡一行（固定两行） */
.itemrow {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24rpx;
  padding: 20rpx 24rpx;
  background: rgba(255, 255, 255, 0.48);
  border: 1rpx solid rgba(70, 90, 150, 0.22);
  border-radius: 24rpx;
}
.itemrow .l { display: flex; flex-direction: column; align-items: flex-start; gap: 12rpx; flex: 1; min-width: 0; }
.ctrline { display: flex; align-items: center; gap: 16rpx; flex-wrap: wrap; }
.tag { background: #fdf6e0; border: 1rpx solid #e0ca86; color: #8a6d1a; padding: 6rpx 24rpx; border-radius: 24rpx; font-size: 30rpx; }
.itemrow .num { font-size: 30rpx; color: #111; font-weight: 700; }
.itemrow .pct { color: #38435e; font-size: 30rpx; flex: none; }
</style>
