<script setup>
import { ref, computed, onMounted } from 'vue'
import { state, adminApi, goHome, toast } from '../store'

const users = ref([])
const me = computed(() => state.auth && state.auth.user)
const meOwner = computed(() => !!(me.value && me.value.owner))

async function load() {
  const d = await adminApi('users')
  if (d.ok) { users.value = d.users } else { alert(d.error || '加载失败') }
}

function back() { goHome() }

function roleBadge(u) {
  if (u.owner) return '<span class="q 黄金">主管理员</span>'
  if (u.is_admin) return '<span class="q 黄金">管理员</span>'
  return '<span class="q 白银">普通</span>'
}

async function setRole(u, val) {
  const r = await adminApi('user/' + u.id, { is_admin: val ? 1 : 0 })
  if (r.ok) { toast(val ? '已设为管理员' : '已降为普通'); load() } else { alert(r.error || '操作失败') }
}
async function resetPwd(u) {
  const p = prompt('为 ' + (u.name || u.contact) + ' 设置新密码（至少6位）：')
  if (p === null) return
  if (p.length < 6) { alert('密码至少6位'); return }
  const r = await adminApi('user/' + u.id, { password: p })
  if (r.ok) { toast('密码已重置') } else { alert(r.error || '重置失败') }
}
async function del(u) {
  if (!confirm('确定删除用户 ' + (u.name || u.contact) + '？')) return
  const r = await adminApi('delete/' + u.id, {}, 'POST')
  if (r.ok) { toast('已删除'); load() } else { alert(r.error || '删除失败') }
}

function actionsFor(u) {
  const self = u.contact === me.value.contact
  if (self) return '<span style="color:var(--sub);font-size:20px;">当前账号</span>'
  let b = ''
  if (meOwner.value) {
    b += u.is_admin ? `<button class="pc-btn" onclick="__do('set0','${u.id}')">降为普通</button>` : `<button class="pc-btn" onclick="__do('set1','${u.id}')">设为管理员</button>`
    b += ` <button class="pc-btn" onclick="__do('pwd','${u.id}')">重置密码</button>`
    b += ` <button class="pc-btn danger" onclick="__do('del','${u.id}')">删除</button>`
  } else {
    b += u.is_admin ? '<span style="color:var(--sub);font-size:20px;">仅主管理员可操作</span>'
                     : `<button class="pc-btn" onclick="__do('pwd','${u.id}')">重置密码</button> <button class="pc-btn danger" onclick="__do('del','${u.id}')">删除</button>`
  }
  return b
}
// 由模板 v-html 回调（因为 v-html 里的 onclick 需全局函数）
window.__do = (kind, id) => {
  const u = users.value.find(x => x.id === id); if (!u) return
  if (kind === 'set0') setRole(u, 0)
  else if (kind === 'set1') setRole(u, 1)
  else if (kind === 'pwd') resetPwd(u)
  else if (kind === 'del') del(u)
}

onMounted(load)
</script>

<template>
  <div class="toolbar">
    <button class="btn" @click="back">返回</button>
    <h2>管理后台</h2>
    <span class="pc-hello">共 {{ users.length }} 位用户</span>
  </div>
  <div class="detail">
    <h3 class="sechead"><span>用户管理</span></h3>
    <table id="tbl">
      <thead><tr><th>用户</th><th>账号</th><th>角色</th><th>注册时间</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td><div class="champline"><img v-if="u.avatar" class="avatar" :src="u.avatar"><span>{{ u.name || '—' }}</span></div></td>
          <td>{{ u.contact }}</td>
          <td v-html="roleBadge(u)"></td>
          <td>{{ new Date((u.created || 0) * 1000).toLocaleDateString() }}</td>
          <td v-html="actionsFor(u)"></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
