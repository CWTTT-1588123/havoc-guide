<template>
  <view v-if="state.augDesc" class="ttov" @tap="close">
    <view class="ttcard" @tap.stop>
      <image v-if="state.augDesc.icon" class="tm-icon" :src="state.augDesc.icon" mode="aspectFill" />
      <view v-else class="tm-icon ph">✦</view>
      <view class="tm-name">
        <text>{{ state.augDesc.name }}</text>
        <text v-if="state.augDesc.quality" class="q qdark" :class="state.augDesc.quality">{{ state.augDesc.quality }}</text>
      </view>
      <view class="tm-desc">{{ state.augDesc.desc || '（暂无描述）' }}</view>
      <view class="tm-hint">点击空白处关闭</view>
    </view>
  </view>
</template>

<script>
import { state, closeAugDesc } from '../../store'

export default {
  name: 'AugDescModal',
  data() { return { state } },
  methods: { close: closeAugDesc },
}
</script>

<style>
.ttov {
  position: fixed;
  left: 0; top: 0; right: 0; bottom: 0;
  z-index: 100300;
  background: rgba(8, 12, 22, 0.62);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 36rpx;
}
.ttcard {
  width: 92%;
  max-width: 640rpx;
  max-height: 82%;
  overflow: auto;
  background: linear-gradient(160deg, #161d33, #10142a);
  border: 1rpx solid rgba(120, 150, 220, 0.42);
  border-radius: 32rpx;
  padding: 36rpx 32rpx;
  box-shadow: 0 40rpx 120rpx rgba(0, 0, 0, 0.45);
}
.tm-icon { width: 120rpx; height: 120rpx; border-radius: 24rpx; display: block; margin: 0 auto 24rpx; }
.tm-icon.ph { display: flex; align-items: center; justify-content: center; border: 1rpx dashed rgba(126, 148, 210, 0.45); color: rgba(170, 185, 230, 0.7); font-size: 60rpx; }
.tm-name { text-align: center; font-size: 44rpx; font-weight: 700; color: #f2f5fc; display: flex; align-items: center; justify-content: center; gap: 16rpx; flex-wrap: wrap; }
.q { display: inline-block; margin-left: 12rpx; padding: 0 14rpx; font-size: 28rpx; line-height: 40rpx; border-radius: 12rpx; border: 1rpx solid; }
.q.白银 { color: #cdd6e4; border-color: #3a4252; background: #2b3240; }
.q.黄金 { color: #e6c24a; border-color: #6a5a20; background: #3a3018; }
.q.棱彩 { color: #d9a8ff; border-color: #6a3a8a; background: #3a2650; }
.tm-desc { margin-top: 20rpx; font-size: 32rpx; line-height: 1.6; color: #cfd9f0; }
.tm-hint { margin-top: 24rpx; text-align: center; font-size: 26rpx; color: rgba(170, 185, 230, 0.55); }
</style>
