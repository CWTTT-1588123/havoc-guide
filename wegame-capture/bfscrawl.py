import glob
import json
import os
import re
import time
import base64

from curl_cffi import requests as creq

BASE_DIR = r"E:\Deepseek Harness\wegame-capture"
OUT_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(OUT_DIR, exist_ok=True)

PLAYERS_FILE = os.path.join(BASE_DIR, "players_seen.json")
HIDDEN_FILE = os.path.join(BASE_DIR, "hidden_players.json")
BASE_URL = "https://www.wegame.com.cn/api/v1/wegame.pallas.game.LolBattle/"
IMPERSONATE = os.environ.get("IMPERSONATE", "chrome124")
PATCH_VERSION = os.environ.get("PATCH_VERSION", "16.16")  # 只收指定补丁版本（默认16.16）

# —— 多账号/多大区支持（2026-09 为黑色玫瑰 area=10 增加）——
# REQ_FILE   : 指定用哪份抓包凭证（默认=最新一份）。多账号同时爬时每个进程指自己的凭证。
# AREA       : 覆盖抓包里的 area（默认用抓包自带的大区）。
# SEED_FROM_GAMES : 是否从 data/ 现有对局补种子玩家（新大区应设 0，避免混入其他大区玩家）。
REQ_FILE = os.environ.get("REQ_FILE", "")
AREA_ENV = os.environ.get("AREA", "")
SEED_FROM_GAMES = os.environ.get("SEED_FROM_GAMES", "1") != "0"
WORKER = os.environ.get("WORKER", "")   # 每区多进程分片：状态文件名加 _w<WORKER> 后缀


def _state_file(name):
    """状态文件名：默认区=原名；显式AREA=加_a<area>；多进程分片=再加_w<worker>。"""
    base = name
    if AREA_ENV:
        base = "%s_a%s" % (name, AREA_ENV)
    if WORKER:
        base = base + "_w" + WORKER
    return os.path.join(BASE_DIR, base + ".json")


def cookie_dict(s):
    d = {}
    for p in s.split(","):
        if "=" in p:
            k, v = p.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def load_auth():
    if REQ_FILE:
        files = [REQ_FILE]
    else:
        files = sorted(glob.glob(os.path.join(BASE_DIR, "captured", "REQ_GetBattleDetail_*.json")))
    r = json.load(open(files[-1], encoding="utf-8"))  # 指定凭证或最新（重新抓包后的新cookie/token）
    h = r["headers"]
    b = json.loads(r["body"])
    return cookie_dict(h.get("cookie", "")), b


COOKIES, AUTHBODY = load_auth()
OWNER_ID = AUTHBODY["id"]  # 当前账号的 id（作为 "查看者" 身份去调 GetBattleDetail）
ACCOUNT_TYPE = AUTHBODY.get("account_type", 2)
AREA = int(AREA_ENV) if AREA_ENV else AUTHBODY.get("area", 1)   # 大区：显式覆盖 > 抓包自带
FROM_SRC = AUTHBODY.get("from_src", "lol_helper")

PLAYERS_FILE = _state_file("players_seen")
HIDDEN_FILE = _state_file("hidden")

_client = creq.Session(impersonate=IMPERSONATE)
_client.headers.update({
    "trpc-caller": "wegame.pallas.web.LolBattle",
    "referer": "https://www.wegame.com.cn/helper/lol/index.html",
})
_client.cookies.update(COOKIES)


def post(endpoint, payload):
    resp = _client.post(BASE_URL + endpoint, json=payload, timeout=20)
    return resp.json()


def player_battles(player_id, offset, count=7):
    # id = 被查询玩家的 openid
    return post("GetBattleList", {
        "account_type": ACCOUNT_TYPE, "area": AREA, "id": player_id,
        "count": count, "filter": "", "offset": offset, "from_src": FROM_SRC,
    })


def detail(game_id):
    # GetBattleDetail 的 id 用"查看者"(OWNER_ID), game_id 是目标对局
    return post("GetBattleDetail", {
        "account_type": ACCOUNT_TYPE, "area": AREA, "id": OWNER_ID,
        "game_id": str(game_id), "from_src": FROM_SRC,
    })


def save_players(players):
    # 原子写：先写临时文件再替换，避免中途被杀导致状态文件损坏
    tmp = PLAYERS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(list(players), f, ensure_ascii=False)
    os.replace(tmp, PLAYERS_FILE)


def load_players():
    if os.path.exists(PLAYERS_FILE):
        with open(PLAYERS_FILE, encoding="utf-8-sig") as f:
            return set(json.load(f))
    return set()


