"""Certify per n: for every d in 1..n-1 either the plain cube (vertex 0 has degree d, cubes_n{n}.log) or the
max-degree cube (vertex 0 has maximum degree d, cubesmax_n{n}.log) is UNSAT, and no cube reported SAT.
Then no graph on n vertices has tau(G) > n - H(n): its maximum-degree vertex would have some degree d, and the graph
would satisfy the corresponding cube."""
import re, glob, sys
from sat151 import H
for n in range(10, 40):
    plain = {}; mx = {}
    for fn, dct in ((f"cubes_n{n}.log", plain), (f"cubesmax_n{n}.log", mx)):
        try:
            for line in open(fn):
                m = re.match(r"n=(\d+) d=(\d+) H=(\d+)(?: \[maxdeg\])?: (SAT|UNSAT)", line)
                if m: dct[int(m.group(2))] = m.group(4)
        except FileNotFoundError: pass
    mono = None
    for fn in ("sat_10_20.log", "satb_14_20.log"):
        try:
            for line in open(fn):
                m = re.match(r"n=(\d+) H=(\d+) threshold n-H=(\d+) \[tau > n-H\]: (SAT|UNSAT)", line)
                if m and int(m.group(1)) == n: mono = m.group(4)
        except FileNotFoundError: pass
    if mono == 'UNSAT':
        print(f"n={n} H={H(n)} threshold {n-H(n)}: COMPLETE (single SAT instance UNSAT): no counterexample"); continue
    if not plain and not mx: continue
    # deeper cubes: (d) covered if every atlas type g in 0..cnt-1 is UNSAT in cubes2_n{n}.log
    deep = {}
    try:
        for line in open(f"cubes2_n{n}.log"):
            m = re.match(r"n=(\d+) d=(\d+) g=(\d+)/(\d+) H=(\d+) \[strict maxdeg\+N0\]: (SAT|UNSAT)", line)
            if m: deep.setdefault(int(m.group(2)), {})[int(m.group(3))] = (m.group(6), int(m.group(4)))
    except FileNotFoundError: pass
    # third level: (d=5, g=0) is covered if all 19 (k,g2) cubes in cubes3_n{n}.log are UNSAT
    try:
        c3 = {}
        for line in open(f"cubes3_n{n}.log"):
            m = re.match(r"n=(\d+) d=(\d+) k=(\d+) g2=(\d+)/(\d+) H=(\d+) \[strict N0indep\+N1\]: (SAT|UNSAT)", line)
            if m: c3[(int(m.group(2)), int(m.group(3)), int(m.group(4)))] = m.group(7)
        for d5 in {d for d, _, _ in c3}:
            got = {(k, g): v for (d, k, g), v in c3.items() if d == d5}
            if any(v == 'SAT' for v in got.values()): deep.setdefault(d5, {})[0] = ('SAT', 0)
            elif len(got) == 19 and all(v == 'UNSAT' for v in got.values()) and d5 in deep: deep[d5][0] = ('UNSAT', next(iter(deep[d5].values()))[1])
    except FileNotFoundError: pass
    # fourth log: general third-level split (any N(0) type g): (d,g) covered if all jobs(n,d,g) are UNSAT
    try:
        from sat151g import jobs as g_jobs
        c4 = {}
        for line in open(f"cubes4_n{n}.log"):
            m = re.match(r"n=(\d+) d=(\d+) g=(\d+) k=(\d+) g2=(\d+)/(\d+) H=(\d+) \[strict maxdeg\+N0\+N1\]: (SAT|UNSAT)", line)
            if m: c4[(int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)))] = m.group(8)
        for (d4, g4) in {(d, g) for d, g, _, _ in c4}:
            need = {(k, g2) for (_, _, _, k, g2) in g_jobs(n, d4, g4)}
            got = {(k, g2): v for (d, g, k, g2), v in c4.items() if d == d4 and g == g4}
            if any(v == 'SAT' for v in got.values()): deep.setdefault(d4, {})[g4] = ('SAT', 0)
            elif need <= set(got) and all(got[x] == 'UNSAT' for x in need) and d4 in deep: deep[d4][g4] = ('UNSAT', next(iter(deep[d4].values()))[1])
    except FileNotFoundError: pass
    for d, res in deep.items():
        cnt = next(iter(res.values()))[1]
        if any(v == 'SAT' for v, _ in res.values()): mx[d] = 'SAT'
        elif len(res) == cnt and all(v == 'UNSAT' for v, _ in res.values()): mx[d] = 'UNSAT'
    sat = [d for d in list(plain) + list(mx) if plain.get(d) == 'SAT' or mx.get(d) == 'SAT']
    missing = [d for d in range(1, n) if plain.get(d) != 'UNSAT' and mx.get(d) != 'UNSAT']
    print(f"n={n} H={h if (h:=H(n)) else 0} threshold {n-h}: {'COMPLETE: no counterexample' if not missing and not sat else ('SAT FOUND at d='+str(sat) if sat else 'missing d='+str(missing))}")
