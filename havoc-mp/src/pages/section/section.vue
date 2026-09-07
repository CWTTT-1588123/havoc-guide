<template>
  <view class="pagebox" v-if="d">
    <view class="detail">
      <view class="dhead">
        <image class="dimg" :src="imgFailed ? AV_FALLBACK : d.image" mode="aspectFill" @error="onImgErr" />
        <view>
          <view class="dtitle">{{ d.name }}</view>
          <view class="dsub">{{ title }} · 共 {{ count }} 条</view>
        </view>
      </view>

      <view class="sec">
        <view class="sechead"><text>{{ title }}</text></view>
        <view class="cap">{{ cap }}</view>

        <view v-if="key === 'augments'" class="aqblockwrap">
          <view v-for="(g, gi) in d.augments_by_quality" :key="gi" class="aqblock">
            <view class="cq">{{ g.quality }}</view>
            <view class="aqgrid">
              <single-card v-for="(a, ai) in g.items" :key="ai" :item="a" :index="ai" />
            </view>
          </view>
        </view>
        <view v-else-if="key === 'combos'" class="list">
          <combo-row v-for="(c, i) in d.combos" :key="i" :c="c" />
        </view>
        <view v-else-if="key === 'synergy'" class="list">
          <synergy-row v-for="(x, i) in d.synergy" :key="i" :s="x" />
        </view>
        <view v-else-if="key === 'builds'" class="list">
          <build-row v-for="(x, i) in d.builds" :key="i" :b="x" />
        </view>
        <view v-else-if="key === 'counters'" class="list">
          <counter-row v-for="(x, i) in d.counters" :key="i" :s="x" />
        </view>
      </view>
    </view>

    <site-foot />
    <aug-desc-modal />
  </view>

  <view v-else class="pagebox"><view class="empty">加载中…</view></view>
</template>

<script>
import { state, AV_FALLBACK, toast } from '../../store'
import { getJSON } from '../../api'

const TITLES = { augments: '最优单个符文', combos: '最优符文组合', synergy: '搭配增益', builds: '核心出装', counters: '克制推荐' }
const CAPS = {
  augments: '该英雄带这个符文胜率最高（按品质分档）',
  combos: '这几个符文一起带的胜率',
  synergy: '这两个符文一起带，胜率比该英雄平均▲高/▼低',
  builds: '该英雄这流派常见的核心三件套',
  counters: '敌方是这类阵容时，选这个符文克制（▲ 克制加成 / ▼ 反被压制）',
}

export default {
  data() {
    return {
      cid: '',
      key: '',
      d: null,
      imgFailed: false,
    }
  },
  computed: {
    title() { return TITLES[this.key] || '更多内容' },
    cap() { return CAPS[this.key] || '' },
    count() {
      if (!this.d) return 0
      const x = this.d
      if (this.key === 'augments') return (x.augments_by_quality || []).reduce((n, g) => n + (g.items || []).length, 0)
      return (x[this.key] || []).length
    },
  },
  onLoad(options) {
    this.cid = (options && options.cid) || state.section.cid || ''
    this.key = (options && options.key) || state.section.key || ''
    this.load()
  },
  methods: {
    onImgErr() { this.imgFailed = true },
    async load() {
      try {
        this.d = await getJSON('/api/champion/' + this.cid)
        uni.setNavigationBarTitle({ title: (this.d.name || '') + ' · ' + this.title })
      } catch (e) { toast('网络异常，请稍后重试') }
    },
  },
}
</script>

<style>
.aqblock { margin-bottom: 28rpx; }
.aqblock:last-child { margin-bottom: 0; }
.cq { color: var(--gold); font-size: 34rpx; font-weight: 600; margin-bottom: 20rpx; }
.aqgrid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20rpx; }
.list { display: flex; flex-direction: column; gap: 20rpx; }
</style>
