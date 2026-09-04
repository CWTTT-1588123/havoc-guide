# GitHub 使用教程：从零上传 → 每次改动 → 回滚

> 这是给**新手**看的、带命令和说明的教程。全程用你自己的项目 `havoc-guide`（GitHub 上的 `CWTTT-1588123/havoc-guide`，仓库 `main` 分支）举例。
> 每一步都给出**你能直接复制的 PowerShell 命令**，以及「这步在干嘛」「出错了怎么办」。

---

## 〇、先搞懂三个概念（搞懂就不会乱）

| 概念 | 是什么 | 比喻 |
|---|---|---|
| **本地仓库（本地 Git）** | 你 `E:\Deepseek Harness` 目录里那个 `.git` 文件夹，存着你所有改动的历史 | 你的「草稿本」 |
| **暂存区（stage）** | 你 `git add` 后、还没 `git commit` 的地方 | 进「待提交篮子」 |
| **远端仓库（GitHub）** | 云端那份，别人/你自己从别的电脑也能下载到 | 云端「正式备份」 |

**核心流程只有 3 步，反复用：**
```
git add .        → 把改动放进「待提交篮子」
git commit -m"..." → 在本地记一个版本（存档）
git push        → 把这个版本传到 GitHub（云端备份）
```
**注意**：`commit` 是存在**本地**，只有 `push` 才真正上云端。所以 `commit` 了没 `push`，云端还是旧的。

---

## 一、环境准备（只做一次）

### 1. 确认 Git 已装
```powershell
git --version
```
（我看到你的是 `git version 2.54.0.windows.1`，OK。）

### 2. 让 Git 知道「你是谁」（一个项目/一台电脑设一次）
```powershell
git config --global user.name  "CWTTT-1588123"
git config --global user.email "3209857965@qq.com"
```
> 不设这个，`commit` 会报 **"Author identity unknown"**（你踩过）。
> 查看：`git config user.name` / `git config user.email`

### 3. 关键一步（你踩过的坑）：`http.sslBackend openssl`
你在**中文 Windows** 上 push 报过 `SEC_E_NO_CREDENTIALS`（连接上了但 TLS 握手失败），是 Windows 默认的 `schannel` 后端惹的祸。解决办法（本仓库已设好）：
```powershell
git config http.sslBackend openssl
```
> 以后在本仓库里 push 都不再报那个错。

---

## 二、第一次上传（从零建仓库）

### 1. 本地：初始化仓库（在项目根目录）
```powershell
# 在 E:\Deepseek Harness 目录
git init
git branch -M main        # 把默认分支命名为 main（主干）
```

### 2. 让敏感文件不被上传（重要！）
新建/编辑 `.gitignore`，把下面这些写进去（**注释一定要单独一行**，不能写在模式后面）：
```
captured/
records.jsonl
users.json
users.db
stats.json
.env
.venv/
node_modules/
```
> **坑（你踩过）**：`captured/  # 抓包凭证` 这种「模式 + 同行注释」会让 Git 把整行当成文件名，导致敏感文件没被忽略。**注释必须单独成行**。
> 验证是否生效：`git check-ignore captured/`（有输出=被忽略，没输出=没忽略）。`git add -n .` 也能预览会被上传哪些文件。

### 3. 第一次提交
```powershell
git add .                            # 把所有改动放进暂存区
git commit -m "海克斯大乱斗攻略站：后端+前端+数据管线+文档"   # 记版本
```
> 查看提交历史：`git log --oneline`（每一行一个版本，前面是版本号/commit hash）

### 4. 连上 GitHub（远端地址）
```powershell
git remote add origin https://github.com/CWTTT-1588123/havoc-guide.git
git remote -v        # 查看已连接的远端
```

### 5. 首次上传（推上去）
```powershell
git push -u origin main
```
> `-u` 表示「记住我这次推的就是 origin 的 main」，以后直接 `git push` 就行，不用带 `origin main`。
> 首次 push 会问你要 GitHub 账号密码 → 用**令牌（token）**当密码。

