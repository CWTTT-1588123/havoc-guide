import glob
import json
import os
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


def cookie_dict(s):
    d = {}
    for p in s.split(","):
        if "=" in p:
            k, v = p.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def load_auth():
    files = sorted(glob.glob(os.path.join(BASE_DIR, "captured", "REQ_GetBattleDetail_*.json")))
    r = json.load(open(files[-1], encoding="utf-8"))  # 用最新的（重新抓包后的新cookie/token）
    h = r["headers"]
    b = json.loads(r["body"])
    return cookie_dict(h.get("cookie", "")), b


COOKIES, AUTHBODY = load_auth()
OWNER_ID = AUTHBODY["id"]  # 当前账号的 id（作为 "查看者" 身份去调 GetBattleDetail）
ACCOUNT_TYPE = AUTHBODY.get("account_type", 2)
AREA = AUTHBODY.get("area", 1)
FROM_SRC = AUTHBODY.get("from_src", "lol_helper")

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
    with open(PLAYERS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(players), f, ensure_ascii=False)


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
    # 从现有 data/ 对局里提取所有玩家 openid 作为种子
    for f in glob.glob(os.path.join(OUT_DIR, "detail_*.json")):
        try:
            d = json.load(open(f, encoding="utf-8"))
            for p in (d.get("battle_detail", {}) or {}).get("player_details", []):
                o = p.get("openid")
                if o:
                    seen.add(o)
        except Exception:
            pass


def main():
    max_games = int(os.environ.get("MAX_GAMES", "2000"))             # 本次新增对局预算
    max_players = int(os.environ.get("MAX_PLAYERS", "3000"))         # 本次扩展玩家上限
    max_pages = int(os.environ.get("MAX_PAGES_PER_PLAYER", "4"))     # 每个玩家最多翻几页
    delay = float(os.environ.get("DELAY", "0.3"))
    count = 7

    seen_players = load_players()
    seed_from_games(seen_players)
    seen_players.add(OWNER_ID)  # 永远含自己
    queue = list(seen_players)

    seen_games = set()
    for f in glob.glob(os.path.join(OUT_DIR, "detail_*.json")):
        try:
            d = json.load(open(f, encoding="utf-8"))
            seen_games.add(d.get("battle_detail", {}).get("game_id"))
        except Exception:
            pass

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
                    with open(os.path.join(OUT_DIR, "detail_%s.json" % gid), "w", encoding="utf-8") as f:
                        json.dump(det, f, ensure_ascii=False)
                    seen_games.add(gid)
                    new_games += 1
                    for p in (det.get("battle_detail", {}) or {}).get("player_details", []):
                        o = p.get("openid")
                        if o and o not in seen_players:
                            seen_players.add(o)
                            queue.append(o)
                    if new_games % 25 == 0:
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
