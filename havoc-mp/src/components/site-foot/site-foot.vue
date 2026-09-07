<template>
  <view class="site-foot">
    <text class="p">本站为<text class="b">非商业性</text>的个人学习/分享站点；英雄联盟及英雄、符文、装备等权利归 <text class="b">Riot Games</text> 所有，数据仅供学习交流，不用于任何商业用途。</text>
    <text class="p">部分图片来自网络，版权归原作者所有。如涉及版权问题，请联系删除。</text>
    <text class="p">联系邮箱：19162860223@163.com</text>
    <view class="beian" v-if="icp || police">
      <text v-if="icp">{{ icp }}</text>
      <text v-if="icp && police">　|　</text>
      <text v-if="police">{{ police }}</text>
    </view>
    <view class="beian" v-if="ver">游戏版本 {{ ver }}</view>
    <view class="aboutlink" @tap="goAbout">关于本站 · 用户协议 · 隐私政策 ›</view>
  </view>
</template>

<script>
import { getJSON } from '../../api'

export default {
  name: 'SiteFoot',
  data() { return { ver: '', icp: '', police: '' } },
  mounted() {
    getJSON('/api/site').then(d => {
      if (d) { if (d.game_version) this.ver = d.game_version; if (d.icp) this.icp = d.icp; if (d.police) this.police = d.police }
    }).catch(() => {})
  },
  methods: {
    goAbout() { uni.navigateTo({ url: '/pages/about/about' }) },
  },
}
</script>

<style>
.site-foot { color: #38435e; font-size: 26rpx; line-height: 1.7; padding: 24rpx 20rpx 60rpx; }
.p { display: block; margin: 8rpx 0; }
.b { color: #141a26; font-weight: 700; }
.beian { text-align: center; margin-top: 12rpx; }
.aboutlink { text-align: center; margin-top: 20rpx; color: #3b8fe0; }
</style>
