"""
webapp.py —— MVP 网站后端（FastAPI）。
- 启动时加载 processed/stats.json + 元数据（英雄/装备/符文名字、英雄头像）。
- 提供 API：/api/champions, /api/champion/{id}, /api/augments_global。
- 首页 index.html 用 JS 拉取渲染（主页排行榜 + 英雄详情）。
"""
import json
import os
import re
import smtplib
import sqlite3
import bcrypt
import urllib.request
import hashlib
import secrets
import time
from typing import Optional, Dict, List, Any, Tuple
from email.mime.text import MIMEText
from email.header import Header

from pypinyin import lazy_pinyin
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import schemas


def _load_env():
    """启动时读取同目录 .env 文件，填入环境变量（不覆盖已存在的）。"""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v


_load_env()

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


def _load(name, default=None):
    p = os.path.join(OUT_DIR, name)
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def _dragon_version():
    try:
        with urllib.request.urlopen("https://ddragon.leagueoflegends.com/api/versions.json", timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))[0]
    except Exception:
        # 拿不到最新版本时兜底到包含全部英雄（含新英雄）的版本
        return "16.17.1"


STATS = _load("stats.json", {})
CHAMPS = _load("champion_names.json", {})
AUGS = _load("augment_names.json", {})
ITEMS = _load("item_names.json", {})
AUG_ICONS = _load("augment_icons.json", {})  # 符文ID -> CDN图标URL
DRAGON_VER = os.environ.get("DRAGON_VER", _dragon_version())
PATCH_VERSION = os.environ.get("PATCH_VERSION", "16.16")  # 当前LOL补丁版本，用于网站名标注

app = FastAPI(title="海克斯大乱斗 攻略站")
# 静态资源（桌面宠物等）：把图片放进 static/ 即可经 /static/... 访问
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _champ_img(cid):
    c = CHAMPS.get(str(cid), {})
    key = c.get("id")  # DDragon 的 id (如 "Ahri")
    if key:
        return "https://ddragon.leagueoflegends.com/cdn/%s/img/champion/%s.png" % (DRAGON_VER, key)
    return ""


@app.get("/", response_class=HTMLResponse)
def home():
    path = os.path.join(STATIC_DIR, "index.html")
    with open(path, encoding="utf-8") as f:
        html = f.read().replace("{{PATCH_VER}}", PATCH_VERSION)
    icp = os.environ.get("ICP_NUMBER", "").strip()
    if icp:
        html = html.replace("{{ICP_BLOCK}}",
                            '　·　<a href="https://beian.miit.gov.cn" target="_blank" rel="noopener">%s</a>' % icp)
    else:
        html = html.replace("{{ICP_BLOCK}}", "")
    return html

@app.get("/api/version")
def api_version():
    return {"game_version": PATCH_VERSION}


@app.get("/api/champions")
def api_champions():
    champs = STATS.get("champions", [])
    detail = STATS.get("champion_detail", {})
    for c in champs:
        c["image"] = _champ_img(c["id"])
        d = detail.get(c["id"], {})
        top3 = (d.get("augments", []) or [])[:3]
        c["best3"] = [{
            "name": AUGS.get(str(a["id"]), {}).get("name", "符文" + str(a["id"])),
            "quality": AUGS.get(str(a["id"]), {}).get("quality", ""),
            "icon": AUG_ICONS.get(str(a["id"]), ""),
        } for a in top3]
    return JSONResponse(champs)