#### 为什么用令牌，怎么拿
GitHub 新规则不能用账号密码，要**个人访问令牌**（PAT）：
1. `https://github.com/settings/tokens?type=beta`（新一代 fine-grained）或 `.../tokens`（classic）
2. 新建 → 只勾 **Contents = Read and write**（推送的最小权限）→ 生成 `github_pat_...` 或 `ghp_...`
3. 推送时把它当密码；或**临时拼进 URL**（推荐一次性，用完就撤）：
   ```powershell
   git push https://<你的令牌>@github.com/CWTTT-1588123/havoc-guide.git main
   ```
   > 推完把地址换回干净的（否则令牌明文留在 `.git/config`）：
   > `git remote set-url origin https://github.com/CWTTT-1588123/havoc-guide.git`

#### 坑（你踩过）：push 报 "Could not connect to github.com port 443"
国内访问 GitHub 不稳定/被墙。解决：重试多次 / 挂代理(`git config http.proxy http://127.0.0.1:端口`) / 换手机热点。

---

## 三、每次改动后再上传（最常用，就 3 步）

以后你改了 `webapp.py`、`index.html`、写了新东西，想备份到 GitHub：

### 1. 看成改了哪些
```powershell
git status          # 红色/?? 的=还没提交；黄色 M 的=改了但没提交
```

### 2. 加入并提交
```powershell
git add .                       # 把这批改动全放进篮子
git commit -m "这次改了什么，简单写一句"     # 记一个版本
```

### 3. 上传
```powershell
git push
```
> 因为之前用了 `-u`，这里直接 `git push` 就行。

**想先预览会被上传什么（防误传敏感/大文件）**：
```powershell
git add -n .        # 只预览，不真正 add
```

**想只看某次改动内容**：
```powershell
git diff            # 改了但没 add 的内容
git diff --cached   # 已 add 未 commit 的内容
```

### 每次都说「改前端重启吗？」（和 Git 无关，但顺带记）
- 改 `static\index.html`：上传到服务器后刷新就行，**不用重启**。
- 改 `webapp.py`：要重启服务器服务。
- 这和「Git 提交」是两回事：Git 备份 ≠ 部署。**Git 备份是上传到 GitHub，部署（上服务器）是另一套 scp + 重启。**

---

## 四、回滚（重点！你要学的核心）

「回滚」有**好几种**，取决于「坏掉的改动走到了哪一步」。**先看改动在哪，再选对应方法。**

用 `git log --oneline` 看版本号（每行最前面那一长串就是 commit hash，可只取前几位）。

### 情况 A：改了但还没 `add`（改动躺在工作区）
想**丢掉这些未提交的修改**，回到上次提交的样子：
```powershell
git restore .              # 丢弃所有未提交的改动
git restore 文件名          # 只丢弃某个文件
```
> 旧写法：`git checkout -- .` / `git checkout -- 文件名`（同样效果）。
> ⚠️ 这会**永久丢掉**未提交的改动，先想清楚。

### 情况 B：`add` 了但还没 `commit`（在暂存区）
想把文件**移出暂存区**（但**保留**改动，方便重新整理）：
```powershell
git restore --staged .      # 全部移出暂存区
git restore --staged 文件名  # 某个文件
```
> 旧写法：`git reset` / `git reset HEAD 文件名`。
> 移出后改动还在工作区，你可以重新 add 或直接 restore 丢弃。

### 情况 C：`commit` 了但**还没 push**（本地新版本错了）
这是**最安全**的撤销，因为远端还没有，随便重置。

**C1：撤销最后一次提交，但保留改动（改完可重新提交）**
```powershell
git reset --soft HEAD~1      # 撤销提交，改动保留在暂存区
```
> `HEAD~1` = 倒数第 1 个提交。改完再 `git add .` + `git commit` 即可。

**C2：撤销提交，且改动回到工作区（还想编辑）**
```powershell
git reset --mixed HEAD~1     # 撤销提交，改动回到工作区（未暂存）
```

