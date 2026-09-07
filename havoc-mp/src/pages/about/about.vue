<template>
  <view class="pagebox">
    <view class="panel sec">
      <view class="about-t">关于本站</view>
      <text class="about-p">「海克斯大乱斗攻略站」是一个基于国服真实对局数据统计的英雄攻略查询工具：提供英雄胜率排行、最优符文/符文组合/搭配增益/核心出装/克制推荐。核心判定标准 = 真实对局胜率。</text>
      <text class="about-p">本站为<text class="b">非商业性</text>的个人学习/分享站点；英雄联盟及英雄、符文、装备等权利归 <text class="b">Riot Games</text> 所有，数据仅供学习交流，不用于任何商业用途。部分图片来自网络，版权归原作者所有，如涉及版权问题请联系删除。</text>
      <text class="about-p">联系邮箱：19162860223@163.com</text>
      <view class="beian" v-if="icp || police">
        <text v-if="icp">{{ icp }}</text>
        <text v-if="icp && police">　|　</text>
        <text v-if="police">{{ police }}</text>
      </view>
      <view class="beian" v-if="ver">数据游戏版本：{{ ver }}</view>
    </view>

    <view class="panel sec">
      <view class="about-t">用户协议（摘要）</view>
      <text class="about-p">1. 本小程序免费提供游戏数据查询服务，数据来自公开对局统计，仅供学习交流，不构成任何游戏内决策的承诺。</text>
      <text class="about-p">2. 用户发表评论须遵守法律法规；评论区设有敏感词过滤与人工管理，违规内容将被删除。</text>
      <text class="about-p">3. 请勿上传或发布侵犯他人权益（含 Riot Games 相关权利）的内容。</text>
    </view>

    <view class="panel sec">
      <view class="about-t">隐私政策（摘要）</view>
      <text class="about-p">1. 本小程序仅在注册/登录时收集：邮箱（登录凭证）、昵称、头像、绑定手机号（可选），用于账号体系与评论展示。</text>
      <text class="about-p">2. 上述信息仅存储于本站服务器，不会出售或提供给第三方。</text>
      <text class="about-p">3. 如需注销账号或删除数据，请通过联系邮箱申请，我们将在核实后处理。</text>
    </view>

    <site-foot />
  </view>
</template>

<script>
import { getJSON } from '../../api'

export default {
  data() { return { ver: '', icp: '', police: '' } },
  onLoad() {
    getJSON('/api/site').then(d => {
      if (d) { if (d.game_version) this.ver = d.game_version; if (d.icp) this.icp = d.icp; if (d.police) this.police = d.police }
    }).catch(() => {})
  },
}
</script>

<style>
.sec { padding: 32rpx; margin-bottom: 24rpx; }
.about-t { font-size: 36rpx; font-weight: 700; color: var(--gold); margin-bottom: 16rpx; }
.about-p { display: block; font-size: 30rpx; line-height: 1.7; color: var(--txt); margin-bottom: 12rpx; }
.b { font-weight: 700; }
.beian { text-align: center; margin-top: 16rpx; font-size: 28rpx; color: var(--sub); }
</style>
