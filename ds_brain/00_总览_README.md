# 海克斯大乱斗 攻略站 —— 项目总览（ds_brain）

> 这是整个项目的"大脑"：一次看懂的**概览、架构、当前进度、快速上手**。
> 更新：本文件每次工作后应同步更新"当前进度"。

## 文档目录（按需阅读）
| 文件 | 内容 |
|---|---|
| `00_总览_README.md` | 本项目：概览/架构/进度/快速上手/文件清单/注意事项 |
| `01_全过程路线.md` | **完整过程步骤**（起源→需求→抓包→直连→BFS→清洗→统计→符文名→网站→后续） |
| `02_数据获取_抓包与爬虫.md` | mitmproxy 探路 → curl_cffi 直连 → BFS玩家图谱爬虫（含关键突破/错误处理/凭证刷新） |
| `03_数据管线与统计口径.md` | extract/metadata/stats 详细逻辑 + 统计口径（Wilson置信/组合/协同/克制/出装/排除A类） |
| `04_网站功能与前端.md` | FastAPI 后端 + 前端单页（首页/详情/详见页/品质徽标/小字说明/箭头） |
| `05_运行手册与当前进度.md` | 常用命令/备份/系统注意/常见问题（下次接手先看这个） |
| `06_记忆记录模板_给agent的话术.md` | **一键话术**：想记录"why/route、进度、做了什么"时，复制对应模板给 agent 即可，不用重新打字 |
| `07_需求与技术现状.md` | **需求/技术债**：功能清单、技术栈、问题(SHA-256/demo验证码/无测试类型框架)、明确不做(LLM/RAG/DL)、改进路线 |
| `08_常见错误与解决.md` | **⚠️ 错误日志**：项目所有踩坑+解决办法（部署/登录/前端/统计/测试/git），**新错误务必追加这里** |
| `09_GitHub从零到回滚.md` | **Git/GitHub 新手教程**：从零上传 → 每次改动再上传 → **怎么回滚**（reset/revert 区别），含全命令速查 |
| `10_AI聊天需求.md` | **🤖 AI 聊天智能体需求**：点 Q 版人物开聊、站点专属 AI 答疑（英雄/符文/装备/胜率+闲聊）、技术方案与分步实施计划 |

---

## 一、项目是什么
一个面向 LOL **「海克斯大乱斗」**（内部模式名 `KIWI`，`queue=2400`）的**英雄攻略站**：
- **主页**：英雄胜率排行榜（按胜率排序，可搜索/正倒序），每行显示该英雄**前3最优符文**。
- **英雄详情页**：整体胜率、**最优单个符文**（按白银/黄金/棱彩分档）、**最优符文组合**、**搭配增益**、**核心出装**、**克制推荐**。
- 目标：让玩家**最快最直接**得到"这英雄该带什么符文/怎么打"。

核心**判定标准 = 胜率**（来自爬取的国服真实对局数据）。

---

## 二、技术栈 / 架构

```
[WeGame 抓包(mitmproxy, 一次性探路)] → [直连爬虫(curl_cffi 伪装Chrome) BFS玩家图谱]
        ↓ 海克斯大乱斗对局JSON
[extract.py 清洗] → [metadata.py 元数据] → [stats.py 统计(Wilson置信)] → [stats.json]
        ↓
[FastAPI webapp.py] → [前端 static/index.html] → 网站(http://127.0.0.1:8000)
```

**依赖已分离（各自独立 venv）**：
- **爬虫 venv** `wegame-capture\.venv`：`curl_cffi`（伪装 Chrome TLS/HTTP2 指纹，直连 WeGame 接口，核心）+ `mitmproxy`（抓包）。清单见 `wegame-capture\requirements.txt`。
- **网站 venv** `havoc_guide\.venv`：`fastapi + uvicorn`（后端）、`pypinyin`、`python-multipart`、`bcrypt`。清单见 `havoc_guide\requirements.txt`。
- （备用）**league-tools**：可解析游戏 WAD（未实际用于符文名）；**requests/标准库**：DDragon 元数据。

---

