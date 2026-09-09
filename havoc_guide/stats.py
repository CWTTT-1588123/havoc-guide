"""
stats.py —— 从 records.jsonl 计算各项胜率统计，输出 processed/stats.json。
口径：
- 单符文胜率：WR(R|X) = 含R的对局中胜率；用 Wilson 下界排序（置信度+样本量），并标注样本量。
- 组合胜率：任意 3 符文子集的胜率（一局贡献 C(n,3) 个子集样本；≥20场收录，不足依次放宽到 10/5 场）；按"贝叶斯收缩+Wilson 下界"排序。
- 协同：WR(A&B) 相对该英雄基础胜率的增益（lift）。
- 对位：需要 champion_tags.json（可填），算 WR(R|X, 敌方含某标签) - WR(R|X, 全部)。
- 出装：该英雄最常用的装备组合 + 胜率。
"""
import collections
import itertools
import json
import os

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed")
RECORDS = os.path.join(OUT_DIR, "records.jsonl")
CHAMP_NAMES = os.path.join(OUT_DIR, "champion_names.json")
ITEM_NAMES = os.path.join(OUT_DIR, "item_names.json")
AUG_NAMES = os.path.join(OUT_DIR, "augment_names.json")
TAGS = os.path.join(OUT_DIR, "champion_tags.json")
# 成装（非小件）物品 ID 集合（来自 ddragon，排除组件/鞋/消耗品）
COMPLETED_ITEMS = os.path.join(OUT_DIR, "completed_items.json")

MIN_GAME = int(os.environ.get("MIN_GAME", "10"))      # 英雄/符文最小样本
MIN_TAG = int(os.environ.get("MIN_TAG", "8"))          # 对位最小样本
# 鞋子物品 ID（三件套不含鞋，鞋单独作为"匹配三件套"的最优鞋）
BOOT_IDS = {"1001", "3006", "3009", "3020", "3047", "3111", "3117", "3158", "2422", "3010", "3174", "3175", "1111"}
Z = 1.96
K = 25  # 先验强度（虚拟场次）：场次占比权重，越小样本越被拉向参照平均


def shrink(wins, games, prior, k=None):
    """先贝叶斯收缩(加先验伪样本)，再取 Wilson 下界——小样本既被拉向平均，又被置信区间压，场次权重更大。"""
    k = K if k is None else k
    if games <= 0:
        return prior
    ws = wins + k * prior
    gs = games + k
    return wilson_lower(ws, gs)


def wilson_lower(k, n):
    if n == 0:
        return 0.0
    p = k / n
    denom = 1 + Z * Z / n
    center = p + Z * Z / (2 * n)
    margin = Z * ((p * (1 - p) / n + Z * Z / (4 * n * n)) ** 0.5)
    return (center - margin) / denom


