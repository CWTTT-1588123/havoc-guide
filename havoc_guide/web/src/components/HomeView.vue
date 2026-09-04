<script setup>
import { ref, computed, onMounted } from 'vue'
import { state, getJSON } from '../store'
import { CAT_META, CAT_IDS } from '../data'

const champs = ref([])
const sort = ref('wilson')   // 'wilson' | 'wr' | 'games'
const ascending = ref(false)
const per = ref(20)
const page = ref(1)
const q = ref('')

async function load() { champs.value = await getJSON('/api/champions') }

const filtered = computed(() => {
  let list = champs.value
  const t = q.value.trim().toLowerCase()
  if (t) list = list.filter(c => (c.name || '').toLowerCase().includes(t))
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
function goCategory(c) { state.cat = c; state.view = 'category' }

function augChip(b) { return `${b.icon ? `<img class="aicon" src="${b.icon}" onerror="this.style.display='none'">` : `<span class="aicon ph"></span>`}${b.name}${b.quality ? `<span class="q ${b.quality}">${b.quality}</span>` : ''}` }
function fmtPct(w) { return (w * 100).toFixed(1) + '%' }

onMounted(load)
</script>

<template>
  <div class="toolbar" id="homeBar">
    <button class="btn" :class="{ active: sort === 'wilson' }" @click="setSort('wilson')">综合胜率</button>
    <button class="btn" :class="{ active: sort === 'wr' }" @click="setSort('wr')">纯胜率</button>
    <button class="btn" :class="{ active: sort === 'games' }" @click="setSort('games')">场次</button>
    <button class="btn" @click="toggleAsc">{{ ascending ? '降序▼' : '升序▲' }}</button>
    <button class="btn primary" @click="goAugments">查看所有符文</button>
    <div class="hs"><input type="text" placeholder="搜索英雄" v-model="q" @input="onSearch"></div>
  </div>

  <div class="toolbar searchrow" v-if="q">
    <button class="btn active" @click="q=''">搜索：{{ q }} ×</button>
  </div>

  <table id="tbl">
    <thead>
      <tr>
        <th class="catth">
          <div class="catdrop">
            <span class="catlabel">英雄</span>
            <div class="catdroprel">
              <button class="catbtn">分类 ▾</button>
              <div class="catpop">
                <div v-for="c in ['刺客','战士','法师','射手','辅助','坦克']" :key="c" class="catcard" :style="{ '--c': CAT_META[c].color }" @click="goCategory(c)">
                  <span class="ccdot"></span><span class="ccname">{{ c }}</span><span class="ccnum">{{ CAT_IDS[c].length }}</span>
                </div>
              </div>
            </div>
          </div>
        </th>
        <th>胜率</th><th>场次</th><th>最优符文</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="c in cur" :key="c.id" @click="goChamp(c.id)">
        <td><div class="champline"><img class="avatar" :src="c.image" @error="e => e.target.style.visibility='hidden'" alt=""><span>{{ c.name }}</span></div></td>
        <td><span class="winrate" :class="{ low: c.wr < 0.45 }">{{ fmtPct(c.wr) }}</span></td>
        <td class="num">{{ c.games }}</td>
        <td><div class="augs"><span v-for="b in (c.best3 || [])" :key="b.name" class="aug-chip hasicon" v-html="augChip(b)"></span></div></td>
      </tr>
    </tbody>
  </table>

  <div class="pager" v-if="pages > 1">
    <button class="pgbtn" :disabled="page <= 1" @click="setPage(page - 1)">‹</button>
    <span class="pginfo">第 {{ page }} / {{ pages }} 页 · 共 {{ total }} 个英雄</span>
    <button class="pgbtn" :disabled="page >= pages" @click="setPage(page + 1)">›</button>
  </div>
</template>
