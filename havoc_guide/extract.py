"""
extract.py —— 把抓到的原始对局 JSON 清洗成结构化"玩家记录"。
输出：processed/meta.json（汇总）+ processed/records.jsonl（每行=一场对局里的一个玩家）。
"""
import glob
import json
import os
import urllib.parse

DATA_DIR = r"E:\Deepseek Harness\wegame-capture\data"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed")
os.makedirs(OUT_DIR, exist_ok=True)

# 只保留指定补丁版本的对局（默认 16.16），可用环境变量 PATCH_VERSION 覆盖
VERSION = os.environ.get("PATCH_VERSION", "16.16")


def unquote_name(s):
    try:
        return urllib.parse.unquote(s or "")
    except Exception:
        return s


def iter_games(data_dir=DATA_DIR):
    for f in sorted(glob.glob(os.path.join(data_dir, "detail_*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        bd = d.get("battle_detail", {}) or {}
        if bd.get("game_mode") != "KIWI":
            continue
        if str(bd.get("game_server_version", "")).strip() != VERSION:
            continue
        yield f, d, bd


def build_records():
    games = 0
    records = []
    seen_games = set()
    for f, d, bd in iter_games():
        gid = str(bd.get("game_id"))
        if gid in seen_games:
            continue
        seen_games.add(gid)
        try:
            teams = {str(t["teamId"]): (str(t["win"]).lower() == "win") for t in bd.get("team_details", [])}
            players = bd.get("player_details", [])
        except Exception:
            continue
        if not players:
            continue
        games += 1
        # 按 teamId 分组，便于构建同队/敌对阵容
        by_team = {}
        for p in players:
            by_team.setdefault(str(p.get("teamId")), []).append(p)
        for p in players:
            tid = str(p.get("teamId"))
            allies = [q["championId"] for q in by_team.get(tid, []) if q.get("championId") != p.get("championId")]
            enemies = [q["championId"] for q in players if str(q.get("teamId")) != tid]
            augs = [p.get("playerAugment%d" % i, 0) for i in range(1, 7)]
            augs = [a for a in augs if a]
            items = [p.get("item%d" % i, 0) for i in range(7)]
            items = [i for i in items if i]
            rec = {
                "game_id": gid,
                "version": str(bd.get("game_server_version", "")),
                "start_time": str(bd.get("game_start_time", "")),
                "duration": bd.get("game_time_played"),
                "champion_id": p.get("championId"),
                "player_name": unquote_name(p.get("name")),
                "level": p.get("level"),
                "augments": augs,
                "items": items,
                "kills": p.get("championsKilled"),
                "assists": p.get("assists"),
                "deaths": p.get("numDeaths"),
                "gold": p.get("goldEarned"),
                "score": p.get("gameScore"),
                "damage": (p.get("physicalDamageToChampions", 0) or 0) + (p.get("magicDamageToChampions", 0) or 0),
                "team_id": tid,
                "win": teams.get(tid, False),
                "ally_champs": allies,
                "enemy_champs": enemies,
            }
            records.append(rec)
    return games, records


def main():
    games, records = build_records()
    rec_path = os.path.join(OUT_DIR, "records.jsonl")
    with open(rec_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    meta = {
        "games": games,
        "player_records": len(records),
        "distinct_champions": len({r["champion_id"] for r in records}),
        "distinct_augments": len({a for r in records for a in r["augments"]}),
        "output": rec_path,
    }
    with open(os.path.join(OUT_DIR, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