## 三、当前进度（务必同步）
| 项 | 状态 |
|---|---|
| **限定版本** | **16.16**（分析/网站只统计这个补丁；`extract`+`bfscrawl` 都加了版本过滤，默认16.16） |
| 分析对局数(16.16) | **8172 场** / 81714 记录 |
| 原始爬取文件(各版本) | data/ ~**12535** 个（仍在增长，旧逻辑爬虫收集） |
| 玩家池 | 8.6万+（BFS扩展） |
| 英雄 | 172 个 |
| 符文 | 208 个 distinct（进统计 202） |
| 符文名/品质 | ✅ 真实（来自 Kiwi 表） |
| 英雄标签(对位用) | ✅ 全标（DDragon自动+人工补充） |
| 网站 | ✅ **已上线 `https://haikelol.com`**（HTTPS+域名，Nginx 反代；备用 `http://8.137.175.107:8000`） |
| **域名** | ✅ `haikelol.com` 已购+已实名；✅ **ICP 备案已完成**（拿到备案号）——可正式上线 |
| **登录/认证** | ✅ 注册(仅邮箱)/密码登录/邮箱验证码注册/忘记密码(邮箱真发)/绑定手机号登录；角色体系(主管理员/管理员/普通用户)+管理后台 |
| 管理员 | **admin@qq.com / admin123**（主管理员 owner；首个注册的账户） |
| `/api/version` | 返回 `16.16` |
| 主数据文件 | `havoc_guide\processed\stats.json`（16.16） |
| **技术现状/债** | 密码 hash=**bcrypt**（旧SHA-256已自动升级）；验证码**安全流**（服务端生成/只发邮箱/不回传/60s限频/用后即删）；**有 pytest、有类型标注(pydantic+mypy)**；**前端框架尚为原生HTML/JS（Vue 3 组件化计划中）**；**无大模型/RAG/深度学习** |

**线上运行状态**：
- **正式站**：阿里云 ECS 上 `systemd havoc-guide.service` 常驻（单进程，`--workers 1`），无需后台任务。
- **本地开发站**：需手动 `uvicorn`（后台任务易断）；爬虫**已暂停**（用户指令）。

**最近改动（见 ds_done 日志）**：
- **上线部署**：纯Python + systemd 部署到阿里云 ECS，公网可访问（关键坑：`--host 0.0.0.0`、`--workers 1`）。
- **登录/认证系统**：真邮件验证码(163 SMTP)/注册(仅邮箱)/忘记密码/绑定手机号登录/角色体系(主管理员/管理员/普通)+管理后台。
- **技术栈正规化（安全+可靠性）✅**：① 密码 **bcrypt**（旧SHA-256首登自动升级）；② **验证码安全流**（服务端生成/只发邮箱/不回传前端/60s限频/用后即删）；③ **pytest**（27个测试：统计6+接口13+模型8）；④ **pydantic 请求模型 + 类型注解 + mypy**。
- **git/GitHub 备份 ✅ 完整**：仓库已建（Private，GitHub: CWTTT-1588123/havoc-guide），`captured/` 抓包凭证等敏感文件已正确 gitignore（踩坑：gitignore 注释不可放在模式同行）。→ **已 push main 成功并全量同步**（踩坑：Windows schannel 报 SEC_E_NO_CREDENTIALS → `git config http.sslBackend openssl`；国内 443 → 代理 `git config --global http.proxy http://127.0.0.1:7897`；Fine-grained 令牌按仓库授权 → 推别的仓库报 403 需单独令牌）。
- **版本标记 v1.0**：把 `havoc-guide` 正式版（提交 `5c868de`）打 tag `v1.0` 并推上 GitHub，可建对应 **Release** 发布页（教程见 `09_GitHub从零到回滚.md`）。
- **Git 教学/练习**：用户全程学会 建库→add/commit→三种 reset→理解 .git 结构→push 上云→每次改动再 push→打版本 tag；练习仓库 `git-practice`（本地 `git练习/`）。
- **环境分离**：爬虫与网站**各建独立 venv**（爬虫 `wegame-capture\.venv` 只装 curl_cffi+mitmproxy；网站 `havoc_guide\.venv` 装 fastapi 全家桶），并清理了爬虫 venv 里混装的网站包。
- **前端**：登录弹窗白底加宽、验证码注册(含确认密码)、密码框睁/闭眼SVG、dark模式对比度、头像菜单不透明、自定义favicon。
- **前端 Vue 3 组件化 ✅（2026-09-04）**：`havoc_guide/web/`（Vite+SFC），全部页面组件化并与原版**一比一对齐**（CSS 逐字复制原版 style；登录/个人中心/后台/排行榜/详情+评论区/分类/所有符文/桌宠/悬浮提示/外号搜索/自定义背景截取预览）；后端加评论接口 + response_model。
- **🤖 待做（新需求）**：**AI 聊天智能体**（点 Q 版人物对话，站点专属 AI 答疑+闲聊）——需求见 `10_AI聊天需求.md`，分步实施中。
- **待做**：公安备案提交；SEO。

---

## 四、文件清单（都在工作区）

