"""爬虫暂停监视器：检测到爬虫停止（滑块/凭证过期/跑完）就弹窗提醒。
用法：
  python watch_crawl.py            # 持续监视，每 10 秒检查一次
  python watch_crawl.py --test     # 立即弹一个测试窗（20 秒自动关闭）

监视对象：crawl_a1_w1.log / crawl_a1_w2.log / crawl_a14.log（同目录下）
触发词：  [VERIFY-NEEDED]  滑块验证到期
          [AUTH-EXPIRED]   凭证过期
          [done]           队列跑完（饱和）
弹窗方式：WScript.Shell Popup（已验证能在本机桌面正常显示）
"""
import os
import subprocess
import sys
import time

BASE = r"E:\Deepseek Harness\wegame-capture"
LOGS = ["crawl_a1_w1.log", "crawl_a1_w2.log", "crawl_a14.log"]
MARKERS = {
    "[VERIFY-NEEDED]": "滑块验证到期，需要你在 WeGame 过一下滑块",
    "[AUTH-EXPIRED]": "登录凭证过期，需要重新点一场对局抓包",
    "[done]": "队列跑完（饱和），可以换区或停止",
}
CHECK_EVERY = 10  # 秒


def popup(title, text, seconds=60):
    """通过 PowerShell + WScript.Shell 弹置顶警告窗（非阻塞，seconds 秒后自动关）。"""
    ps = (
        "$ws = New-Object -ComObject WScript.Shell; "
        "$null = $ws.Popup('%s', %d, '%s', 48 + 4096)"
        % (text.replace("'", "''").replace("\n", "`n"), seconds, title)
    )
    try:
        subprocess.Popen(["powershell", "-NoProfile", "-Command", ps],
                         creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except Exception as e:
        print("[popup失败]", e)
        return False


def tail_from(path, start):
    """读取文件 start 偏移之后的新内容；文件变小(被新 run 覆盖)则从头读。"""
    try:
        size = os.path.getsize(path)
    except OSError:
        return "", start
    if size < start:
        start = 0
    if size == start:
        return "", start
    with open(path, encoding="utf-8", errors="replace") as f:
        f.seek(start)
        data = f.read()
    return data, size


def main():
    if "--test" in sys.argv:
        print("测试弹窗（20 秒自动关闭）…")
        popup("爬虫监视器测试", "弹窗功能正常！以后爬虫停了会这样提醒你。", 20)
        print("已发出弹窗指令")
        return

    print("爬虫监视器启动，监视：", ", ".join(LOGS), "| 每 %d 秒检查 | Ctrl+C 退出" % CHECK_EVERY)
    pos = {f: 0 for f in LOGS}        # 每个日志的读取偏移
    alerted = {f: 0 for f in LOGS}    # 每个日志已提醒到的偏移（避免重复弹）
    while True:
        try:
            for f in LOGS:
                p = os.path.join(BASE, f)
                if not os.path.exists(p):
                    continue
                data, pos[f] = tail_from(p, pos[f])
                if not data:
                    continue
                for marker, hint in MARKERS.items():
                    if marker in data:
                        # 只有新事件才弹（日志被新 run 覆盖变小后自动重置）
                        if pos[f] > alerted[f]:
                            alerted[f] = pos[f]
                            print("[检测到] %s: %s" % (f, marker))
                            popup("爬虫已暂停 - " + f,
                                  hint + "\n\n（解决后告诉助手，由助手重启爬虫）")
            time.sleep(CHECK_EVERY)
        except KeyboardInterrupt:
            print("监视器已退出")
            return
        except Exception as e:
            print("[监视异常]", e)
            time.sleep(CHECK_EVERY)


if __name__ == "__main__":
    main()