@app.get("/api/champion/{cid}")
def api_champion(cid: str):
    detail = STATS.get("champion_detail", {}).get(cid)
    if not detail:
        return JSONResponse({"error": "no data"}, status_code=404)
    detail = dict(detail)

    # 单个符文：补名字+品质+图标，并按品质分三档（每档最多5个，保留原胜率排序）
    augs_meta = {}
    for a in detail.get("augments", []):
        meta = AUGS.get(str(a["id"]), {})
        a["name"] = meta.get("name", "符文" + str(a["id"]))
        a["quality"] = meta.get("quality", "")
        a["icon"] = AUG_ICONS.get(str(a["id"]), "")
        augs_meta[str(a["id"])] = a["name"]
    by_q = {}
    for a in detail.get("augments", []):
        by_q.setdefault(a.get("quality", "其他"), []).append(a)
    quality_order = ["白银", "黄金", "棱彩", "其他"]
    detail["augments_by_quality"] = [
        {"quality": q, "items": by_q.get(q, [])[:15]} for q in quality_order if by_q.get(q)
    ]

    # 组合：过滤"只有1个符文"的，只保留>=2个，并附上符文名+品质，精简到6条
    combos = []
    for c in detail.get("combos", []):
        augs = c.get("augments", [])
        if len(augs) < 2:
            continue
        c["augment_meta"] = [{
            "id": str(x),
            "name": AUGS.get(str(x), {}).get("name", "符文" + str(x)),
            "quality": AUGS.get(str(x), {}).get("quality", ""),
            "icon": AUG_ICONS.get(str(x), ""),
        } for x in augs]
        combos.append(c)
    detail["combos"] = combos[:20]

    # 协同/出装/对位 附名字+品质+图标 并精简到15条
    for s in detail.get("synergy", []):
        s["aname"] = AUGS.get(str(s["a"]), {}).get("name", str(s["a"]))
        s["bname"] = AUGS.get(str(s["b"]), {}).get("name", str(s["b"]))
        s["aquality"] = AUGS.get(str(s["a"]), {}).get("quality", "")
        s["bquality"] = AUGS.get(str(s["b"]), {}).get("quality", "")
        s["aicon"] = AUG_ICONS.get(str(s["a"]), "")
        s["bicon"] = AUG_ICONS.get(str(s["b"]), "")
    detail["synergy"] = detail.get("synergy", [])[:15]
    # 出装：按物品 id 附上 ddragon 装备图标（与头像同版本）
    for b in detail.get("builds", []):
        b["item_icons"] = ["https://ddragon.leagueoflegends.com/cdn/%s/img/item/%s.png" % (DRAGON_VER, i) for i in b.get("items", [])]
    detail["builds"] = detail.get("builds", [])[:15]
    # 克制推荐：过滤掉"质变/潘朵拉"这类随机事件符文（结果随机、非确定性克制），并补品质，再取前6
    cnt = []
    for s in detail.get("counters", []):
        nm = s.get("augment_name", "")
        if ("质变" in nm) or ("潘朵拉" in nm):
            continue
        s["augment_quality"] = AUGS.get(str(s.get("augment", "")), {}).get("quality", "")
        s["icon"] = AUG_ICONS.get(str(s.get("augment", "")), "")
        cnt.append(s)
    detail["counters"] = cnt[:15]

    detail["image"] = _champ_img(cid)
    return JSONResponse(detail)


@app.get("/api/augments_global")
def api_augments_global():
    return JSONResponse(STATS.get("augments_global", []))


@app.get("/api/augments_all")
def api_augments_all():
    """查看所有符文：按品质分组，组内按中文名拼音排序，附效果描述（去掉问号占位）。"""
    def clean(t):
        return (t or "").replace("？", "").replace("?", "").strip()

    groups = {}
    for aid, meta in AUGS.items():
        q = meta.get("quality") or "其他"
        groups.setdefault(q, []).append({
            "id": aid,
            "name": clean(meta.get("name", "符文" + aid)),
            "en": clean(meta.get("en", "")),
            "desc": clean(meta.get("desc", "")),
            "icon": AUG_ICONS.get(str(aid), ""),
            "quality": q,
            "_sort": "".join(lazy_pinyin(meta.get("name", ""))) or aid,
        })
    order = ["白银", "黄金", "棱彩", "其他"]
    result = []
    for q in order:
        items = groups.get(q, [])
        items.sort(key=lambda x: (x["_sort"], x["id"]))
        for it in items:
            it.pop("_sort", None)
        result.append({"quality": q, "items": items})
    return JSONResponse(result)


