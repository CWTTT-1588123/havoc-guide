<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { state, getJSON } from '../store'
import { CAT_META, CAT_IDS, avErr } from '../data'
import { NAME_NICKS } from '../nicknames'

const champs = ref([])
const sort = ref('wilson')   // 'wilson' | 'wr' | 'games'
const ascending = ref(false)
const per = ref(20)
const page = ref(1)

async function load() {
  const list = await getJSON('/api/champions')
  // 给每个英雄挂一个"官方名 + 外号"的可搜索串（大小写无关）
  champs.value = list.map(c => ({ ...c, _search: ((c.name || '') + ' ' + (NAME_NICKS[c.name] || []).join(' ')).toLowerCase() }))
}

const filtered = computed(() => {
  let list = champs.value
  const t = (state.q || '').trim().toLowerCase()
  if (t) list = list.filter(c => (c._search || '').includes(t))
  return list
})
const sorted = computed(() => {
  const list = filtered.value.slice().sort((a, b) => {
    const va = a[sort.value] || 0, vb = b[sort.value] || 0
    return ascending.value ? va - vb : vb - va
  })
  return list
})
const total = computed(() => sorted.value.length)
const pages = computed(() => Math.max(1, Math.ceil(total.value / per.value)))
const cur = computed(() => {
  if (page.value > pages.value) page.value = pages.value
  if (page.value < 1) page.value = 1
  return sorted.value.slice((page.value - 1) * per.value, (page.value - 1) * per.value + per.value)
})

function setSort(s) { sort.value = s; page.value = 1 }
function toggleAsc() { ascending.value = !ascending.value; page.value = 1 }
function setPage(p) { page.value = p }
function onSearch() { page.value = 1 }
function goChamp(id) { state.champId = id; state.view = 'champ' }
function goAugments() { state.view = 'augments' }
function goCategories() { state.cat = '刺客'; state.view = 'category' }

function augChip(b) { return `<span class="aug-chip hasicon" data-name="${b.name}">${b.icon ? `<img class="aicon" src="${b.icon}" onerror="this.style.display='none'">` : '<span class="aicon ph"></span>'}${b.name}${b.quality ? `<span class="q ${b.quality}">${b.quality}</span>` : ''}</span>` }
function rankOf(i) { return (page.value - 1) * per.value + i + 1 }
function fmtPct(w) { return (w * 100).toFixed(1) + '%' }

watch(() => state.q, () => { page.value = 1 })

onMounted(load)
</script>

<template>
  <div class="toolbar" id="homeBar">
    <button class="btn" :class="{ active: sort === 'wilson' }" @click="setSort('wilson')">综合胜率</button>
    <button class="btn" :class="{ active: sort === 'wr' }" @click="setSort('wr')">纯胜率</button>
    <button class="btn" :class="{ active: sort === 'games' }" @click="setSort('games')">场次</button>
    <button class="btn" @click="toggleAsc">{{ ascending ? '降序▼' : '升序▲' }}</button>
    <button class="btn" @click="goCategories">英雄分类</button>
    <button class="btn primary" @click="goAugments">查看所有符文</button>
  </div>

  <table id="tbl">
    <thead>
      <tr>
        <th>英雄</th>
        <th class="th-wr">胜率</th><th class="th-games">场次</th>
        <th class="th-rank">排名</th>
        <th>最优符文</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(c, i) in cur" :key="c.id" class="row" @click="goChamp(c.id)">
        <td><div class="champline"><img class="avatar" :src="c.image" @error="avErr($event, c.name)" alt=""><span>{{ c.name }}</span></div></td>
        <td class="c-wr"><span class="winrate" :class="{ low: c.wr < 0.45 }">{{ fmtPct(c.wr) }}</span></td>
        <td class="c-games num">{{ c.games }}</td>
        <td class="c-rank"><span class="rankbadge" :class="{ r1: rankOf(i) === 1, r2: rankOf(i) === 2, r3: rankOf(i) === 3 }">{{ rankOf(i) }}</span></td>
        <td class="c-augs"><div class="augs"><span v-for="b in (c.best3 || [])" :key="b.name" v-html="augChip(b)"></span></div></td>
      </tr>
    </tbody>
  </table>

  <div class="pager" v-if="pages > 1">
    <button class="pgbtn" :disabled="page <= 1" @click="setPage(page - 1)">‹</button>
    <span class="pginfo">第 {{ page }} / {{ pages }} 页 · 共 {{ total }} 个英雄</span>
    <button class="pgbtn" :disabled="page >= pages" @click="setPage(page + 1)">›</button>
  </div>
</template>
