"""
build_tags_v2.py —— 系统化补全英雄标签。
- 用 Riot DDragon 的 role(角色) 和 attackRange(攻击距离) 自动推导：远程/近战、脆皮/坦克/刺客。
- 召唤物/治疗 用人工名单补充。
- 输出 processed/champion_tags.json（覆盖全部英雄）。
"""
import json
import os
import urllib.request

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed")
DD = "https://ddragon.leagueoflegends.com/cdn/{ver}/data/zh_CN/champion.json"


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _ver():
    with urllib.request.urlopen("https://ddragon.leagueoflegends.com/api/versions.json", timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))[0]


# 召唤物英雄（ID）
SUMMONERS = [90, 74, 83, 143, 60, 427, 1, 268]
# 治疗/护盾辅助（ID）
HEALERS = [16, 267, 37, 117, 40, 44, 350, 902, 497, 427]
# 手动修正：某些角色标签想覆盖的，可加 {id: [tags]}
OVERRIDE = {}


def main():
    data = _get(DD.format(ver=_ver()))
    tags = {}
    for cid, c in data["data"].items():
        cid = str(c["key"])
        tags[cid] = []
        role = c.get("tags", [])
        ar = (c.get("stats", {}) or {}).get("attackrange", 0) or 0
        # 远程/近战
        ranged = ar >= 400
        tags[cid].append("远程" if ranged else "近战")
        # 脆皮 / 坦克 / 刺客（按角色）
        if "Marksman" in role or "Mage" in role or "Assassin" in role:
            tags[cid].append("脆皮")
        if "Tank" in role or "Fighter" in role:
            tags[cid].append("坦克")
        if "Assassin" in role:
            tags[cid].append("刺客")
        # 人工补充
        if int(cid) in SUMMONERS:
            tags[cid].append("召唤物")
        if int(cid) in HEALERS:
            tags[cid].append("治疗")
    # 手动覆盖
    for cid, lst in OVERRIDE.items():
        tags[str(cid)] = list(dict.fromkeys(lst))
    # 去重保序
    tags = {k: list(dict.fromkeys(v)) for k, v in tags.items()}
    with open(os.path.join(OUT_DIR, "champion_tags.json"), "w", encoding="utf-8") as f:
        json.dump(tags, f, ensure_ascii=False, indent=2)
    print("已覆盖英雄数:", len(tags))
    # 统计各类别数量
    from collections import Counter
    cnt = Counter(t for v in tags.values() for t in v)
    print("各类别数量:", dict(cnt))


if __name__ == "__main__":
    main()
