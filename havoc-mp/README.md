# havoc-mp —— 海克斯大乱斗攻略站 · 微信小程序

uni-app（Vue 3 + Vite）工程，对应线上网站 https://haikelol.com（FastAPI 后端**直接复用，无需改动**）。
第一版范围：排行榜 / 所有符文 / 英雄分类 / 英雄详情+评论区 / 登录注册 / 个人中心 / 关于页。
**不含** AI 聊天（wx.request 不支持 SSE）与网页版桌宠/自定义背景（网页专属功能）。

## 目录结构

```
havoc-mp/
├── package.json / vite.config.js / index.html
└── src/
    ├── main.js / App.vue        # 入口 + 全局样式(app.wxss)
    ├── manifest.json            # ⚠️ 注册小程序后填入 appid
    ├── pages.json               # 页面路由 + tabBar(排行榜/符文/我的)
    ├── api.js                   # uni.request 封装 → https://haikelol.com
    ├── store.js                 # 状态/登录态(uni storage)/toast/modal
    ├── data.js / nicknames.js   # 英雄定位/分类/外号搜索表
    ├── components/              # easycom 自动注册（目录名=组件名）
    └── pages/                   # index/augments/category/champ/section/login/profile/about
```

## 本地构建（需联网）

```powershell
cd E:\Deepseek Harness\havoc-mp
npm install                 # 首次：@dcloudio/* 装"latest"，装完后建议把 package.json 里所有 @dcloudio 版本锁成一致的实际版本再 npm install 一次
npm run build:mp-weixin     # 产出 dist/build/mp-weixin
npm run dev:mp-weixin       # 开发监听模式（配合微信开发者工具）
```

## 微信开发者工具

1. 安装[微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)（稳定版）。
2. 导入项目 → 目录选 `E:\Deepseek Harness\havoc-mp\dist\build\mp-weixin` → AppID 填小程序后台的 appid（也可先点"测试号"）。
3. 详情 → 本地设置 → 勾选「不校验合法域名…」（开发期）；**真机/发布前**必须在小程序后台「开发管理→开发设置→服务器域名」添加 request 合法域名 `https://haikelol.com`（已 HTTPS + ICP 备案，满足要求）。
4. 预览/真机调试 → 确认各页正常 → 上传代码。

## 上架前检查清单

- [ ] `src/manifest.json` 与工具里 AppID 一致（个人主体，wx 开头）
- [ ] 小程序后台：request 合法域名 = haikelol.com
- [ ] 小程序备案完成（后台「设置→小程序备案」，约 1~2 周，与域名 ICP 备案不同，必须做）
- [ ] 后台配《用户隐私保护指引》（收集：邮箱/昵称/头像/手机号(可选)）
- [ ] 「关于本站」页已含备案号 + 免责声明 + 用户协议 + 隐私政策 ✅（已内置于 pages/about）
- [ ] 类目选择：个人主体无"资讯/文娱"类目，按「工具-信息查询」类提交；如审核驳回按意见调整
- [ ] 审核备注：说明为真实对局数据统计查询工具、评论区有敏感词过滤+管理员删除机制、可提供测试账号 admin@qq.com

## 已知限制 / 后续（v2）

- AI 聊天：需后端加 WebSocket 版聊天接口（FastAPI `@app.websocket`），小程序用 `uni.connectSocket`；并需 AIGC 标识与深度合成类目评估。
- 图标 CDN：英雄/符文图标当前走 ddragon/communitydragon CDN，国内偏慢——建议镜像到 ECS（`https://haikelol.com/icons/...`）后改 stats.json 里的 image 字段来源。
- 微信一键登录（wx.login + code2session）可作为 v2 登录补充。
- 深色模式：v1 只发浅色。

> 方案文档：`E:\Deepseek Harness\ds_brain\12_微信小程序上架方案.md`
