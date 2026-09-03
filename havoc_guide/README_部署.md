# 海克斯大乱斗 攻略站 —— 上架/部署手册

> 目标：让网站公开到公网，别人点链接进入、浏览器可搜索、可注册登录；管理员可用「管理后台」管理全部用户。

## 0. 网站由什么构成（别人需要什么）
- `webapp.py`：后端（FastAPI）
- `static/`：前端 + 全部图片（含 Q 版人物、预设头像、用户上传头像 avatars/）
- `processed/stats.json + 各元数据 json`：全站数据；`users.json`：用户账号
- 外部：英雄头像/符文图标/出装图标走 **ddragon / communitydragon CDN**（访客需能联网）
- `processed/records.jsonl`：原始对局，**运行时不需要**（可不上传）

---

## 一、买服务器 + 装 Docker（最省事路径）
1. 买一台服务器（阿里云 / 腾讯云 / 轻量云 / 任何 Linux VPS）。建议 ≥1G内存、≥20G 盘。
2. 装 Docker + Compose（Ubuntu）：
   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo systemctl enable --now docker
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```
3. 把 `havoc_guide/` 整个目录传到服务器，例如用 scp 或 Git：
   ```bash
   scp -r havoc_guide root@你的服务器IP:/srv/
   ```

## 二、构建并启动
```bash
cd /srv/havoc_guide
docker-compose up -d --build      # 构建镜像并后台运行
docker-compose logs -f             # 看日志，出现 Uvicorn running on http://0.0.0.0:8000 即成功
```
- 现在 `http://服务器IP:8000` 就能访问了。

## 三、绑定域名 + HTTPS（让浏览器能搜到）
1. 买一个域名，DNS 解析 A 记录指向服务器 IP。
2. 用 Nginx 反代 + 自动 HTTPS（推荐），或直接装宝塔面板配 Nginx。
   - 在域名解析生效后，装 `certbot` 或宝塔，把 `http://域名` 反代到 `127.0.0.1:8000`，申请免费 SSL（https）。
3. 完成后 `https://你的域名` 就是正式网址。

> 浏览器搜到 = 需要网站被搜索引擎收录：确认 `<meta name="description/keywords">`（已加到 index.html），并主动到 百度/Google/必应 的**站长平台提交网址**（可选，会有延迟）。

## 四、普通访客能做什么
- 浏览英雄/符文/出装/分类等全部内容（全站数据在服务器上）。
- **注册/登录**：
  - 推荐用「**注册**」tab：**邮箱＋用户名＋密码**（无需验证码，密码哈希存库）——最省事、可靠。
  - 也可用「密码登录」；「验证码登录」为**演示**（验证码直接显示在页面，未接短信/邮箱）。
- 登录后可：更换头像 / 改密码 / 改用户名 / 自定义背景(含上传图片) / 锁定 Q 版桌宠 / 深浅主题 —— 这些偏好**存服务器按账号同步**（换设备也保留）。

## 四·二、不用 Docker 的纯 Python 部署（更简单）
如果你不想用 Docker，直接在服务器上跑 Python：
```bash
# 1) 上传 havoc_guide 到 /srv/havoc_guide，进入目录
cd /srv/havoc_guide
# 2) 装 python3 + 依赖
sudo apt install -y python3 python3-venv
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
# 3) 试运行
uvicorn webapp:app --host 127.0.0.1 --port 8000 --workers 2
# 4) 用 systemd 常驻（文件见 deploy/havoc-guide.service）
sudo cp deploy/havoc-guide.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now havoc-guide
# 5) 用 Nginx 反代 8000 + HTTPS（见 README 第三节）
```
> `deploy/havoc-guide.service` 里 `User=/WorkingDirectory=ExecStart` 改成你实际路径/用户即可。

## 五、管理员后台
- **第一个注册的用户 = 管理员**。（如果之前已有账号，可在 `processed/users.json` 里的用户加 `"is_admin": true`，或直接在管理后台把某账号设为管理员。）
- 登录后点右上角头像 → 菜单「管理后台」→ 可查看所有用户、**设为/降为管理员、重置密码、删除用户**。

## 六、真实邮箱/短信验证码（可选，需服务商）
- 目前验证码是"演示"（生成后显示在页面，不真正发送）。
- 要真发验证码：接入**阿里云短信 / 腾讯云短信 / SendGrid / SMTP 等**，在 `webapp.py` 的 `/api/auth/send_code` 里调用发送接口（需要服务商的 AK/SK、模板、签名），并把前端"显示验证码"去掉。
- 若只想做**安全的邮箱+密码注册**（不发验证码），可直接用"密码登录"注册；我可以帮你把"验证码登录"tab 弱化成"邮箱+密码注册"。

## 七、常见问题
- 打不开：检查 `docker-compose up -d` 是否成功、防火墙是否放行 8000（或只经由 Nginx 80/443）。
- 用户头像上传：`static/avatars/` 需要可写（Docker 里默认可写；若挂载卷需给权限）。
- 数据更新：重跑 `extract.py`→`stats.py` 后用 Docker 重新 `--build` 或把新 `stats.json` 拷进容器/挂载目录。
- 并发注册：`users.json` 单文件在并发下可能冲突；用户多了建议换 SQLite/Postgres（我可帮你改）。