# ============ 本地用户（存 SQLite 数据库）============
USERS_PATH = os.environ.get("DSH_USERS_PATH", os.path.join(OUT_DIR, "users.json"))   # 旧 JSON（迁移来源/备份）
DB_PATH = os.environ.get("DSH_DB_PATH", os.path.join(OUT_DIR, "users.db"))


def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    with _db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT, contact TEXT, phone TEXT DEFAULT '',
            salt TEXT, phash TEXT, avatar TEXT DEFAULT '',
            is_admin INTEGER DEFAULT 0, created INTEGER DEFAULT 0,
            tokens TEXT DEFAULT '[]',
            bg TEXT DEFAULT '', bgImg TEXT DEFAULT '',
            pets TEXT DEFAULT '[]', theme TEXT DEFAULT '',
            comments TEXT DEFAULT '[]')""")


def _row_user(r):
    return {"id": r["id"], "name": r["name"] or "", "contact": r["contact"] or "",
            "phone": r["phone"] or "", "salt": r["salt"] or "", "phash": r["phash"] or "",
            "avatar": r["avatar"] or "", "is_admin": bool(r["is_admin"]), "created": r["created"] or 0,
            "tokens": json.loads(r["tokens"] or "[]"), "bg": r["bg"] or "", "bgImg": r["bgImg"] or "",
            "pets": json.loads(r["pets"] or "[]"), "theme": r["theme"] or "",
            "comments": json.loads(r["comments"] or "[]")}


def _load_users():
    with _db() as conn:
        rows = conn.execute("SELECT * FROM users").fetchall()
    return {r["id"]: _row_user(r) for r in rows}


def _save_users():
    with _db() as conn:
        conn.execute("DELETE FROM users")
        for u in USERS.values():
            conn.execute(
                "INSERT INTO users (id,name,contact,phone,salt,phash,avatar,is_admin,created,tokens,bg,bgImg,pets,theme,comments)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (u["id"], u.get("name", ""), u.get("contact", ""), u.get("phone", ""),
                 u.get("salt", ""), u.get("phash", ""), u.get("avatar", ""),
                 1 if u.get("is_admin") else 0, u.get("created", 0),
                 json.dumps(u.get("tokens", [])), u.get("bg", ""), u.get("bgImg", ""),
                 json.dumps(u.get("pets", [])), u.get("theme", ""), json.dumps(u.get("comments", []))))


_init_db()
# 启动：从 SQLite 加载；若 DB 为空且旧 users.json 存在，则迁移导入
try:
    USERS = _load_users()
except Exception:
    USERS = {}
if not USERS and os.path.exists(USERS_PATH):
    try:
        with open(USERS_PATH, encoding="utf-8") as _f:
            USERS = json.load(_f)
    except Exception:
        USERS = {}
    for _u in USERS.values():
        if not _u.get("tokens"):
            _u["tokens"] = [_u["token"]] if _u.get("token") else []
    _save_users()

CODES = {}  # contact -> {code, exp}

# ---- SMTP 发信配置（用环境变量，真发验证码）----
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.163.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
MAIL_FROM = os.environ.get("MAIL_FROM", SMTP_USER)


def _smtp_ready():
    return bool(SMTP_USER and SMTP_PASS)


def _send_email(to_addr, subject, body):
    """用配置的 SMTP 真发一封 HTML 邮件。失败返回 False。"""
    if not _smtp_ready():
        return False
    msg = MIMEText(body, "html", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = MAIL_FROM
    msg["To"] = to_addr
    try:
        if SMTP_PORT == 465:
            s = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=12)
        else:
            s = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=12)
            s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(MAIL_FROM, [to_addr], msg.as_string())
        s.quit()
        return True
    except Exception as e:
        print("[SMTP] send failed:", repr(e))
        return False


def _make_code_html(code):
    return ("<div style='font-family:sans-serif;max-width:480px;margin:0 auto;'>"
            "<h2 style='color:#2c4a72;'>海克斯大乱斗攻略站</h2>"
            "<p>你的验证码是：</p>"
            "<p style='font-size:32px;font-weight:bold;letter-spacing:6px;color:#b8860b;'>%s</p>"
            "<p>10 分钟内有效，请勿泄露给他人。</p>"
            "<p style='color:#888;font-size:12px;'>若非本人操作请忽略此邮件。</p></div>" % code)


def _hash(password):
    """bcrypt 哈希（内置随机盐，安全）。超72字节自动截断（bcrypt 限制）。"""
    pw = password.encode("utf-8")
    if len(pw) > 72:
        pw = pw[:72]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def _is_bcrypt(h: str) -> bool:
    return isinstance(h, str) and h.startswith("$2")


def _check_pw(u: Dict[str, Any], password: str) -> bool:
    """校验密码：新=bcrypt；旧=SHA-256(退化校验，成功则自动升级为 bcrypt)。"""
    phash = u.get("phash") or ""
    pw = password.encode("utf-8")[:72]
    if _is_bcrypt(phash):
        return bcrypt.checkpw(pw, phash.encode("utf-8"))
    # 旧方案：sha256(salt + password)；对则升级为 bcrypt
    salt = u.get("salt") or ""
    if phash == hashlib.sha256((salt + password).encode("utf-8")).hexdigest():
        try:
            u["phash"] = _hash(password)
            u["salt"] = ""
            _save_users()
        except Exception:
            pass
        return True
    return False


def _norm_contact(c: Optional[str]) -> str:
    """归一化账号：邮箱转小写、手机号去空格/横线等。"""
    c = (c or "").strip()
    if "@" in c:
        return c.lower()
    return re.sub(r"[^\d]", "", c)


def _valid_contact(c: str) -> bool:
    """校验账号：合法邮箱 或 大陆手机号（1开头11位）。"""
    if "@" in c:
        return bool(re.match(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$", c))
    return bool(re.match(r"^1[3-9]\d{9}$", c))


def _default_name(contact: str) -> str:
    if "@" in contact:
        return "用户" + contact.split("@")[0][:6]
    return "用户" + contact[-4:]


def _find_by_contact(c):
    c = _norm_contact(c)
    for u in USERS.values():
        if _norm_contact(u.get("contact")) == c:
            return u
    return None


def _find_by_phone(p):
    p = _norm_contact(p)
    for u in USERS.values():
        if _norm_contact(u.get("phone", "")) == p and p:
            return u
    return None


def _find_account(c):
    """登录时根据输入自动匹配：含@→邮箱，否则→绑定的手机号。"""
    c = _norm_contact(c)
    if "@" in c:
        return _find_by_contact(c)
    return _find_by_phone(c)


async def _body(request):
    try:
        return await request.json()
    except Exception:
        return {}


def _validate(model, data: Dict[str, Any]) -> Any:
    """用 pydantic 模型校验请求体；失败返回 None（调用方回 400）。"""
    try:
        return model(**data)
    except Exception:
        return None


def _auth_user(req):
    h = req.headers.get("authorization", "")
    if h.startswith("Bearer "):
        t = h[7:]
        for u in USERS.values():
            if t in u.get("tokens", []) or t == u.get("token"):
                return u
    return None


def _owner_id():
    admins = [x for x in USERS.values() if x.get("is_admin")]
    if not admins:
        return None
    return min(admins, key=lambda x: x.get("created", 0))["id"]


def _is_owner(u):
    """主管理员 = 最早创建的管理员，永远置顶、权限最大。"""
    if not u or not u.get("is_admin"):
        return False
    return u["id"] == _owner_id()


def _user_public(u):
    return {"id": u["id"], "name": u.get("name", ""), "contact": u.get("contact", ""),
            "phone": u.get("phone", ""), "avatar": u.get("avatar", ""),
            "is_admin": bool(u.get("is_admin")), "owner": bool(_is_owner(u))}


@app.post("/api/auth/send_code")
async def api_send_code(request: Request):
    d = await _body(request)
    contact = _norm_contact(d.get("contact"))
    if not contact:
        return JSONResponse({"ok": False, "error": "请输入邮箱"}, status_code=400)
    if "@" not in contact or not _valid_contact(contact):
        return JSONResponse({"ok": False, "error": "邮箱输入错误，请检查格式"}, status_code=400)
    # 频率限制：60 秒内同一邮箱不能重复发
    if time.time() - CODES.get(contact, {}).get("sent_at", 0) < 60:
        return JSONResponse({"ok": False, "error": "发送太频繁，请稍后再试"}, status_code=429)
    if not _smtp_ready():
        return JSONResponse({"ok": False, "error": "邮件服务未配置，无法发送验证码"}, status_code=500)
    code = "%06d" % secrets.randbelow(1000000)
    CODES[contact] = {"code": code, "exp": time.time() + 600, "sent_at": time.time()}
    ok = _send_email(contact, "海克斯攻略站验证码", _make_code_html(code))
    if not ok:
        return JSONResponse({"ok": False, "error": "邮件发送失败，请稍后重试"}, status_code=500)
    return {"ok": True, "sent": True}   # 只提示已发送，绝不返回验证码


@app.post("/api/auth/register")
async def api_register(request: Request):
    d = await _body(request)
    contact = _norm_contact(d.get("contact"))
    code = (d.get("code") or "").strip()
    password = d.get("password") or ""
    name = (d.get("name") or "").strip() or _default_name(contact)
    if "@" not in contact or not _valid_contact(contact):
        return JSONResponse({"ok": False, "error": "请输入正确的邮箱"}, status_code=400)
    c = CODES.get(contact)
    if not c or c["code"] != code or c["exp"] < time.time():
        return JSONResponse({"ok": False, "error": "验证码错误或已过期"}, status_code=400)
    if _find_by_contact(contact):
        return JSONResponse({"ok": False, "error": "该邮箱已注册，请直接登录"}, status_code=400)
    uid = secrets.token_hex(8)
    is_admin = len(USERS) == 0  # 第一个注册的用户设为管理员
    token = secrets.token_hex(16)
    USERS[uid] = {"id": uid, "name": name, "contact": contact, "salt": "",
                  "phash": _hash(password), "avatar": "", "tokens": [token],
                  "is_admin": is_admin, "created": int(time.time())}
    _save_users()
    CODES.pop(contact, None)  # 用后即删，防重放
    return {"ok": True, "token": token, "user": _user_public(USERS[uid])}


@app.post("/api/auth/register_pub")
async def api_register_pub(request: Request):
    """公开注册：邮箱 + 密码（无需验证码，可真正上线用）。"""
    d = await _body(request)
    body = _validate(schemas.RegisterPubBody, d)
    if body is None:
        return JSONResponse({"ok": False, "error": "参数不完整或格式错误"}, status_code=400)
    contact = _norm_contact(body.contact)
    password = body.password
    name = (body.name or "").strip() or _default_name(contact)
    if not contact or len(password) < 6:
        return JSONResponse({"ok": False, "error": "请填写邮箱，密码至少6位"}, status_code=400)
    if "@" not in contact or not _valid_contact(contact):
        return JSONResponse({"ok": False, "error": "请输入正确的邮箱"}, status_code=400)
    if _find_by_contact(contact):
        return JSONResponse({"ok": False, "error": "该邮箱已注册，请直接登录"}, status_code=400)
    uid = secrets.token_hex(8)
    is_admin = len(USERS) == 0  # 第一个注册的用户设为管理员
    token = secrets.token_hex(16)
    USERS[uid] = {"id": uid, "name": name, "contact": contact, "salt": "",
                  "phash": _hash(password), "avatar": "", "tokens": [token],
                  "is_admin": is_admin, "created": int(time.time())}
    _save_users()
    CODES.pop(contact, None)  # 用后即删，防重放
    return {"ok": True, "token": token, "user": _user_public(USERS[uid])}


@app.post("/api/auth/login")
async def api_login(request: Request):
    d = await _body(request)
    body = _validate(schemas.LoginBody, d)
    if body is None:
        return JSONResponse({"ok": False, "error": "参数不完整或格式错误"}, status_code=400)
    contact = _norm_contact(body.contact)
    code = (body.code or "").strip()
    password = body.password or ""
    u = _find_account(contact)
    if not u:
        return JSONResponse({"ok": False, "error": "账号不存在，请先注册"}, status_code=404)
    if code:
        c = CODES.get(contact)
        if not c or c["code"] != code or c["exp"] < time.time():
            return JSONResponse({"ok": False, "error": "验证码错误或已过期"}, status_code=400)
        CODES.pop(contact, None)  # 用后即删，防重放
    elif password:
        if not _check_pw(u, password):
            return JSONResponse({"ok": False, "error": "密码错误"}, status_code=400)
    else:
        return JSONResponse({"ok": False, "error": "请输入验证码或密码"}, status_code=400)
    tok = secrets.token_hex(16)
    u.setdefault("tokens", []).append(tok)
    _save_users()
    return {"ok": True, "token": tok, "user": _user_public(u)}


@app.get("/api/auth/me")
async def api_me(request: Request):
    u = _auth_user(request)
    if not u:
        return JSONResponse({"ok": False, "error": "未登录"}, status_code=401)
    return {"ok": True, "user": _user_public(u)}


@app.post("/api/auth/avatar")
async def api_avatar(request: Request):
    u = _auth_user(request)
    if not u:
        return JSONResponse({"ok": False, "error": "未登录"}, status_code=401)
    d = await _body(request)
    dataurl = d.get("avatar") or ""
    if not dataurl.startswith("data:image"):
        return JSONResponse({"ok": False, "error": "无效图片"}, status_code=400)
    import base64
    header, b64 = dataurl.split(",", 1)
    raw = base64.b64decode(b64)
    ext = "png"
    if "image/jpeg" in header:
        ext = "jpg"
    elif "image/webp" in header:
        ext = "webp"
    avdir = os.path.join(STATIC_DIR, "avatars")
    os.makedirs(avdir, exist_ok=True)
    fname = "%s.%s" % (u["id"], ext)
    with open(os.path.join(avdir, fname), "wb") as f:
        f.write(raw)
    u["avatar"] = "/static/avatars/" + fname
    _save_users()
    return {"ok": True, "avatar": u["avatar"]}


@app.post("/api/auth/logout")
async def api_logout(request: Request):
    u = _auth_user(request)
    if u:
        h = request.headers.get("authorization", "")
        t = h[7:] if h.startswith("Bearer ") else ""
        u["tokens"] = [x for x in u.get("tokens", []) if x != t]
        if u.get("token") == t:
            u["token"] = None
        _save_users()
    return {"ok": True}


@app.post("/api/auth/password")
async def api_password(request: Request):
    u = _auth_user(request)
    if not u:
        return JSONResponse({"ok": False, "error": "未登录"}, status_code=401)
    d = await _body(request)
    pw = d.get("password") or ""
    if len(pw) < 4:
        return JSONResponse({"ok": False, "error": "密码至少4位"}, status_code=400)
    u["salt"] = ""
    u["phash"] = _hash(pw)
    _save_users()
    return {"ok": True}


@app.post("/api/auth/name")
async def api_name(request: Request):
    u = _auth_user(request)
    if not u:
        return JSONResponse({"ok": False, "error": "未登录"}, status_code=401)
    d = await _body(request)
    name = (d.get("name") or "").strip()
    if not name:
        return JSONResponse({"ok": False, "error": "请输入用户名"}, status_code=400)
    u["name"] = name
    _save_users()
    return {"ok": True, "name": name}


@app.post("/api/auth/forgot")
async def api_forgot(request: Request):
    """忘记密码：向注册的邮箱发重置验证码。"""
    d = await _body(request)
    contact = _norm_contact(d.get("contact"))
    if not contact or not _valid_contact(contact):
        return JSONResponse({"ok": False, "error": "请输入有效的邮箱或手机号"}, status_code=400)
    if "@" not in contact:
        return JSONResponse({"ok": False, "error": "手机号重置需短信服务，暂用邮箱"}, status_code=400)
    u = _find_by_contact(contact)
    if not u:
        return JSONResponse({"ok": False, "error": "该邮箱未注册"}, status_code=404)
    # 频率限制：60 秒内不能重复发
    if time.time() - CODES.get(contact, {}).get("sent_at", 0) < 60:
        return JSONResponse({"ok": False, "error": "发送太频繁，请稍后再试"}, status_code=429)
    if not _smtp_ready():
        return JSONResponse({"ok": False, "error": "邮件服务未配置，无法发送验证码"}, status_code=500)
    code = "%06d" % secrets.randbelow(1000000)
    CODES[contact] = {"code": code, "exp": time.time() + 600, "sent_at": time.time()}
    ok = _send_email(contact, "海克斯攻略站-重置密码", _make_code_html(code))
    if not ok:
        return JSONResponse({"ok": False, "error": "邮件发送失败，请稍后重试"}, status_code=500)
    return {"ok": True, "sent": True}   # 只提示已发送，绝不返回验证码


@app.post("/api/auth/reset")
async def api_reset(request: Request):
    """验证重置验证码并设置新密码。"""
    d = await _body(request)
    contact = _norm_contact(d.get("contact"))
    code = (d.get("code") or "").strip()
    password = d.get("password") or ""
    u = _find_by_contact(contact)
    if not u:
        return JSONResponse({"ok": False, "error": "该账号未注册"}, status_code=404)
    c = CODES.get(contact)
    if not c or c["code"] != code or c["exp"] < time.time():
        return JSONResponse({"ok": False, "error": "验证码错误或已过期"}, status_code=400)
    if len(password) < 6:
        return JSONResponse({"ok": False, "error": "新密码至少6位"}, status_code=400)
    u["salt"] = ""
    u["phash"] = _hash(password)
    CODES.pop(contact, None)
    _save_users()
    return {"ok": True}


@app.post("/api/auth/phone")
async def api_phone(request: Request):
    """绑定/解绑手机号（需登录）。绑定手机后可用该手机号登录；手机号唯一。"""
    u = _auth_user(request)
    if not u:
        return JSONResponse({"ok": False, "error": "未登录"}, status_code=401)
    d = await _body(request)
    phone = _norm_contact(d.get("phone"))
    if not phone:
        # 传空 = 解绑
        u["phone"] = ""
        _save_users()
        return {"ok": True, "phone": ""}
    if not re.match(r"^1[3-9]\d{9}$", phone):
        return JSONResponse({"ok": False, "error": "请输入正确的手机号（1开头11位）"}, status_code=400)
    owner = _find_by_phone(phone)
    if owner and owner["id"] != u["id"]:
        return JSONResponse({"ok": False, "error": "该手机号已被绑定"}, status_code=400)
    u["phone"] = phone
    _save_users()
    return {"ok": True, "phone": phone}


# ============ 用户偏好（存服务器，按账号同步）============
PREF_KEYS = ("bg", "bgImg", "pets", "theme")


@app.get("/api/auth/prefs")
async def api_prefs_get(request: Request):
    u = _auth_user(request)
    if not u:
        return JSONResponse({"ok": False, "error": "未登录"}, status_code=401)
    return {"ok": True, "prefs": {k: u.get(k, "") for k in PREF_KEYS}}


@app.post("/api/auth/prefs")
async def api_prefs_set(request: Request):
    u = _auth_user(request)
    if not u:
        return JSONResponse({"ok": False, "error": "未登录"}, status_code=401)
    d = await _body(request)
    for k in PREF_KEYS:
        if k in d:
            u[k] = d[k]
    _save_users()
    return {"ok": True, "prefs": {k: u.get(k, "") for k in PREF_KEYS}}


# ============ 管理员后台 ============
def _admin_required(req):
    u = _auth_user(req)
    if not u or not u.get("is_admin"):
        return None
    return u


@app.get("/api/admin/users")
async def api_admin_users(request: Request):
    u = _admin_required(request)
    if not u:
        return JSONResponse({"ok": False, "error": "需要管理员权限"}, status_code=403)
    users = [{"id": x["id"], "name": x.get("name"), "contact": x.get("contact"),
              "avatar": x.get("avatar", ""), "is_admin": bool(x.get("is_admin")),
              "owner": bool(_is_owner(x)), "created": x.get("created")} for x in USERS.values()]
    # 主管理员永远置顶，其次管理员，再普通；同级按注册时间倒序
    users.sort(key=lambda x: (0 if x["owner"] else (1 if x["is_admin"] else 2), -(x["created"] or 0)))
    return {"ok": True, "users": users}


@app.post("/api/admin/user/{uid}")
async def api_admin_user(request: Request, uid: str):
    u = _admin_required(request)
    if not u:
        return JSONResponse({"ok": False, "error": "需要管理员权限"}, status_code=403)
    d = await _body(request)
    tgt = USERS.get(uid)
    if not tgt:
        return JSONResponse({"ok": False, "error": "用户不存在"}, status_code=404)
    if "is_admin" in d:
        if not _is_owner(u):
            return JSONResponse({"ok": False, "error": "只有主管理员能设置/取消管理员"}, status_code=403)
        new_val = bool(d["is_admin"])
        if not new_val:
            # 保护：不能降低自己的管理员身份（误点导致自己被锁在后台外）
            if uid == u["id"]:
                return JSONResponse({"ok": False, "error": "不能降低自己的管理员身份"}, status_code=400)
            # 保护：至少保留一名管理员，防止把最后一个管理员降掉导致后台锁死
            admins = [x for x in USERS.values() if x.get("is_admin")]
            if len(admins) <= 1 and tgt.get("is_admin"):
                return JSONResponse({"ok": False, "error": "至少需要保留一名管理员"}, status_code=400)
        tgt["is_admin"] = new_val
    if d.get("name"):
        if tgt.get("is_admin") and not _is_owner(u):
            return JSONResponse({"ok": False, "error": "只有主管理员能修改管理员"}, status_code=403)
        tgt["name"] = str(d["name"]).strip() or tgt["name"]
    if d.get("password"):
        if tgt.get("is_admin") and not _is_owner(u):
            return JSONResponse({"ok": False, "error": "只有主管理员能重置管理员密码"}, status_code=403)
        tgt["salt"] = ""
        tgt["phash"] = _hash(d["password"])
    _save_users()
    return {"ok": True}


@app.post("/api/admin/delete/{uid}")
async def api_admin_delete(request: Request, uid: str):
    u = _admin_required(request)
    if not u:
        return JSONResponse({"ok": False, "error": "需要管理员权限"}, status_code=403)
    if uid == u["id"]:
        return {"ok": False, "error": "不能删除自己"}
    tgt = USERS.get(uid)
    if tgt and _is_owner(tgt):
        return {"ok": False, "error": "不能删除主管理员"}
    if tgt and tgt.get("is_admin") and not _is_owner(u):
        return {"ok": False, "error": "只有主管理员能删除管理员"}
    USERS.pop(uid, None)
    _save_users()
    return {"ok": True}