**`E:\Deepseek Harness\`**
| 文件/目录 | 作用 |
|---|---|
| `LOL攻略助手_学习路线规划.md` | 最初的学习规划（个人） |
| `LOL海克斯大乱斗攻略站_需求文档.md` | 需求文档（已定稿） |
| `ds_brain\` | **本项目文档（当前所在）** |

**`E:\Deepseek Harness\wegame-capture\`（数据抓取）**
| 文件/目录 | 作用 |
|---|---|
| `bfscrawl.py` | **主爬虫**（BFS玩家图谱，抓满每玩家历史） |
| `crawler.py` | 单历史爬虫（备用/早期） |
| `addon.py` | mitmproxy插件（捕获 WeGame 接口） |
| `run_mitmweb.py` | 启动 mitmweb（抓包用） |
| `.venv\` | **爬虫虚拟环境**（curl_cffi/mitmproxy；网站另有 `havoc_guide\.venv` 装 fastapi 全家桶） |
| `data\` | **爬到的对局**（`detail_*.json`，~9971个） |
| `captured\` | 抓包原始文件 + **凭证来源**（`REQ_GetBattleDetail_*.json`） |
| `players_seen.json` | 已见过的玩家 openid |
| `hidden_players.json` | 隐藏/受限玩家记录 |

**`E:\Deepseek Harness\havoc_guide\`（处理+网站）**
| 文件/目录 | 作用 |
|---|---|
| `extract.py` | 原始JSON→结构化玩家记录（records.jsonl） |
| `metadata.py` | 英雄/装备名（DDragon） |
| `stats.py` | 统计引擎（胜率/组合/协同/克制/出装，Wilson置信） |
| `webapp.py` | FastAPI 后端（API + 服务前端 + **登录/认证/管理后台**） |
| `static/index.html` | 前端单页（首页+英雄详情+详见页+登录弹窗） |
| `processed\` | 输出：records.jsonl、stats.json、champion_names.json、item_names.json、augment_names.json、champion_tags.json、completed_items.json(成装ID,判定非小件)、**users.db(SQLite用户表, 主)**、users.json(旧表/迁移备份) |
| `deploy\setup.sh` | 服务器一键部署脚本（systemd，免交互） |
| `deploy/nginx.conf`、`deploy/nginx-haikelol.conf` | Nginx 反代 80/443→8000 模板（haikelol.com 版） |
| `Dockerfile`、`docker-compose.yml`、`requirements.txt`、`.env.example` | 容器部署 + 依赖 + SMTP/备案号环境变量样例 |
| `havoc_deploy.tar.gz` | 部署包（webapp/static/processed/start脚本；**排除36MB records.jsonl**） |

**`E:\英雄联盟符文id\kiwi\augments.json`**：从游戏文件提取的**符文ID→中文名/品质/描述**表（222个）——**符文名的权威来源**。

---

## 五、快速上手（下次怎么用）

### 看网站
```
& "E:\Deepseek Harness\havoc_guide\.venv\Scripts\python.exe" -m uvicorn webapp:app --host 127.0.0.1 --port 8000
# 在目录 E:\Deepseek Harness\havoc_guide 下运行；浏览器开 http://127.0.0.1:8000
```

### 抓更多数据（扩大）
```
$env:MAX_GAMES="30000"; $env:MAX_PLAYERS="50000"; $env:MAX_PAGES_PER_PLAYER="10000"; $env:DELAY="0.25"
& "E:\Deepseek Harness\wegame-capture\.venv\Scripts\python.exe" "E:\Deepseek Harness\wegame-capture\bfscrawl.py"
# 后台跑（run_in_background）。直连接口，不需要代理。
```

### 刷新网站数据（爬取变多后）
```
# 数据管线属于网站项目，用网站 venv
& "E:\Deepseek Harness\havoc_guide\.venv\Scripts\python.exe" "E:\Deepseek Harness\havoc_guide\extract.py"
& "E:\Deepseek Harness\havoc_guide\.venv\Scripts\python.exe" "E:\Deepseek Harness\havoc_guide\stats.py"
# 然后重启 webapp 加载新的 stats.json
```

---

## 六、关键前提 / 注意事项
- **爬虫直连，不需要系统代理/证书**。它读 `captured\REQ_GetBattleDetail_*.json`（**最新**那份，`files[-1]`）里的 cookie/token 作为鉴权，用 `curl_cffi` 伪装 Chrome。
- **如果爬虫报 `8025009`（凭证过期）**：需要用 mitmproxy 重新抓一次 WeGame 的流量拿新 cookie（见 `02_数据获取_抓包与爬虫.md`）。
- **系统代理应关闭**（`ProxyEnable=0`），否则上网会被劫持。mitmproxy 证书只在"重新抓包"时才需要临时信任。
- 只爬 `queue=2400`（海克斯大乱斗）；隐藏玩家（`error 8000021`）自动跳过。
