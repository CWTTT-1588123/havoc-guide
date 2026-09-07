<script>
import { loadAuth } from './store'
import { ensureAugDesc } from './api'

export default {
  onLaunch() {
    loadAuth()
    // 预取符文名→描述表（点符文卡弹窗用）
    ensureAugDesc()
  },
}
</script>

<style>
/* ===== 全局样式（编译进 app.wxss；rpx = 750 等宽设计稿，web 移动端 px × 2） ===== */
page {
  --bg: #f5f7fc;
  --panel: rgba(255, 255, 255, 0.45);
  --panel2: rgba(255, 255, 255, 0.48);
  --line: rgba(70, 90, 150, 0.22);
  --txt: #141a26;
  --sub: #38435e;
  --gold: #9a6d08;
  --blue: #3b8fe0;
  --green: #12a556;
  --red: #9e1010;
  background: linear-gradient(180deg, #eaf4ff, #cfe3f9);
  color: var(--txt);
  font-size: 32rpx;
  line-height: 1.5;
}

/* —— 通用容器/面板 —— */
.pagebox { padding: 20rpx; }
.panel {
  background: var(--panel);
  border: 1rpx solid var(--line);
  border-radius: 28rpx;
  box-shadow: 0 12rpx 40rpx rgba(60, 90, 150, 0.1);
}

/* —— 按钮 —— */
.btn {
  background: var(--panel2);
  border: 1rpx solid var(--line);
  color: var(--txt);
  padding: 16rpx 24rpx;
  border-radius: 24rpx;
  font-size: 28rpx;
  line-height: 1.2;
  margin: 0;
}
.btn::after { border: 0; }
.btn.active { border-color: var(--blue); color: var(--blue); background: rgba(74, 168, 255, 0.12); }
.btn.primary { background: #fff; border: 1rpx solid var(--line); color: var(--blue); font-weight: 700; }
.btn.danger { color: var(--red); }

/* —— 文本语义 —— */
.winrate { color: var(--green); font-weight: 700; }
.winrate.low { color: var(--red); }
.num { color: #111; font-weight: 700; }
.sub { color: var(--sub); }
.empty { color: var(--sub); padding: 48rpx; text-align: center; }

/* —— 品质小字（白银/黄金/棱彩）—— */
.q {
  display: inline-block;
  margin-left: 12rpx;
  padding: 0 14rpx;
  font-size: 28rpx;
  line-height: 40rpx;
  border-radius: 12rpx;
  border: 1rpx solid;
}
.q.白银 { color: #4a5470; border-color: #c3ccdd; background: #eef1f7; }
.q.黄金 { color: #8a6d1a; border-color: #e0ca86; background: #fdf6e0; }
.q.棱彩 { color: #7a3fa0; border-color: #d7b8ea; background: #f3e8fb; }

/* 深色图标容器内的品质小字（发光可读） */
.darkq .q.白银,
.qdark.白银 { color: #cdd6e4; border-color: #3a4252; background: #2b3240; }
.darkq .q.黄金,
.qdark.黄金 { color: #e6c24a; border-color: #6a5a20; background: #3a3018; }
.darkq .q.棱彩,
.qdark.棱彩 { color: #d9a8ff; border-color: #6a3a8a; background: #3a2650; }

/* —— 详情页通用 —— */
.detail { background: var(--panel); border: 1rpx solid var(--line); border-radius: 36rpx; padding: 32rpx; box-shadow: 0 12rpx 40rpx rgba(60, 90, 150, 0.1); }
.dhead { display: flex; align-items: center; gap: 24rpx; flex-wrap: wrap; margin-bottom: 32rpx; }
.dhead .dimg { width: 128rpx; height: 128rpx; border-radius: 32rpx; box-shadow: 0 8rpx 36rpx rgba(74, 168, 255, 0.25); }
.dhead .dtitle { font-size: 48rpx; font-weight: 700; }
.dhead .dsub { color: var(--sub); font-size: 30rpx; margin-top: 4rpx; }
.bigwr { font-size: 60rpx; color: var(--gold); font-weight: 800; }

.sec { margin-top: 44rpx; }
.sechead { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24rpx; font-size: 40rpx; color: var(--gold); font-weight: 700; }
.cap { color: var(--sub); font-size: 28rpx; margin-bottom: 24rpx; }
.secend { height: 1rpx; background: rgba(70, 90, 150, 0.2); width: 100%; margin-top: 36rpx; }
.secmore { display: flex; justify-content: flex-end; margin-top: 28rpx; }
.arrow {
  display: inline-flex;
  align-items: center;
  background: rgba(74, 168, 255, 0.1);
  border: 1rpx solid rgba(74, 168, 255, 0.36);
  color: var(--blue);
  border-radius: 20rpx;
  padding: 12rpx 32rpx;
  font-size: 30rpx;
  font-weight: 600;
  margin: 0;
}
.arrow::after { border: 0; }

/* —— 板块导航 —— */
.secnav { display: flex; flex-wrap: wrap; gap: 12rpx; margin: 8rpx 0 32rpx; }
.navbtn {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(180deg, #f7f9fc, #edf1f8);
  border: 1rpx solid var(--line);
  color: var(--txt);
  padding: 16rpx 28rpx;
  border-radius: 20rpx;
  font-size: 28rpx;
  font-weight: 600;
  margin: 0;
}
.navbtn::after { border: 0; }

/* —— 工具栏 —— */
.toolbar { display: flex; gap: 12rpx; align-items: center; flex-wrap: wrap; margin-bottom: 24rpx; }

/* —— 搜索框 —— */
.sbar {
  display: flex;
  align-items: center;
  background: #fff;
  border: 1rpx solid var(--line);
  border-radius: 28rpx;
  overflow: hidden;
  flex: 1;
  min-width: 0;
}
.sbar .sb-in { flex: 1; border: 0; background: transparent; color: var(--txt); font-size: 30rpx; padding: 18rpx 12rpx; min-width: 0; }
.sbar .sb-clear { color: var(--sub); font-size: 30rpx; padding: 0 20rpx; }

/* —— 页脚/免责声明 —— */
.site-foot { color: var(--sub); font-size: 26rpx; line-height: 1.7; padding: 24rpx 20rpx 60rpx; }
.site-foot .b { color: var(--txt); font-weight: 700; }
.beian { text-align: center; margin-top: 16rpx; }
.verlabel { text-align: center; color: #111; font-size: 26rpx; font-weight: 700; padding-bottom: 30rpx; }

/* —— 评论 —— */
.comrow { display: flex; gap: 16rpx; margin-bottom: 24rpx; align-items: stretch; }
.com-in { flex: 1; background: var(--panel2); border: 1rpx solid var(--line); color: var(--txt); padding: 20rpx; border-radius: 20rpx; font-size: 30rpx; min-height: 70rpx; }
.com-send { flex: none; }
.com-login { margin-bottom: 24rpx; color: var(--sub); font-size: 30rpx; display: flex; align-items: center; gap: 20rpx; }
.com-list { display: flex; flex-direction: column; gap: 16rpx; }
.com-item { background: var(--panel2); border: 1rpx solid var(--line); border-radius: 20rpx; padding: 20rpx 24rpx; }
.com-name { font-size: 30rpx; font-weight: 700; }
.com-text { font-size: 30rpx; margin-top: 6rpx; word-break: break-all; }
.com-time { font-size: 26rpx; color: var(--sub); margin-top: 6rpx; }
</style>
