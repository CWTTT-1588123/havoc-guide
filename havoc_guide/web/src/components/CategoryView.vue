<script setup>
import { ref, computed, onMounted } from 'vue'
import { state, getJSON, goHome } from '../store'
import { CAT_META, CAT_IDS, avErr } from '../data'

const champs = ref([])
const cats = ['刺客', '战士', '法师', '射手', '辅助', '坦克']
const cat = computed(() => state.cat)
const meta = computed(() => CAT_META[cat.value] || {})

const list = computed(() => {
  const ids = new Set(CAT_IDS[cat.value] || [])
  return champs.value.filter(c => ids.has(c.id)).slice().sort((a, b) => (b.wilson || 0) - (a.wilson || 0))
})

function medal(i) { return i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : (i + 1) }
function back() { goHome() }
function pick(c) { state.cat = c }
function goChamp(id) { state.champId = id; state.view = 'champ' }
function augChip(b) { return `${b.icon ? `<img class="aicon" src="${b.icon}" onerror="this.style.display='none'">` : '<span class="aicon ph"></span>'}${b.name}${b.quality ? `<span class="q ${b.quality}">${b.quality}</span>` : ''}` }

onMounted(async () => { champs.value = await getJSON('/api/champions') })
</script>

<template>
  <div class="toolbar">
    <button class="btn" @click="back">返回</button>
    <h2>英雄分类</h2>
    <span class="pc-hello">选择英雄分支查看各定位胜率榜</span>
  </div>

  <div class="catpick">
    <div v-for="c in cats" :key="c" class="catcard" :class="{ on: cat === c }" @click="pick(c)">
      <span class="ccname">{{ c }}</span><span class="ccnum">{{ CAT_IDS[c].length }}位</span>
    </div>
  </div>

  <template v-if="cat">
    <div class="cathead" :style="{ '--c': meta.color }">
      <div>
        <h2 class="catttl">{{ cat }} 英雄</h2>
        <div class="capsub">{{ meta.desc }} · 共 {{ list.length }} 位 · 按综合胜率排序</div>
      </div>
    </div>
    <div class="catgrid">
      <div v-for="(c, i) in list" :key="c.id" class="catcard2" :style="{ '--c': meta.color }" @click="goChamp(c.id)">
        <div class="crank">{{ medal(i) }}</div>
        <div class="crow">
          <img class="cavatar" :src="c.image" @error="avErr($event, c.name)" alt="">
          <div class="cinfo">
            <div class="cname">{{ c.name }}</div>
            <div class="csub"><span class="cwr" :class="{ low: c.wr < 0.45 }">{{ (c.wr * 100).toFixed(1) }}%</span> <span class="cnum">{{ c.games }}场</span></div>
          </div>
        </div>
        <div class="caugs"><span v-for="b in (c.best3 || [])" :key="b.name" v-html="augChip(b)"></span></div>
      </div>
    </div>
  </template>
  <div v-else class="empty">请点击上方选择一个英雄分支</div>
</template>
