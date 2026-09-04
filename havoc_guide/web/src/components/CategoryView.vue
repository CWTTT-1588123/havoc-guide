<script setup>
import { ref, computed, onMounted } from 'vue'
import { state, getJSON } from '../store'
import { CAT_META, CAT_IDS } from '../data'

const champs = ref([])
const cat = computed(() => state.cat)
const meta = computed(() => CAT_META[cat.value] || {})

const list = computed(() => {
  const ids = new Set(CAT_IDS[cat.value] || [])
  return champs.value.filter(c => ids.has(c.id)).slice().sort((a, b) => (b.wilson || 0) - (a.wilson || 0))
})

function medal(i) { return i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : (i + 1) }
function back() { state.view = 'home' }
function goChamp(id) { state.champId = id; state.view = 'champ' }
function augChip(b) { return `${b.icon ? `<img class="aicon" src="${b.icon}" onerror="this.style.display='none'">` : '<span class="aicon ph"></span>'}${b.name}${b.quality ? `<span class="q ${b.quality}">${b.quality}</span>` : ''}` }

onMounted(async () => { champs.value = await getJSON('/api/champions') })
</script>

<template>
  <div class="toolbar"><button class="btn" @click="back">返回</button></div>
  <div class="detail">
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
          <img class="cavatar" :src="c.image" @error="e => e.target.style.visibility='hidden'" alt="">
          <div class="cinfo">
            <div class="cname">{{ c.name }}</div>
            <div class="csub"><span class="cwr">{{ (c.wr * 100).toFixed(1) }}%</span> <span class="cnum">{{ c.games }}场</span></div>
          </div>
        </div>
        <div class="caugs"><span v-for="b in (c.best3 || [])" :key="b.name" class="aug-chip hasicon" v-html="augChip(b)"></span></div>
      </div>
    </div>
  </div>
</template>
