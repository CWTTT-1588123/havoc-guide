r"""一键重抓凭证 · 第二步：清理环境 + 找新凭证 + 验证三区（爬虫由 AI 会话用托管后台任务拉起）。

用法（在你自己打开的 PowerShell 里跑）：
    & "E:\Deepseek Harness\wegame-capture\.venv\Scripts\python.exe" "E:\Deepseek Harness\wegame-capture\recap_off.py"

前提：先跑过 recap_on.py 并在 WeGame 里点开过一场对局。
"""
import glob
import json
import os
import subprocess
import sys
import time
import winreg

BASE = os.path.dirname(os.path.abspath(__file__))
VENV_PY = os.path.join(BASE, ".venv", "Scripts", "python.exe")
CERT = os.path.join(BASE, ".mitmproxy", "mitmproxy-ca-cert.cer")
PIDFILE = os.path.join(BASE, ".mitmproxy", "mitmweb.pid")
MARKER = os.path.join(BASE, ".mitmproxy", "last_req_detail.txt")
CAP = os.path.join(BASE, "captured")
URL = "https://www.wegame.com.cn/api/v1/wegame.pallas.game.LolBattle/GetBattleList"
PROXY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"


def set_proxy(enable):
    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, PROXY_KEY, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(k, "ProxyEnable", 0, winreg.REG_DWORD, 1 if enable else 0)
    winreg.CloseKey(k)


def kill_mitm():
    try:
        pid = int(open(PIDFILE, encoding="utf-8").read().strip())
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
        print("[1/5] mitmweb 已停止 (PID=%d)" % pid)
    except Exception:
        print("[1/5] mitmweb 停止（PID 文件缺失，可能已退出）")
    # 兜底：杀掉所有 run_mitmweb 的残留
    try:
        subprocess.run(["taskkill", "/F", "/FI", "IMAGENAME eq python.exe", "/FI",
                        "WINDOWTITLE eq *mitmweb*"], capture_output=True)
    except Exception:
        pass


def ck_from(p):
    r = json.load(open(p, encoding="utf-8"))
    h = r["headers"]
    b = json.loads(r["body"])
    ck = {}
    for pair in h.get("cookie", "").split(","):
        if "=" in pair:
            k2, v = pair.split("=", 1)
            ck[k2.strip()] = v.strip()
    return ck, b


def validate(path):
    """按 test_api.py 逻辑测 3 个大区，返回 (ok_count, 结果描述)。"""
    from curl_cffi import requests as creq
    ck, b = ck_from(path)
    ok = 0
    desc = []
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
            desc.append("area%d=%s/%d场" % (area, code, n))
            if code == 0 and n > 0:
                ok += 1
        except Exception as e:
            desc.append("area%d=EXC" % area)
    return ok, desc


def main():
    # 1. 清理环境
    kill_mitm()
    set_proxy(False)
    subprocess.run(["certutil", "-user", "-delstore", "Root", "mitmproxy"], capture_output=True)
    print("[2/5] 系统代理已关闭、mitmproxy 证书已删除")

    # 2. 找新凭证（对比 recap_on 时的标记）
    old = ""
    if os.path.exists(MARKER):
        old = open(MARKER, encoding="utf-8").read().strip()
    dets = sorted(glob.glob(os.path.join(CAP, "REQ_GetBattleDetail_*.json")), key=os.path.getmtime)
    if not dets:
        print("[3/5] ❌ captured 目录里没有任何 REQ_GetBattleDetail 凭证"); sys.exit(1)
    newest = os.path.basename(dets[-1])
    if newest != old:
        print("[3/5] 抓到新凭证:", newest)
    else:
        print("[3/5] ⚠ 没抓到新的 GetBattleDetail（详情页有缓存）→ 用最新列表 cookie + 旧 openid 合成")
        lists = sorted(glob.glob(os.path.join(CAP, "REQ_GetBattleList_*.json")), key=os.path.getmtime)
        if not lists:
            print("    ❌ 也没抓到列表请求，请再点一场对局后重跑 recap_off.py"); sys.exit(1)
        lst = json.load(open(lists[-1], encoding="utf-8"))
        det = json.load(open(dets[-1], encoding="utf-8"))
        synth = {"headers": lst["headers"], "body": det["body"]}
        out = os.path.join(CAP, "REQ_GetBattleDetail_%s_synth.json" % time.strftime("%Y%m%d_%H%M%S"))
        json.dump(synth, open(out, "w", encoding="utf-8"), ensure_ascii=False)
        dets = [out]
        newest = os.path.basename(out)
        print("    合成凭证:", newest)

    # 3. 验证
    ok, desc = validate(dets[-1])
    print("[4/5] 自测:", " ".join(desc))
    if not ok:
        print("    ❌ 凭证不可用：8025009=过期(重点一次对局重抓)；8000022=滑块(去客户端过滑块后重点)")
        sys.exit(1)

    # 4. 验证通过后不在这里拉起爬虫（分离子进程在用户环境会被回收，见 08_常见错误）；
    #    改为输出指引，由 AI 会话用托管后台任务拉起双线。
    req = "captured\\" + newest
    print("[5/5] 凭证有效，新凭证:", newest)
    print("    爬虫由 AI 会话用托管后台任务拉起（本脚本不再自动拉，分离进程会被回收）。")
    print("    请把下面这行参数发给 AI：")
    print("    REQ_FILE=%s" % req)
    print()
    print("✅ 完成。凭证已就绪；AI 会用: AREA=1 双线(WORKER=1/2) + PATCH_VERSION=16.17 + DELAY=0.3 拉起爬虫。")


if __name__ == "__main__":
    main()