def record_hidden(pid, code):
    hidden = {}
    if os.path.exists(HIDDEN_FILE):
        with open(HIDDEN_FILE, encoding="utf-8-sig") as f:
            hidden = json.load(f)
    hidden[pid] = {"error_code": code, "time": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(HIDDEN_FILE, "w", encoding="utf-8") as f:
        json.dump(hidden, f, ensure_ascii=False)


def seed_from_games(seen):
    # 从 data/ 对局里提取玩家 openid 作为种子。
    # 多区并存：显式 AREA 时种本区文件（area=1 → 无前缀 detail_*.json；其他区 → detail_a<area>_*.json），避免跨区污染。
    if AREA_ENV and AREA_ENV != "1":
        pattern = os.path.join(OUT_DIR, "detail_a%s_*.json" % AREA_ENV)
        skip_prefixed = False
    else:
        pattern = os.path.join(OUT_DIR, "detail_*.json")
        skip_prefixed = True
    for f in glob.glob(pattern):
        if skip_prefixed and os.path.basename(f).startswith("detail_a"):
            continue
        try:
            d = json.load(open(f, encoding="utf-8"))
            for p in (d.get("battle_detail", {}) or {}).get("player_details", []):
                o = p.get("openid")
                if o:
                    seen.add(o)
        except Exception:
            pass


RE_DETAIL = re.compile(r"^detail_(?:a\d+_)?(\d+)\.json$")


def scan_seen_games():
    """扫描 data/ 建立"已抓对局"集合：文件名即 detail_[a<区>_]<game_id>.json，优先从文件名提取（秒级），
    仅对文件名不规范的少数文件回退解析 JSON（旧实现逐个 json.load 9万+ 文件，冷启动要 2~4 分钟）。"""
    seen = set()
    t0 = time.time()
    files = glob.glob(os.path.join(OUT_DIR, "detail_*.json"))
    fallback = 0
    for f in files:
        m = RE_DETAIL.match(os.path.basename(f))
        if m:
            seen.add(m.group(1))
            continue
        fallback += 1
        try:
            d = json.load(open(f, encoding="utf-8"))
            gid = (d.get("battle_detail", {}) or {}).get("game_id")
            if gid is not None:
                seen.add(str(gid))
        except Exception:
            pass
    print("[init] seen_games=%d（%d 个文件，回退解析 %d 个，耗时 %.1fs）"
          % (len(seen), len(files), fallback, time.time() - t0), flush=True)
    return seen


def main():
    max_games = int(os.environ.get("MAX_GAMES", "2000"))             # 本次新增对局预算
    max_players = int(os.environ.get("MAX_PLAYERS", "3000"))         # 本次扩展玩家上限
    max_pages = int(os.environ.get("MAX_PAGES_PER_PLAYER", "4"))     # 每个玩家最多翻几页
    delay = float(os.environ.get("DELAY", "0.3"))
    count = 7

    print("[start] area=%s patch=%s auth=%s max_games=%d max_players=%d pages=%d"
          % (AREA, PATCH_VERSION, (REQ_FILE or "最新抓包"), max_games, max_players, max_pages), flush=True)

    seen_players = load_players()
    if SEED_FROM_GAMES:
        seed_from_games(seen_players)   # 新大区(AREA/SEED_FROM_GAMES=0)不混入其他大区的玩家种子
    seen_players.add(OWNER_ID)  # 永远含自己
    queue = list(seen_players)

    seen_games = scan_seen_games()

    new_games = 0
    processed = 0
    while queue and new_games < max_games and processed < max_players:
        pid = queue.pop()
        processed += 1
        for page in range(max_pages):
            offset = page * count
            try:
                bl = player_battles(pid, offset, count)
            except Exception as e:
                print("[err] player=%s list %s" % (pid, e), flush=True)
                break
            code = bl.get("result", {}).get("error_code")
            if code == 8025009:
                print("[AUTH-EXPIRED] 登录凭证过期，停止本次抓取（需重新抓包刷新 cookie）| player=%s" % pid, flush=True)
                return
            if code == 8000022:
                print("[VERIFY-NEEDED] 触发滑块验证，停止本次抓取（需在客户端过滑块后重跑）| player=%s" % pid, flush=True)
                return
            if code != 0:
                record_hidden(pid, code)
                print("[hidden] player=%s error_code=%s" % (pid, code), flush=True)
                break
            battles = bl.get("battles") or []
            if not battles:
                break
            for b in battles:
                if b.get("game_queue_id") != 2400:
                    continue
                gid = str(b["game_id"])
                if gid in seen_games:
                    continue
                try:
                    det = detail(gid)
                    if det.get("result", {}).get("error_code") != 0:
                        continue
                    if (det.get("battle_detail", {}) or {}).get("game_mode") != "KIWI":
                        seen_games.add(gid)
                        continue
                    if str((det.get("battle_detail", {}) or {}).get("game_server_version", "")).strip() != PATCH_VERSION:
                        seen_games.add(gid)
                        continue
                    # 多区并存：显式指定 AREA 时文件名带区前缀，避免与其他大区对局ID冲突互相覆盖
                    fname = "detail_a%s_%s.json" % (AREA, gid) if AREA_ENV else "detail_%s.json" % gid
                    with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
                        json.dump(det, f, ensure_ascii=False)
                    seen_games.add(gid)
                    new_games += 1
                    for p in (det.get("battle_detail", {}) or {}).get("player_details", []):
                        o = p.get("openid")
                        if o and o not in seen_players:
                            seen_players.add(o)
                            queue.append(o)
                    if new_games % 25 == 0:
                        save_players(seen_players)   # 每25场也存一次状态，防意外
                        print("[progress] games=%d players_seen=%d queue=%d" % (new_games, len(seen_players), len(queue)), flush=True)
                except Exception as e:
                    print("[err] gid=%s %s" % (gid, e), flush=True)
                time.sleep(delay)
            if new_games >= max_games:
                break
            time.sleep(0.1)
        if processed % 50 == 0:
            save_players(seen_players)
        if new_games >= max_games:
            break
    save_players(seen_players)
    print("[done] 新增对局=%d 处理玩家=%d 累计seen玩家=%d" % (new_games, processed, len(seen_players)), flush=True)


if __name__ == "__main__":
    main()
