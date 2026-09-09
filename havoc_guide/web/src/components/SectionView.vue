<script setup>
import { ref, computed, onMounted } from 'vue'
import { state, getJSON, goHome } from '../store'
import { avErr } from '../data'

const cid = computed(() => state.section.cid)
const key = computed(() => state.section.key)
const d = ref(null)

const TITLES = { augments:'最优单个符文', combos:'最优符文组合', synergy:'搭配增益', builds:'核心出装', counters:'克制推荐' }
const CAPS = { augments:'该英雄带这个符文胜率最高（按品质分档）', combos:'这三个符文一起带的胜率，比该英雄平均▲高/▼低', synergy:'这两个符文一起带，胜率比该英雄平均▲高/▼低', builds:'该英雄这流派常见的核心三件套', counters:'敌方是这类阵容时，选这个符文克制（▲ 克制加成 / ▼ 反被压制）' }

function esc(x) { return String(x ?? '').replace(/[&<>"]/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;' }[c])) }
function augChip(name, q, icon) { return `<span class="aug-chip hasicon" data-name="${esc(name)}">${icon ? `<img class="aicon" src="${icon}" onerror="this.style.display='none'">` : '<span class="aicon ph"></span>'}${esc(name)}${q ? `<span class="q ${esc(q)}">${esc(q)}</span>` : ''}</span>` }
function itemCard(name, icon) { return `<span class="aug-chip hasicon" data-name="${esc(name)}">${icon ? `<img class="aicon" src="${icon}" onerror="this.style.display='none'">` : '<span class="aicon ph"></span>'}${esc(name)}</span>` }
function singleRow(a, i) { const rk = (i ?? 0) + 1; return `<div class="singlecard hasicon" data-name="${esc(a.name)}"><span class="srank${rk <= 3 ? ' sr' + rk : ''}">${rk}</span>${a.icon ? `<img class="sicon" src="${a.icon}" onerror="this.style.display='none'">` : '<span class="sicon ph"></span>'}<div class="sname">${esc(a.name)}${a.quality ? `<span class="q ${esc(a.quality)}">${esc(a.quality)}</span>` : ''}</div><div class="swr">${(a.wr * 100).toFixed(1)}%</div><div class="snum">${a.games}场</div></div>` }
function comboRow(c, base) { const pct = c.est ?? c.wilson ?? c.wr; const diff = pct - (base ?? pct); return `<div class="itemrow"><div class="l">${(c.augment_meta || []).map(m => augChip(m.name, m.quality, m.icon)).join('')} <span class="num num-desk">${c.games}场</span></div><div class="r"><span class="winrate">${(pct * 100).toFixed(1)}%</span> <span class="pct">${diff >= 0 ? '▲' : '▼'}${Math.abs(diff * 100).toFixed(1)}%</span> <span class="num num-mob">${c.games}场</span></div></div>` }
function synergyRow(s) { return `<div class="itemrow"><div class="l">${augChip(s.aname, s.aquality, s.aicon)}+${augChip(s.bname, s.bquality, s.bicon)} <span class="num">${s.games}场</span></div><div class="r"><span class="winrate">${(s.wr * 100).toFixed(1)}%</span> <span class="pct">${s.lift > 0 ? '▲' : '▼'}${Math.abs(s.lift * 100).toFixed(1)}%</span></div></div>` }
function buildRow(b) { return `<div class="itemrow"><div class="l">${(b.item_names || []).map((x, i) => itemCard(x, (b.item_icons || [])[i])).join('')} <span class="num">${b.games}场</span></div><span class="winrate">${(b.wr * 100).toFixed(1)}%</span></div>` }
function counterRow(s) { return `<div class="itemrow ctr"><div class="l"><span class="tag">${esc(s.tag)}</span><div class="ctrline">${augChip(s.augment_name, s.augment_quality, s.icon)} <span class="num">${s.games}场</span></div></div><span class="pct">${s.lift > 0 ? '▲' : '▼'} ${Math.abs(s.lift * 100).toFixed(1)}%</span></div>` }
function qualityBlocks(dd) { return `<div class="aqgrid">${(dd.augments_by_quality || []).map(g => `<div class="aqcol"><div class="cq">${esc(g.quality)}</div><div class="list">${g.items.map(singleRow).join('')}</div></div>`).join('')}</div>` }

const body = computed(() => {
  if (!d.value) return ''
  const x = d.value
  const k = key.value
  if (k === 'augments') return qualityBlocks(x)
  if (k === 'combos') return `<div class="list">${x.combos.map(c => comboRow(c, x.overall && x.overall.wr)).join('')}</div>`
  if (k === 'synergy') return `<div class="list">${x.synergy.map(synergyRow).join('')}</div>`
  if (k === 'builds') return `<div class="list">${x.builds.map(buildRow).join('')}</div>`
  if (k === 'counters') return `<div class="list">${x.counters.map(counterRow).join('')}</div>`
  return ''
})
const count = computed(() => {
  if (!d.value) return 0
  const x = d.value, k = key.value
  if (k === 'augments') return (x.augments_by_quality || []).reduce((n, g) => n + (g.items || []).length, 0)
  return (x[k] || []).length
})
function back() { state.view = 'champ' }

onMounted(async () => { d.value = await getJSON('/api/champion/' + cid.value) })
</script>

<template>
  <div v-if="d">
    <div class="toolbar">
      <button class="btn" @click="back">返回</button>
      <span class="pc-hello">{{ d.name }} · {{ TITLES[key] || '更多内容' }} · 共 {{ count }} 条</span>
    </div>
    <div class="detail">
      <div class="dhead">
        <img class="dimg" :src="d.image" @error="avErr($event, d.name)" alt="">
        <div><h2>{{ d.name }}</h2><div class="sub">{{ TITLES[key] || '更多内容' }} · 共 {{ count }} 条</div></div>
      </div>
      <div class="sec">
        <h3 class="sechead"><span>{{ TITLES[key] || '更多内容' }}</span></h3>
        <div class="cap">{{ CAPS[key] }}</div>
        <div v-html="body"></div>
      </div>
    </div>
  </div>
</template>
