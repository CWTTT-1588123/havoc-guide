import os
import sys

# 用 python -m mitmproxy.tools.main 的方式启动 mitmweb，
# 绕开被 Windows 应用程序控制策略拦截的 mitmweb.exe。
from mitmproxy.tools.main import mitmweb

base = r"E:\Deepseek Harness\wegame-capture"
os.makedirs(os.path.join(base, ".mitmproxy"), exist_ok=True)

sys.argv = [
    "mitmweb",
    "--set", "confdir=" + os.path.join(base, ".mitmproxy"),
    "--scripts", os.path.join(base, "addon.py"),   # 加载自动保存插件
    "--listen-port", "8080",      # mitmproxy 代理端口（WeGame 走这里）
    "--web-port", "8081",        # 网页查看界面端口
    "--web-host", "127.0.0.1",
]
mitmweb()
