"""每日风控自测：检查 WeGame 接口是否解除 8000022 限流（跑一次即可，不打重请求）。
用法：
  & "E:\\Deepseek Harness\\wegame-capture\\.venv\\Scripts\\python.exe" "E:\\Deepseek Harness\\wegame-capture\\test_api.py"
结果解读：error_code=0 且 battles>0 => 已解除，可恢复爬取；8000022 => 仍被限流，继续等。
"""
import glob
import json
import os

from curl_cffi import requests as creq

BASE = r"E:\Deepseek Harness\wegame-capture"
URL = "https://www.wegame.com.cn/api/v1/wegame.pallas.game.LolBattle/GetBattleList"


def ck_from(p):
    r = json.load(open(p, encoding="utf-8"))
    h = r["headers"]
    b = json.loads(r["body"])
    ck = {}
    for pair in h.get("cookie", "").split(","):
        if "=" in pair:
            k, v = pair.split("=", 1)
            ck[k.strip()] = v.strip()
    return ck, b


creds = {
    "C2(22:15)": r"E:\Deepseek Harness\wegame-capture\captured\REQ_GetBattleDetail_20260905_221525_967637.json",
    "C3(22:48)": r"E:\Deepseek Harness\wegame-capture\captured\REQ_GetBattleDetail_20260905_224816_508039.json",
}

ok = 0
for name, p in creds.items():
    if not os.path.exists(p):
        print(name, "-> 凭证文件不存在")
        continue
    ck, b = ck_from(p)
    for area in (1, 14, 17):
        c = creq.Session(impersonate="chrome124")
        c.headers.update({"trpc-caller": "wegame.pallas.web.LolBattle",
                          "referer": "https://www.wegame.com.cn/helper/lol/index.html"})
        c.cookies.update(ck)
        try:
            resp = c.post(URL, json={"account_type": 2, "area": area, "id": b["id"],
                                     "count": 3, "filter": "", "offset": 0,
                                     "from_src": b.get("from_src", "lol_helper")}, timeout=20)
            d = resp.json()
            code = d.get("result", {}).get("error_code")
            n = len(d.get("battles") or [])
            print("%s x area%d -> %s | %d场" % (name, area, code, n))
            if code == 0 and n > 0:
                ok += 1
        except Exception as e:
            print(name, "x area%d -> EXC" % area, e)

print("----")
if ok:
    print("[OK] 凭证有效（%d 个组合正常），可以爬取" % ok)
else:
    print("[BLOCKED] 错误码见上：8025009=凭证过期需重新抓包；8000022=风控未解除，继续等")
