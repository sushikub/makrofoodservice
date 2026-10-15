"""Select Makro Food Service branches to open as darkstore hubs for 7-Eleven stores.

Rules
- Bangkok + vicinity (first 32 rows of the Makro file): every hub serves 280-320
  7-Eleven stores within 5 km, and each store belongs to one hub only.
  The script tries every combination of candidate hubs, keeps the largest
  feasible set, then the one that serves the most stores.
- Upcountry: one hub per province, the branch with the most stores within 5 km.

Usage:  python scripts/analyze.py
Output: output/hub_summary.csv, output/store_assignment.csv
"""
import itertools
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RADIUS_KM = 5.0
LO, HI = 280, 320
N_BKK = 32  # rows 1-32 of the Makro file are Bangkok + vicinity

PROVINCE = {
    "Hua Hin": "ประจวบคีรีขันธ์", "Cha-Am": "เพชรบุรี", "Pattaya N.": "ชลบุรี",
    "Amata Nakhon": "ชลบุรี", "Laem Chabang": "ชลบุรี", "Ko Chang": "ตราด",
    "Ban Phe": "ระยอง", "Phitsanulok 2": "พิษณุโลก", "Sirimangkalajarn": "เชียงใหม่",
    "Khon Kaen 2": "ขอนแก่น", "Nakhon Ratchsima 2": "นครราชสีมา", "Pakchong": "นครราชสีมา",
    "Ao Nang": "กระบี่", "Karon": "ภูเก็ต", "Patong": "ภูเก็ต", "Rawai": "ภูเก็ต",
    "Lamai": "สุราษฎร์ธานี", "Ko Pha-Ngan": "สุราษฎร์ธานี", "Ko Samui": "สุราษฎร์ธานี",
}


def distance_matrix(m, s):
    """Haversine distance (km), shape = (n_makro, n_store)."""
    la1, lo1 = np.radians(m.lat.values)[:, None], np.radians(m.lng.values)[:, None]
    la2, lo2 = np.radians(s.lat.values)[None, :], np.radians(s.lng.values)[None, :]
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.sqrt(a))


def max_flow(W, hubs, cap):
    G = nx.DiGraph()
    for h in hubs:
        G.add_edge("s", f"h{h}", capacity=cap)
        for st in np.where(W[h])[0]:
            G.add_edge(f"h{h}", f"s{st}", capacity=1)
    for st in np.where(W[list(hubs)].any(0))[0]:
        G.add_edge(f"s{st}", "t", capacity=1)
    return nx.maximum_flow_value(G, "s", "t")


def assign(W, D, hubs, n_store):
    """Min-cost assignment: every hub gets LO..HI stores, maximise coverage, then shortest distance."""
    sup = HI * len(hubs)
    G = nx.DiGraph()
    G.add_node("s", demand=-sup)
    G.add_node("t", demand=sup)
    G.add_edge("s", "t", capacity=sup, weight=0)
    for h in hubs:
        G.add_edge("s", f"a{h}", capacity=LO, weight=-10**7)
        G.add_edge("s", f"b{h}", capacity=HI - LO, weight=-10**5)
        G.add_edge(f"a{h}", f"h{h}", weight=0)
        G.add_edge(f"b{h}", f"h{h}", weight=0)
        for st in np.where(W[h])[0]:
            G.add_edge(f"h{h}", f"s{st}", capacity=1, weight=int(D[h, st] * 1000))
    for st in np.where(W[list(hubs)].any(0))[0]:
        G.add_edge(f"s{st}", "t", capacity=1, weight=0)
    flow = nx.network_simplex(G)[1]
    asg = np.full(n_store, -1)
    for h in hubs:
        for node, v in flow[f"h{h}"].items():
            if v:
                asg[int(node[1:])] = h
    return asg


def main():
    m = pd.read_csv(ROOT / "data/makro_food_service.csv")
    s = pd.read_csv(ROOT / "data/7-11_store.csv", encoding="utf-8-sig")
    D = distance_matrix(m, s)
    W = D <= RADIUS_KM

    # Bangkok + vicinity: largest feasible set of hubs
    cand = [i for i in range(N_BKK) if W[i].sum() >= LO]
    best = None
    for k in range(len(cand), 0, -1):
        feas = [c for c in itertools.combinations(cand, k)
                if W[list(c)].any(0).sum() >= LO * k and max_flow(W, c, LO) == LO * k]
        if feas:
            best = max(feas, key=lambda c: max_flow(W, c, HI))
            break
    bkk = list(best)
    asg = assign(W, D, bkk, len(s))

    # Upcountry: one hub per province
    pick = {}
    for i in range(N_BKK, len(m)):
        p = PROVINCE[m.name[i]]
        if p not in pick or W[i].sum() > W[pick[p]].sum():
            pick[p] = i
    up = sorted(pick.values(), key=lambda i: -W[i].sum())
    for i in up:
        asg[W[i] & (asg < 0)] = i

    hubs = set(bkk) | set(up)
    rows = []
    for i in range(len(m)):
        d = D[i][asg == i]
        rows.append({
            "makro": m.name[i],
            "group": "BKK+vicinity" if i < N_BKK else "upcountry",
            "province": PROVINCE.get(m.name[i], ""),
            "selected": i in hubs,
            "stores_3km": int((D[i] <= 3).sum()),
            "stores_5km": int(W[i].sum()),
            "stores_assigned": int(len(d)),
            "avg_km": round(float(d.mean()), 2) if len(d) else None,
            "max_km": round(float(d.max()), 2) if len(d) else None,
        })
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    pd.DataFrame(rows).sort_values(["selected", "stores_assigned"], ascending=False) \
        .to_csv(out / "hub_summary.csv", index=False, encoding="utf-8-sig")
    idx = np.where(asg >= 0)[0]
    pd.DataFrame({
        "hub": m.name.values[asg[idx]], "store_id": s.store_id.values[idx], "store_name": s.name.values[idx],
        "lat": s.lat.values[idx], "lng": s.lng.values[idx], "km": D[asg[idx], idx].round(2),
    }).sort_values(["hub", "km"]).to_csv(out / "store_assignment.csv", index=False, encoding="utf-8-sig")

    print(f"Bangkok + vicinity: {len(bkk)} hubs -> {[m.name[i] for i in bkk]}")
    print(f"Upcountry: {len(up)} hubs -> {[m.name[i] for i in up]}")
    print(f"Stores served: {len(idx):,}")


if __name__ == "__main__":
    main()
