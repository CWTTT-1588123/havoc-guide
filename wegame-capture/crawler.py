import glob
import json
import os
import time

from curl_cffi import requests as creq

BASE_DIR = r"E:\Deepseek Harness\wegame-capture"
OUT_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(OUT_DIR, exist_ok=True)

BASE_URL = "https://www.wegame.com.cn/api/v1/wegame.pallas.game.LolBattle/"
IMPERSONATE = os.environ.get("IMPERSONATE", "chrome124")


def _cookie_dict(cookiestr):
    ck = {}
    for pair in cookiestr.split(","):
        if "=" in pair:
            k, v = pair.split("=", 1)
            ck[k.strip()] = v.strip()
    return ck


def load_auth():
    files = sorted(glob.glob(os.path.join(BASE_DIR, "captured", "REQ_GetBattleDetail_*.json")))
    r = json.load(open(files[-1], encoding="utf-8"))  # 用最新的（重新抓包后的新cookie/token）
    h = r["headers"]
    b = json.loads(r["body"])
    cookies = _cookie_dict(h.get("cookie", ""))
    return cookies, b


COOKIES, AUTHBODY = load_auth()
TOKEN = AUTHBODY["id"]
ACCOUNT_TYPE = AUTHBODY.get("account_type", 2)
AREA = AUTHBODY.get("area", 1)
FROM_SRC = AUTHBODY.get("from_src", "lol_helper")

# 关键：用 curl_cffi impersonate 浏览器指纹，只补自定义头，cookie 走 cookies 参数
HEADERS = {
    "trpc-caller": "wegame.pallas.web.LolBattle",
    "referer": "https://www.wegame.com.cn/helper/lol/index.html",
}

_client = creq.Session(impersonate=IMPERSONATE)
_client.headers.update(HEADERS)
_client.cookies.update(COOKIES)


def post(endpoint, payload):
    resp = _client.post(BASE_URL + endpoint, json=payload, timeout=20)
    return resp.json()


def fetch_battle_list(offset, count=7):
    return post("GetBattleList", {
        "account_type": ACCOUNT_TYPE, "area": AREA, "id": TOKEN,
        "count": count, "filter": "", "offset": offset, "from_src": FROM_SRC,
    })


def fetch_detail(game_id):
    return post("GetBattleDetail", {
        "account_type": ACCOUNT_TYPE, "area": AREA, "id": TOKEN,
        "game_id": str(game_id), "from_src": FROM_SRC,
    })


def main():
    max_games = int(os.environ.get("MAX_GAMES", "10000"))
    delay = float(os.environ.get("DELAY", "0.35"))
    count = 7
    offset = int(os.environ.get("OFFSET", "0"))
    seen = set()
    for f in glob.glob(os.path.join(OUT_DIR, "detail_*.json")):
        try:
            d = json.load(open(f, encoding="utf-8"))
            seen.add(d.get("battle_detail", {}).get("game_id"))
        except Exception:
            pass
    fetched = 0
    empty_streak = 0
    while fetched < max_games:
        bl = fetch_battle_list(offset, count)
        code = bl.get("result", {}).get("error_code")
        if code != 0:
            print("[AUTH/ERR] error_code=%s — 可能 token/cookie 过期，请重新在 WeGame 里浏览一次刷新" % code)
            break
        battles = bl.get("battles") or []
        if not battles:
            empty_streak += 1
            if empty_streak >= 2:
                print("[done] 翻到底了 offset=%d" % offset)
                break
        else:
            empty_streak = 0
        for b in battles:
            # 优化：只在列表阶段挑出海克斯大乱斗（queue=2400），跳过其它模式，避免白请求详情
            if b.get("game_queue_id") != 2400:
                continue
            gid = str(b["game_id"])
            if gid in seen:
                continue
            try:
                det = fetch_detail(gid)
                c = det.get("result", {}).get("error_code")
                if c != 0:
                    print("[warn] detail err gid=%s code=%s" % (gid, c))
                    time.sleep(delay)
                    continue
                if (det.get("battle_detail", {}) or {}).get("game_mode") != "KIWI":
                    print("[skip] mode!=KIWI gid=%s" % gid)
                    time.sleep(delay)
                    continue
                with open(os.path.join(OUT_DIR, "detail_%s.json" % gid), "w", encoding="utf-8") as f:
                    json.dump(det, f, ensure_ascii=False)
                seen.add(gid)
                fetched += 1
                if fetched % 20 == 0:
                    print("[progress] fetched=%d offset=%d" % (fetched, offset))
            except Exception as e:
                print("[err] gid=%s %s" % (gid, e))
            time.sleep(delay)
        offset += count
    print("[done] 本次新抓=%d 场（累计 data/ 目录）" % fetched)


if __name__ == "__main__":
    main()