def load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def main():
    champs = load_json(CHAMP_NAMES, {})
    items = load_json(ITEM_NAMES, {})
    augs = load_json(AUG_NAMES, {})
    tags = load_json(TAGS, {})  # {champion_id: [tag,...]}
    completed = set(str(x) for x in load_json(COMPLETED_ITEMS, []))

    records = []
    with open(RECORDS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    def champ_name(cid):
        e = champs.get(str(cid), {})
        return e.get("name", "champ%s" % cid)

    def aug_name(aid):
        e = augs.get(str(aid), {})
        return e.get("name", "符文%s" % aid)

    def is_random_aug(aid):
        # A类：结果随机"拿强化符文"的赌博类（质变/潘朵拉），应从推荐板块排除
        e = augs.get(str(aid), {})
        nm = e.get("name", "")
        return ("质变" in nm) or ("潘朵拉" in nm)

    def is_boot(iid):
        sid = str(iid)
        if sid in BOOT_IDS:
            return True
        nm = items.get(sid, "")
        return ("靴" in nm) or ("boots" in nm.lower())

    def item_name(iid):
        return items.get(str(iid), str(iid))

    # ---- 冠军总览 ----
    champ_stat = collections.defaultdict(lambda: [0, 0])  # wins, games
    aug_global = collections.defaultdict(lambda: [0, 0])  # wins, games  (all champs)
    per_champ_aug = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    per_champ_combo = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    per_champ_pair = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    per_champ_combo_by_tags = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    per_champ_build = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    # tags: (champ, tag) -> (aug -> [win,game]) and (champ -> [win,game])
    tag_aug = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    tag_base = collections.defaultdict(lambda: [0, 0])

    for r in records:
        cid = r["champion_id"]
        win = r["win"]
        augs_r = sorted(r["augments"])
        items_r = r["items"]
        champ_stat[cid][0] += 1 if win else 0
        champ_stat[cid][1] += 1
        # 单符文（全局 + 分英雄）
        for a in augs_r:
            aug_global[a][0] += 1 if win else 0
            aug_global[a][1] += 1
            per_champ_aug[cid][a][0] += 1 if win else 0
            per_champ_aug[cid][a][1] += 1
        # 组合（任意 3 符文子集）：一局贡献 C(n,3) 个子集组合，样本量远大于"整套符文"精确匹配
        if len(augs_r) >= 3:
            for combo in itertools.combinations(augs_r, 3):
                per_champ_combo[cid][combo][0] += 1 if win else 0
                per_champ_combo[cid][combo][1] += 1
        # 协同（两两）
        for i in range(len(augs_r)):
            for j in range(i + 1, len(augs_r)):
                pair = tuple(sorted([augs_r[i], augs_r[j]]))
                per_champ_pair[cid][pair][0] += 1 if win else 0
                per_champ_pair[cid][pair][1] += 1
        # 出装（核心流派）：玩家按顺序最早出的三件套成装（非小件、非鞋），每套只记一次
        core = [x for x in items_r if str(x) in completed and not is_boot(x)]
        if len(core) >= 3:
            per_champ_build[cid][tuple(core[:3])][0] += 1 if win else 0
            per_champ_build[cid][tuple(core[:3])][1] += 1
        # 对位：敌方阵容标签（遍历敌方阵容出现的所有标签，覆盖更多阵容类型）
        if tags:
            tag_base[cid][0] += 1 if win else 0
            tag_base[cid][1] += 1
            enemy_tags = set()
            for ec in r["enemy_champs"]:
                enemy_tags.update(tags.get(str(ec), []))
            for a in augs_r:
                for t in enemy_tags:
                    tag_aug[(cid, t)][a][0] += 1 if win else 0
                    tag_aug[(cid, t)][a][1] += 1

    # 全局平均胜率（作为英雄榜/全局符文的收缩参照）
    _tw = sum(v[0] for v in champ_stat.values())
    _tg = sum(v[1] for v in champ_stat.values())
    global_prior = _tw / _tg if _tg else 0.5

    # 汇总输出
    out = {"meta": {"records": len(records), "min_game": MIN_GAME}}
    champions = []
    champion_detail = {}

    for cid, (wins, games) in champ_stat.items():
        if games < MIN_GAME:
            continue
        wr = wins / games
        base = wr  # 该英雄基础胜率，作为其符文/组合/协同/出装/克制的收缩参照
        champions.append({
            "id": str(cid), "name": champ_name(cid), "wins": wins, "games": games,
            "wr": round(wr, 4), "wilson": round(shrink(wins, games, global_prior), 4),
        })
        # 单符文推荐
        augs_rec = []
        for a, (aw, ag) in per_champ_aug[cid].items():
            if is_random_aug(a):
                continue
            if ag < MIN_GAME:
                continue
            if ag < 3:
                continue
            augs_rec.append({
                "id": str(a), "name": aug_name(a), "wins": aw, "games": ag,
                "wr": round(aw / ag, 4), "wilson": round(shrink(aw, ag, base), 4),
            })
        augs_rec.sort(key=lambda x: (-x["wilson"], -x["games"]))
        # 组合（任意 3 符文子集；≥20 场收录，不足依次放宽到 10/5 场，最多 20 条）
        todo = []
        for combo, (cw, cg) in per_champ_combo[cid].items():
            if any(is_random_aug(x) for x in combo):
                continue
            todo.append({"combo": combo, "cw": cw, "cg": cg, "score": shrink(cw, cg, base)})
        todo.sort(key=lambda x: (-x["score"], -x["cg"]))
        combos = []
        for min_cg in (20, 10, 5):
            picked = [it for it in todo if it["cg"] >= min_cg]
            if picked:
                for it in picked[:20]:
                    combos.append({"augments": [str(x) for x in it["combo"]], "wins": it["cw"], "games": it["cg"],
                                   "wr": round(it["cw"] / it["cg"], 4), "wilson": round(it["score"], 4)})
                break
        # 协同
        synergy = []
        for pair, (sw, sg) in per_champ_pair[cid].items():
            if is_random_aug(pair[0]) or is_random_aug(pair[1]):
                continue
            if sg < 5:  # 提高最小样本，减少小样本噪音
                continue
            lift = (sw / sg) - base
            synergy.append({
                "a": str(pair[0]), "b": str(pair[1]),
                "wins": sw, "games": sg, "wr": round(sw / sg, 4),
                "lift": round(lift, 4),
                "wilson": round(shrink(sw, sg, base), 4),
            })
        synergy.sort(key=lambda x: (-x["wilson"], -x["games"]))
        synergy = synergy[:15]
        # 出装
        # 出装（核心流派）：两件不同才算不同套；共享≥2件视为同一套聚合一并；≥5场才收录；Wilson 综合胜率
        all_combos = []
        for core3, (bw, bg) in per_champ_build[cid].items():
            all_combos.append({"items": set(core3), "seq": list(core3), "wins": bw, "games": bg})
        clusters = []
        for c in sorted(all_combos, key=lambda x: -x["games"]):
            merged = False
            for cl in clusters:
                if len(c["items"] & cl["rep_items"]) >= 2:
                    cl["wins"] += c["wins"]
                    cl["games"] += c["games"]
                    merged = True
                    break
            if not merged:
                clusters.append({"rep_items": set(c["items"]), "seq": list(c["seq"]), "wins": c["wins"], "games": c["games"]})
        builds = []
        for cl in clusters:
            if cl["games"] < 10:
                continue
            bw, bg = cl["wins"], cl["games"]
            builds.append({
                "items": [str(x) for x in cl["seq"]],
                "item_names": [item_name(x) for x in cl["seq"]],
                "wins": bw, "games": bg, "wr": round(bw / bg, 4),
                "wilson": round(shrink(bw, bg, base), 4),
            })
        builds.sort(key=lambda x: (-x["wilson"], -x["games"]))
        builds = builds[:15]
        # 对位（若有标签）——先按敌方标签找最优符文，再按符文聚合；用收缩后的符文胜率算 lift
        counters = []
        if tags:
            ba, bg = tag_base[cid]
            bw = ba / bg if bg else 0
            best_per_tag = {}  # tag -> best augment entry
            for (c, t), da in tag_aug.items():
                if c != cid:
                    continue
                for a, (aw, ag) in da.items():
                    if is_random_aug(a):
                        continue
                    if ag < MIN_TAG:
                        continue
                    awr = aw / ag   # 克制用原始胜率（不算收缩），保留更多克制类别
                    lift = awr - bw
                    if lift <= 0:  # 只推荐"比该英雄平均胜率更高"的克制，负增益无意义
                        continue
                    cur = best_per_tag.get(t)
                    if cur is None or lift > cur["lift"]:
                        best_per_tag[t] = {
                            "augment": str(a), "name": aug_name(a),
                            "wins": aw, "games": ag, "wr": round(aw / ag, 4), "lift": round(lift, 4),
                        }
            # 按符文聚合，合并它能克制的敌方标签
            rune_map = {}
            for t, e in best_per_tag.items():
                k = e["augment"]
                ent = rune_map.setdefault(k, {"tagset": set(), "wr": 0, "lift": float("-inf"), "wins": 0, "games": 0, "name": e["name"]})
                ent["tagset"].add(t)
                if e["lift"] > ent["lift"]:
                    ent["lift"] = e["lift"]; ent["wr"] = e["wr"]; ent["wins"] = e["wins"]; ent["games"] = e["games"]
            for k, e in rune_map.items():
                counters.append({
                    "tag": "/".join(sorted(e["tagset"])), "augment": k, "augment_name": e["name"],
                    "wins": e["wins"], "games": e["games"], "wr": round(e["wr"], 4), "lift": round(e["lift"], 4),
                })
            counters.sort(key=lambda x: -x["lift"])
            counters = counters[:15]
        champion_detail[str(cid)] = {
            "name": champ_name(cid),
            "overall": {"wr": round(wr, 4), "games": games, "wins": wins},
            "augments": augs_rec[:30],
            "combos": combos,
            "synergy": synergy,
            "builds": builds,
            "counters": counters,
        }

    champions.sort(key=lambda x: (-x["wilson"], -x["games"]))
    out["champions"] = champions
    out["champion_detail"] = champion_detail

    # 全局符文
    augs_global = []
    for a, (aw, ag) in aug_global.items():
        if is_random_aug(a):
            continue
        if ag < MIN_GAME:
            continue
        augs_global.append({
            "id": str(a), "name": aug_name(a), "wins": aw, "games": ag,
            "wr": round(aw / ag, 4), "wilson": round(shrink(aw, ag, global_prior), 4),
        })
    augs_global.sort(key=lambda x: (-x["wilson"], -x["games"]))
    out["augments_global"] = augs_global

    with open(os.path.join(OUT_DIR, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("champions:", len(out["champions"]), "| global augments:", len(out["augments_global"]))


if __name__ == "__main__":
    main()
