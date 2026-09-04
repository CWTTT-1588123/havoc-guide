<script setup>
import { ref, watch, onMounted } from 'vue'
import { state, PET_IMGS } from '../store'
import { TRIVIA, TRIVIA_CUTE } from '../data_trivia'

const pet = ref(null)
const bubble = ref('')
const bubbleShow = ref(false)
const jumping = ref(false)
const gender = ref('f')

function pick() {
  let candidates = PET_IMGS
  if (state.petLock && state.petLock.length) {
    const locked = state.petLock.map(f => PET_IMGS.find(x => x[0] === f)).filter(Boolean)
    if (locked.length) candidates = locked
  }
  const p = candidates[Math.floor(Math.random() * candidates.length)]
  pet.value = p; gender.value = p[2]; state.petGender = p[2]
}

function talk() {
  if (!pet.value) return
  const lib = gender.value === 'f' ? TRIVIA_CUTE : TRIVIA
  bubble.value = lib[Math.floor(Math.random() * lib.length)]
  bubbleShow.value = true
  jumping.value = false
  requestAnimationFrame(() => { jumping.value = true })
  clearTimeout(talk._t)
  talk._t = setTimeout(() => { bubbleShow.value = false }, 6500)
}

function openChat() { state.chatOpen = true }

watch(() => state.petLock, pick)
// 切换页面/点网站标题 → 随机出现语录气泡（由 store.petTick 触发）
watch(() => state.petTick, () => { talk() })
onMounted(() => { pick(); talk() })
</script>

<template>
  <div class="pet" @click="openChat">
    <div class="petbubble" v-if="bubbleShow">{{ bubble }}</div>
    <div class="petbody">
      <img v-if="pet" class="petimg" :class="{ jump: jumping }" :src="'/static/' + pet[0]" :alt="pet[1]" :title="pet[1]">
    </div>
  </div>
</template>

<style scoped>
.pet { position:fixed; right:22px; bottom:120px; z-index:9999; display:flex; flex-direction:column; align-items:center; cursor:pointer; user-select:none; }
.petbody { width:180px; height:180px; }
.petimg { width:180px; height:180px; display:block; object-fit:contain; filter:drop-shadow(0 8px 14px rgba(60,90,150,.28)); }
.petimg.jump { animation:petJump .5s ease; }
.petbubble { display:block; position:absolute; bottom:200px; right:0; width:240px; background:rgba(74,84,110,.86); color:#eef2f8; border:1px solid rgba(150,170,210,.4); border-radius:12px; padding:10px 13px; font-size:21px; line-height:1.45; box-shadow:0 8px 22px rgba(0,0,0,.25); }
.petbubble::after { content:''; position:absolute; bottom:-8px; right:30px; border:8px solid transparent; border-top-color:rgba(74,84,110,.86); border-bottom:0; }
@keyframes petJump { 0%{transform:translateY(0)} 30%{transform:translateY(-18px)} 60%{transform:translateY(0)} 80%{transform:translateY(-8px)} 100%{transform:translateY(0)} }
</style>
