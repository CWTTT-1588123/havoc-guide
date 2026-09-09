<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { state, getJSON, openLogin, goHome, toast } from '../store'
import { avErr } from '../data'

const cid = computed(() => state.champId)
const d = ref(null)
const comments = ref([])
const commentText = ref('')

function esc(s) { return String(s ?? '').replace(/[&<>"]/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;' }[c])) }

function augChip(name, q, icon) {
  return `<span class="aug-chip hasicon" data-name="${esc(name)}">${icon ? `<img class="aicon" src="${icon}" onerror="this.style.display='none'">` : '<span class="aicon ph"></span>'}${esc(name)}${q ? `<span class="q ${esc(q)}">${esc(q)}</span>` : ''}</span>`
}
function itemCard(name, icon) {
  return `<span class="aug-chip hasicon" data-name="${esc(name)}">${icon ? `<img class="aicon" src="${icon}" onerror="this.style.display='none'">` : '<span class="aicon ph"></span>'}${esc(name)}</span>`
}
function singleRow(a, i) {
  const rk = (i ?? 0) + 1
  return `<div class="singlecard hasicon" data-name="${esc(a.name)}"><span class="srank${rk <= 3 ? ' sr' + rk : ''}">${rk}</span>${a.icon ? `<img class="sicon" src="${a.icon}" onerror="this.style.display='none'">` : '<span class="sicon ph"></span>'}<div class="sname">${esc(a.name)}${a.quality ? `<span class="q ${esc(a.quality)}">${esc(a.quality)}</span>` : ''}</div><div class="swr">${(a.wr * 100).toFixed(1)}%</div><div class="snum">${a.games}场</div></div>`
}
function comboRow(c, base) {
  const pct = c.est ?? c.wilson ?? c.wr
  const diff = pct - (base ?? pct)
  return `<div class="itemrow"><div class="l">${(c.augment_meta || []).map(m => augChip(m.name, m.quality, m.icon)).join('')} <span class="num num-desk">${c.games}场</span></div><div class="r"><span class="winrate">${(pct * 100).toFixed(1)}%</span> <span class="pct">${diff >= 0 ? '▲' : '▼'}${Math.abs(diff * 100).toFixed(1)}%</span> <span class="num num-mob">${c.games}场</span></div></div>`
}
function synergyRow(s) {
  return `<div class="itemrow"><div class="l">${augChip(s.aname, s.aquality, s.aicon)}+${augChip(s.bname, s.bquality, s.bicon)} <span class="num">${s.games}场</span></div><div class="r"><span class="winrate">${(s.wr * 100).toFixed(1)}%</span> <span class="pct">${s.lift > 0 ? '▲' : '▼'}${Math.abs(s.lift * 100).toFixed(1)}%</span></div></div>`
}
function buildRow(b) {
  return `<div class="itemrow"><div class="l">${(b.item_names || []).map((x, i) => itemCard(x, (b.item_icons || [])[i])).join('')} <span class="num">${b.games}场</span></div><span class="winrate">${(b.wr * 100).toFixed(1)}%</span></div>`
}
function counterRow(s) {
  return `<div class="itemrow ctr"><div class="l"><span class="tag">${esc(s.tag)}</span><div class="ctrline">${augChip(s.augment_name, s.augment_quality, s.icon)} <span class="num">${s.games}场</span></div></div><span class="pct">${s.lift > 0 ? '▲' : '▼'} ${Math.abs(s.lift * 100).toFixed(1)}%</span></div>`
}
function qualityBlocks(dd, full) {
  return `<div class="aqgrid">${(dd.augments_by_quality || []).map(g => `<div class="aqcol"><div class="cq">${esc(g.quality)}</div><div class="list">${g.items.slice(0, full ? g.items.length : 5).map(singleRow).join('')}</div></div>`).join('')}</div>`
}
function rowsHtml(rows, limit) {
  if (!rows || !rows.length) return ''
  const first = rows.slice(0, limit || 6)
  return `<div class="list">${first.join('')}</div>`
}

const sects = computed(() => {
  if (!d.value) return []
  const x = d.value
  const out = []
  const limit = 6
  if (x.augments_by_quality && x.augments_by_quality.length) {
    out.push({ id: 'sec-augments', key: 'augments', title: '最优单个符文', caption: '该英雄带这个符文胜率最高（按品质分档）', html: qualityBlocks(x, false), hasMore: x.augments_by_quality.some(g => g.items.length > 5) })
  }
  if (x.combos && x.combos.length) {
    const rows = x.combos.map(c => comboRow(c, x.overall && x.overall.wr))
    out.push({ id: 'sec-combos', key: 'combos', title: '最优符文套路', caption: '这三个符文一起带的胜率，比该英雄平均▲高/▼低', html: rowsHtml(rows, limit), hasMore: rows.length > limit })
  }
  if (x.synergy && x.synergy.length) {
    const rows = x.synergy.map(synergyRow)
    out.push({ id: 'sec-synergy', key: 'synergy', title: '搭配增益', caption: '这两个符文一起带，胜率比该英雄平均▲高/▼低', html: rowsHtml(rows, limit), hasMore: rows.length > limit })
  }
  if (x.builds && x.builds.length) {
    const rows = x.builds.map(buildRow)
    out.push({ id: 'sec-builds', key: 'builds', title: '核心出装', caption: '该英雄这流派常见的核心三件套', html: rowsHtml(rows, limit), hasMore: rows.length > limit })
  }
  if (x.counters && x.counters.length) {
    const rows = x.counters.map(counterRow)
    out.push({ id: 'sec-counters', key: 'counters', title: '克制推荐', caption: '敌方是这类阵容时，选这个符文克制（▲ 克制加成 / ▼ 反被压制）', html: rowsHtml(rows, limit), hasMore: rows.length > limit })
  }
  return out
})
function goMore(k) { state.section = { cid: state.champId, key: k }; state.view = 'section' }

function back() { goHome() }
function jumpTo(id) { const el = document.getElementById(id); if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' }) }

async function load() {
  d.value = await getJSON('/api/champion/' + cid.value)
  await loadComments()
}
async function loadComments() {
  const r = await getJSON('/api/champion/' + cid.value + '/comments')
  comments.value = (r.comments || []).slice().reverse()
}
async function postComment() {
  const t = commentText.value.trim()
  if (!t) { toast('请输入评论内容'); return }
  const r = await fetch('/api/champion/' + cid.value + '/comments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(state.auth && state.auth.token ? { Authorization: 'Bearer ' + state.auth.token } : {}) },
    body: JSON.stringify({ text: t }),
  })
  const data = await r.json().catch(() => ({}))
  if (r.ok) { commentText.value = ''; await loadComments(); toast('评论已发布') }
  else { toast(data.error || '发送失败') }
}
function fmtTs(ts) { return new Date((ts || 0) * 1000).toLocaleString() }

onMounted(load)
</script>

<template>
  <div v-if="d" class="detail">
    <div class="toolbar">
      <button class="btn" @click="back">返回</button>
    </div>
    <div class="dhead">
      <img class="dimg" :src="d.image" @error="avErr($event, d.name)" alt="">
      <div>
        <h2>{{ d.name }}</h2>
        <div class="sub">整体胜率 <span class="bigwr">{{ (d.overall.wr * 100).toFixed(1) }}%</span> · {{ d.overall.games }} 场</div>
      </div>
    </div>
    <div v-if="sects.length" class="secnav">
      <button v-for="s in sects" :key="s.id" class="navbtn" @click="jumpTo(s.id)">{{ s.title }}</button>
    </div>

    <div v-for="s in sects" :key="s.id" :id="s.id" class="sec">
      <h3 class="sechead"><span>{{ s.title }}</span></h3>
      <div class="cap">{{ s.caption }}</div>
      <div v-html="s.html"></div>
      <div v-if="s.hasMore" class="secmore"><button class="arrow" @click="goMore(s.key)">更多 ›</button></div>
      <div class="secend"></div>
    </div>

    <!-- 评论区（每英雄各自，共享） -->
    <div class="sec" id="sec-comments">
      <h3 class="sechead"><span>评论区</span></h3>
      <div class="cap">说说你对 {{ d.name }} 符文/出装的看法</div>
      <div class="comment-box">
        <div v-if="state.auth" class="comrow">
          <input v-model="commentText" class="com-in" placeholder="写点什么吧…">
          <button class="pc-btn ok" @click="postComment">发表评论</button>
        </div>
        <div v-else class="com-login">登录后可以评论 <button class="btn" @click="openLogin">去登录</button></div>
        <div class="com-list">
          <div v-if="!comments.length" class="empty">还没有评论，来发第一条吧</div>
          <div v-for="(c, i) in comments" :key="i" class="com-item">
            <div class="com-name">{{ c.name }}</div>
            <div class="com-text">{{ c.text }}</div>
            <div class="com-time">{{ fmtTs(c.ts) }}</div>
          </div>
        </div>
      </div>
      <div class="secend"></div>
    </div>
  </div>
</template>