**C3：连提交带改动一起扔掉（回到上一个版本的干净状态）**
```powershell
git reset --hard HEAD~1      # ⚠️ 丢弃到上一个版本，改动全没了
```

### 情况 D：已经 `push` 了（远端也有这个提交）——【重要】
这时候**别用 `reset --hard` + 强推**去删历史（那会改写云端历史，别人要是拉过就乱了）。正确做法：

**加一个「反转提交」把坏事抵消（推荐，最安全）**
```powershell
git revert <坏掉的commit hash>
# 它会新生成一个"把这些改动撤销"的提交，你再看下没问题
git push
```
> `git revert` 不改写历史，只是**往前走一步**把之前的改动撤销掉，云端/别人都安全。

**除非你确定只一个人在用，才可以用：**
```powershell
git reset --hard <想回到的commit hash>   # 回到某个老版本
git push --force                          # ⚠️ 强制覆盖远端（会丢历史，谨慎）
```
> `--force` 会**覆盖云端历史**，多人协作严禁用。自己一个人的仓库，也能用，但会丢掉被覆盖的那些提交。

### 情况 E：回到「某个历史版本」
```powershell
git log --oneline            # 找到想回到的版本的 commit hash（前几位即可）
git reset --hard <commit hash>   # 本地回到那个版本
git push --force                 # 若已推送，需强推（同上，慎用）
```
> 或者只"看一眼"老版本然后回来：`git checkout <commit hash>`（会进入游离状态，看完 `git checkout main` 回来）。

### 情况 F：误把敏感文件 `push` 上去了
```powershell
git rm --cached 敏感文件        # 从仓库移除（保留本地文件）
# 把该文件加进 .gitignore
git add . && git commit -m"移除误传的敏感文件"
git push
```
> ⚠️ **但这只是"以后不再上传"，云端历史里那个文件还在**。敏感文件（密码/令牌/抓包凭证）一旦传上云，必须：① **把仓库设为 Private**；② **在 GitHub 上删掉那个文件的历史**（或干脆删仓库重建）；③ **立即更换相应密码/令牌/凭证**（因为历史里躺着，随时可能泄露）。你之前 `captured/` 抓包凭证泄露就是这么处理的。

---

## 五、对比表：reset 与 revert

| | `revert` | `reset --hard` |
|---|---|---|
| 对历史 | **不改写**，新增一个反向提交 | **改写/丢弃**历史 |
| 是否安全 | ✅ 安全，适合多人/已推送 | ⚠️ 危险，已推送慎用，需 `--force` |
| 常用场景 | 撤销**已经 push** 的错误 | 撤销**还没 push** 的本地提交 / 丢弃改动 |
| 影响的提交 | 只影响那一个 | 它之后的所有提交 |

> 口诀：**「还没 push 用 reset，已经 push 用 revert」**（多人时）。

---

## 六、常用命令速查表

| 目的 | 命令 |
|---|---|
| 看状态 | `git status` |
| 看历史 | `git log --oneline` |
| 加入暂存 | `git add .` |
| 提交（本地存版本） | `git commit -m"说明"` |
| 上传云端 | `git push` |
| 拉取云端/别人的更新 | `git pull` |
| 预览会传啥 | `git add -n .` |
| 看改动内容 | `git diff` |
| 丢弃未提交改动 | `git restore .` |
| 移出暂存 | `git restore --staged .` |
| 撤销最近本地提交 | `git reset --soft HEAD~1` |
| 撤销已上传的提交 | `git revert <hash>` |
| 回到某个版本 | `git reset --hard <hash>` |
| 克隆别人的仓库 | `git clone 网址` |
| 删除某个文件的跟踪（保留本地） | `git rm --cached 文件` |
| 打版本标签(带说明,推荐) | `git tag -a v1.0 -m"说明"` |
| 打标签到指定提交 | `git tag -a v1.0 <commit> -m"说明"` |
| 推标签到 GitHub | `git push origin v1.0` |
| 看所有标签 | `git tag` |
| 看标签指向的提交 | `git log --oneline -1 v1.0` |

---

