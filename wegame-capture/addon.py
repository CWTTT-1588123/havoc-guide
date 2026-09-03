import json
import os
import re
import time
from datetime import datetime

from mitmproxy import http

BASE = r"E:\Deepseek Harness\wegame-capture"
OUT = os.path.join(BASE, "captured")
os.makedirs(OUT, exist_ok=True)

MODE_OK = "KIWI"


def _ts():
    # Windows 的 time.strftime 不支持 %f（微秒），必须用 datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _save(name, data):
    ts = _ts()
    path = os.path.join(OUT, "%s_%s.json" % (name, ts))
    with open(path, "wb") as f:
        f.write(data if isinstance(data, bytes) else str(data).encode("utf-8"))
    return path


def _save_req(flow, tag):
    ts = _ts()
    path = os.path.join(OUT, "REQ_%s_%s.json" % (tag, ts))
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "url": flow.request.pretty_url,
            "method": flow.request.method,
            "headers": dict(flow.request.headers),
            "body": (flow.request.content or b"").decode("utf-8", "replace"),
        }, f, ensure_ascii=False, indent=2)
    return path


def response(flow: http.HTTPFlow):
    try:
        url = flow.request.pretty_url

        # rune 图标 URL -> 收集符文 string id
        if "/rune/" in url:
            m = re.search(r"/rune/([^/]+)_small\.png", url)
            if m:
                with open(os.path.join(OUT, "rune_ids.txt"), "a", encoding="utf-8") as fh:
                    fh.write(m.group(1) + "\n")

        # 1) 对局详情：只存海克斯大乱斗
        if "GetBattleDetail" in url:
            body = flow.response.content or b""
            mode = "?"
            try:
                j = json.loads(body)
                mode = (j.get("battle_detail", {}) or {}).get("game_mode", "?")
            except Exception:
                pass
            if str(mode) == MODE_OK:
                p = _save("GetBattleDetail", body)
                _save_req(flow, "GetBattleDetail")
                print("[cap-KIWI] saved %d bytes -> %s" % (len(body), p))
            else:
                print("[skip] mode=%s (非KIWI)" % mode)

        # 2) 对战列表（用于拿大批 game_id）
        if "GetBattleList" in url:
            _save("GetBattleList", flow.response.content or b"")
            _save_req(flow, "GetBattleList")
            print("[cap] GetBattleList saved %d bytes" % len(flow.response.content or b""))

        # 3) 英雄目录（championId -> 名字/头像）
        if "GetChampion" in url:
            _save("GetChampion", flow.response.content or b"")
            print("[cap] GetChampion saved %d bytes" % len(flow.response.content or b""))

        # 4) 任何可能是符文/强化目录的接口（非图片）
        low = url.lower()
        is_data = ("/rune/" not in url) or (not low.endswith((".png", ".jpg", ".webp")))
        if is_data and any(k in low for k in ("augment", "loadout", "catalog", "runelist", "runeconfig", "boon")):
            body = flow.response.content or b""
            if body.strip().startswith((b"{", b"[")):
                p = _save("RUNECAT", body)
                print("[cap] possible rune catalog -> %s (%d bytes)" % (p, len(body)))
    except Exception as e:
        print("[addon-error] %s" % e)
