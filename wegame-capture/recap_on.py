r"""一键重抓凭证 · 第一步：搭环境（信任证书 + 开系统代理 + 后台起 mitmweb）。

用法（在你自己打开的 PowerShell 里跑，不要在沙箱里跑）：
    & "E:\Deepseek Harness\wegame-capture\.venv\Scripts\python.exe" "E:\Deepseek Harness\wegame-capture\recap_on.py"

运行后 → 去 WeGame 点开一场海克斯大乱斗对局详情（有滑块就过）→ 运行 recap_off.py 收尾。
"""
import glob
import os
import subprocess
import sys
import time
import winreg

BASE = os.path.dirname(os.path.abspath(__file__))
VENV_PY = os.path.join(BASE, ".venv", "Scripts", "python.exe")
CERT = os.path.join(BASE, ".mitmproxy", "mitmproxy-ca-cert.cer")
CONFDIR = os.path.join(BASE, ".mitmproxy")
PIDFILE = os.path.join(CONFDIR, "mitmweb.pid")
MARKER = os.path.join(CONFDIR, "last_req_detail.txt")
LOG = os.path.join(BASE, "mitmweb.log")
CAP = os.path.join(BASE, "captured")

PROXY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"


def set_proxy(enable):
    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, PROXY_KEY, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(k, "ProxyEnable", 0, winreg.REG_DWORD, 1 if enable else 0)
    if enable:
        winreg.SetValueEx(k, "ProxyServer", 0, winreg.REG_SZ, "127.0.0.1:8080")
        winreg.SetValueEx(k, "ProxyOverride", 0, winreg.REG_SZ, "localhost;127.0.0.1;<local>")
    winreg.CloseKey(k)


def main():
    # 1. 信任 mitmproxy 证书
    r = subprocess.run(["certutil", "-user", "-addstore", "Root", CERT],
                       capture_output=True, text=True)
    print("[1/5] 信任证书:", "OK" if r.returncode == 0 else "注意：" + (r.stderr or r.stdout)[:100])

    # 2. 开系统代理 127.0.0.1:8080
    set_proxy(True)
    print("[2/5] 系统代理已开启 -> 127.0.0.1:8080")

    # 3. 记录当前最新凭证（收尾时判断是否抓到新的）
    dets = sorted(glob.glob(os.path.join(CAP, "REQ_GetBattleDetail_*.json")), key=os.path.getmtime)
    marker = os.path.basename(dets[-1]) if dets else ""
    with open(MARKER, "w", encoding="utf-8") as f:
        f.write(marker)
    print("[3/5] 已记录当前最新凭证:", marker or "(无)")

    # 4. 后台启动 mitmweb（分离进程，日志写 mitmweb.log）
    os.makedirs(CONFDIR, exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as fout:
        p = subprocess.Popen(
            [VENV_PY, os.path.join(BASE, "run_mitmweb.py")],
            cwd=BASE, stdout=fout, stderr=subprocess.STDOUT,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    with open(PIDFILE, "w") as f:
        f.write(str(p.pid))
    print("[4/5] mitmweb 已后台启动 (PID=%d, 日志 mitmweb.log)" % p.pid)

    # 5. 等端口就绪
    time.sleep(4)
    print("[5/5] 环境就绪")
    print()
    print(">>> 现在去 WeGame 点开一场大乱斗对局详情（有滑块就过），点完运行 recap_off.py <<<")


if __name__ == "__main__":
    main()
