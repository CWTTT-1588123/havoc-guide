"""
metadata.py —— 建立 ID -> 名字/头像 的元数据。
- 英雄 + 装备：用 Riot 官方 Data Dragon（中文），抓取后缓存到 processed/。
- 符文：从 processed/augment_names.json 读取（可手动/后续补充），缺省用占位。
"""
import json
import os
import urllib.request

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed")
os.makedirs(OUT_DIR, exist_ok=True)

DD = "https://ddragon.leagueoflegends.com/cdn/{ver}/data/zh_CN/{kind}.json"


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _latest_version():
    with urllib.request.urlopen("https://ddragon.leagueoflegends.com/api/versions.json", timeout=20) as resp:
        v = json.loads(resp.read().decode("utf-8"))
        return v[0]


def load_champions(cache=True):
    cache_path = os.path.join(OUT_DIR, "champion_names.json")
    if cache and os.path.exists(cache_path):
        return json.load(open(cache_path, encoding="utf-8"))
    ver = _latest_version()
    data = _get(DD.format(ver=ver, kind="champion"))
    mapping = {}
    for cid, c in data["data"].items():
        # c["key"] 是数字id字符串；c["name"] 中文名
        mapping.setdefault(str(c["key"]), {"name": c["name"], "id": cid, "title": c.get("title", "")})
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    return mapping


def load_items(cache=True):
    cache_path = os.path.join(OUT_DIR, "item_names.json")
    if cache and os.path.exists(cache_path):
        return json.load(open(cache_path, encoding="utf-8"))
    ver = _latest_version()
    data = _get(DD.format(ver=ver, kind="item"))
    mapping = {}
    for iid, c in data["data"].items():
        mapping[iid] = c.get("name", iid)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    return mapping


def load_augments(records_augments=None):
    """符文 ID -> 名字。读取 augment_names.json（可手填）；缺省用占位。"""
    path = os.path.join(OUT_DIR, "augment_names.json")
    mapping = {}
    if os.path.exists(path):
        mapping = json.load(open(path, encoding="utf-8"))
    # 把出现的但表里没有的符文补占位
    if records_augments:
        for a in records_augments:
            a = str(a)
            mapping.setdefault(a, {"name": "符文" + a, "quality": "", "desc": ""})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    return mapping


def main():
    import glob
    import os as _os
    records = []
    rp = os.path.join(OUT_DIR, "records.jsonl")
    if _os.path.exists(rp):
        with open(rp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    augids = sorted({a for r in records for a in r.get("augments", [])})
    champs = load_champions()
    items = load_items()
    augs = load_augments(augids)
    print("英雄数:", len(champs), "装备数:", len(items), "符文数(含占位):", len(augs))


if __name__ == "__main__":
    main()
