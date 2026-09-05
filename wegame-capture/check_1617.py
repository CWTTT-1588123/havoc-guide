"""只读预览：统计 data/ 中 16.17 对局的场次/玩家记录/英雄分布（不写任何文件）。"""
import glob
import json
import os
import collections

DATA = r"E:\Deepseek Harness\wegame-capture\data"
VER = os.environ.get("PATCH_VERSION", "16.17")

games = 0
records = 0
champ_count = collections.Counter()
seen = set()
for f in sorted(glob.glob(os.path.join(DATA, "detail_*.json"))):
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    bd = d.get("battle_detail", {}) or {}
    if bd.get("game_mode") != "KIWI":
        continue
    if str(bd.get("game_server_version", "")).strip() != VER:
        continue
    gid = str(bd.get("game_id"))
    if gid in seen:
        continue
    seen.add(gid)
    games += 1
    for p in bd.get("player_details", []) or []:
        records += 1
        c = p.get("championId")
        if c:
            champ_count[c] += 1

print("版本:", VER)
print("16.17 对局场次:", games)
print("玩家记录数:", records)
print("涉及英雄数:", len(champ_count))
if champ_count:
    cnt = champ_count.most_common()
    print(">=10场的英雄数:", sum(1 for _, n in cnt if n >= 10))
    print(">=30场的英雄数:", sum(1 for _, n in cnt if n >= 30))
    print("场次前10英雄:", cnt[:10])
