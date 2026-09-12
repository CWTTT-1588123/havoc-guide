<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { state, getJSON, goHome } from '../store'

const groups = ref([])
const open = reactive({ 白银: true })   // 默认展开白银
const order = ['白银', '黄金', '棱彩']
const total = computed(() => groups.value.reduce((n, g) => n + (g.items || []).length, 0))
const qualityItems = computed(() => order.map(q => groups.value.find(x => x.quality === q)).filter(Boolean))

function back() { goHome() }
function toggle(q) { open[q] = !open[q] }
// 吸顶高度：固定为头部高度（现状即贴顶，上方展开也不留空）
const STICKY_TOP = 'calc(var(--headerh, 90px))'
function card(a) { return `<div class="augcard hasicon" data-name="${a.name}">${a.icon ? `<img class="sicon" src="${a.icon}" onerror="this.style.display='none'">` : '<span class="sicon ph"></span>'}<div class="sname">${a.name}${a.quality ? `<span class="q ${a.quality}">${a.quality}</span>` : ''}</div><div class="sdesc">${a.desc || '（暂无描述）'}</div></div>` }

onMounted(async () => { groups.value = await getJSON('/api/augments_all') })
</script>

<template>
  <div class="toolbar"><button class="btn" @click="back">返回</button></div>
  <div class="detail">
    <div class="dhead">
      <h2>所有符文</h2>
      <div class="sub">点击品质标题展开该品质全部符文 · 共 {{ total }} 个 · <b>点击任意符文卡片查看完整效果说明</b></div>
    </div>
    <div class="qlist">
      <div v-for="(g, i) in qualityItems" :key="g.quality" class="qblock">
        <div class="qhead" :class="{ open: open[g.quality] }" :style="{ '--i': i, top: STICKY_TOP }" @click="toggle(g.quality)">
          <span class="qttl">{{ g.quality }} <span class="num">{{ (g.items || []).length }}个</span></span>
          <span class="qchev">▼</span>
        </div>
        <div v-if="open[g.quality]" class="augwrap">
          <div class="auggrid"><span v-for="(a, j) in (g.items || [])" :key="j" class="augcard-wrap" v-html="card(a)"></span></div>
        </div>
      </div>
    </div>
  </div>
</template>