## 七、你自己踩过的坑（已记入 `08_常见错误与解决.md`，这里再汇总）

1. **`.gitignore` 注释写了同行** → 整行变成文件名，敏感文件没被忽略。**注释单独成行**，用 `git check-ignore` 验证。
2. **push 报 `SEC_E_NO_CREDENTIALS`** → Windows 默认 `schannel` 后端有问题，`git config http.sslBackend openssl`。
3. **push 报 `Could not connect 443`** → 国内网络，重试/**代理 `git config --global http.proxy http://127.0.0.1:7897`**/hotspot。
4. **敏感文件 `captured/`、`users.json` 误传** → 设 Private + 换凭证 + 删历史。
5. **令牌写在远程地址里** → 用完 `git remote set-url` 换回干净地址，别让令牌明文留在 `.git/config`。
6. **push 报 `403 Write access not granted`** → **Fine-grained 令牌只对你勾的仓库有效**；推别的仓库要单独给该仓库一个令牌。
7. **push 没让你输密码** → **Git Credential Manager 已缓存凭据**（`git:https://github.com`），是好事，不用输。

---

## 八、答疑小知识（学的时候问过的）

| 疑问 | 答案 |
|---|---|
| 为什么 `5c868de` 就够了（不是 40 位完整哈希） | git 接受**唯一的前缀缩写**；前缀唯一即可，`git log --oneline` 默认显示 7 位短哈希方便人看，真正的身份证是完整 40 位 |
| `git log` 里 `origin/main` 显示**红色** | git 默认配色：**远端跟踪分支(origin/*)红色**、本地分支绿、tag 另一种色；**只是颜色装饰，不是错误** |
| push 怎么记住了不输密码 | Windows **Git Credential Manager** 把令牌存入"凭据管理器"，git 自动取用。想清：删 `git:https://github.com` |
| git 到底改的是哪个 `.git` 文件 | 默认 **`--local`**（当前仓库 `.git/config`）；要全电脑用 **`--global`**；要系统级用 `--system` |

---

## 九、打版本标签(tag) 与 GitHub Release

**想给某个提交(版本)钉个固定名字**（如 v1.0），用 tag。

### 打标签（本地）
```powershell
git tag -a v1.0 -m"v1.0：首次正式版"        # 给当前 HEAD 打带说明的标签(推荐 -a)
git tag -a v1.0 <commit哈希> -m"v1.0：..."  # 给指定提交打(不一定是当前 HEAD)
git tag                                      # 看所有标签
git log --oneline -1 v1.0                    # 看 v1.0 指向哪个提交
```

### 推标签到 GitHub
```powershell
git push origin v1.0     # 把 v1.0 推到 GitHub
```

### tag 和 GitHub Release 的区别
- **tag**：git 里给提交钉的"名字/标记"（`refs/tags/v1.0`）。
- **Release**：GitHub 在 tag 基础上做的**发布页**，能写版本说明(Release notes)、挂可下载文件。
- 网站项目一般 tag 就够了；想对外展示版本说明就再建个 Release。

### 在 GitHub 网页建 Release
1. 仓库页 → 右侧 **Releases** → **Create a new release**
2. **Choose a tag** → 选 `v1.0`（已推上去）
3. **Release title** 填标题（如 `海克斯大乱斗攻略站 v1.0`）
4. **Release notes**：点 **`Generate release notes`** 自动生成变更日志，或自己写 Markdown
5. **Attach binaries**：网站项目**留空**；软件才挂安装包
6. **Release label**：正式版选 **None**；测试版选 **Pre-release**
7. 点 **`Publish release`**（或先 `Save draft` 暂存）

---

## 十、开始使用前，你在本仓库的状态
- 远端：`https://github.com/CWTTT-1588123/havoc-guide.git`（Private），分支 `main`
- 已设 `http.sslBackend openssl`；已配全局代理 `http.proxy=http://127.0.0.1:7897`
- 本地已 commit、`main` 已 push 并同步；`v1.0` 标签已推
- **每次改动后**：`git add .` → `git commit -m"..."` → `git push`
