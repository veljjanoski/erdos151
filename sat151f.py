r"""Third-level cube for Erdős #151, for the hard case N(0) independent: vertex 0 has maximum degree d, N(0)={1..d}
independent; vertex 1 has the largest degree among N(0): N(1) = {0} u {d+1..d+k}, deg(j) <= k+1 for j in 2..d; the
induced graph on {d+1..d+k} is atlas type g2 (lossless: free relabelling inside N(0)\{1} and inside V\N[0]).
Usage: python sat151f.py n d k g2 [weak]  -> cubes3_n{n}.log"""
import sys, itertools, time, networkx as nx
from networkx.generators.atlas import graph_atlas_g
from sat151 import H, tau_exact
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
def atlas(k): return [g for g in graph_atlas_g() if g.number_of_nodes() == k] if k >= 1 else [nx.empty_graph(0)]
def solve(n, d, k, g2, weak=False):
    h = H(n); kk = h + 1 if weak else h
    A = atlas(k)[g2]
    cnt = [0]; e = {}
    def new(key):
        cnt[0] += 1; return cnt[0]
    for a, b in itertools.combinations(range(n), 2): e[(a, b)] = new(('e', a, b))
    def E(a, b): return e[(a, b)] if a < b else e[(b, a)]
    s = Cadical153(); m = {}
    for size in range(2, kk + 1):
        for C in itertools.combinations(range(n), size):
            mc = new(('m', C)); m[C] = mc
            for a, b in itertools.combinations(C, 2): s.add_clause([-mc, E(a, b)])
            for v in range(n):
                if v in C: continue
                t = new(('t', C, v)); s.add_clause([-mc, t]); s.add_clause([-t] + [-E(v, c) for c in C])
    for U in itertools.combinations(range(n), kk):
        s.add_clause([m[C] for size in range(2, kk + 1) for C in itertools.combinations(U, size)])
        s.add_clause([E(a, b) for a, b in itertools.combinations(U, 2)])
    for j in range(1, n): s.add_clause([E(0, j)] if j <= d else [-E(0, j)])           # N(0) = {1..d}
    for a, b in itertools.combinations(range(1, d + 1), 2): s.add_clause([-E(a, b)])    # N(0) independent
    for j in range(2, n): s.add_clause([E(1, j)] if d + 1 <= j <= d + k else [-E(1, j)])  # N(1) = {0} u {d+1..d+k}
    nodes = sorted(A.nodes())
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if i < j: s.add_clause([E(d + 1 + i, d + 1 + j)] if A.has_edge(a, b) else [-E(d + 1 + i, d + 1 + j)])
    top = cnt[0]
    for v in range(1, n):
        bound = k + 1 if 2 <= v <= d else d
        cnf = CardEnc.atmost(lits=[E(v, u) for u in range(n) if u != v], bound=bound, top_id=top, encoding=EncType.seqcounter)
        for cl in cnf.clauses: s.add_clause(cl)
        top = max(top, cnf.nv)
    t0 = time.time(); ok = s.solve(); dt = time.time() - t0
    line = f"n={n} d={d} k={k} g2={g2}/{len(atlas(k))} H={h} [{'weak' if weak else 'strict'} N0indep+N1]: {'SAT' if ok else 'UNSAT'} ({dt:.0f}s)"
    if ok:
        model = set(l for l in s.get_model() if l > 0); G = nx.Graph(); G.add_nodes_from(range(n))
        G.add_edges_from([(a, b) for (a, b), v in e.items() if v in model]); t = tau_exact(G)
        good = (t >= n - h) if weak else (t > n - h)
        line += f"  witness tau={t} (threshold {n-h}) check={'OK' if good else 'MISMATCH'} edges={sorted(G.edges())}"
    open(f"cubes3_n{n}{'_weak' if weak else ''}.log", "a").write(line + "\n"); print(line)
if __name__ == "__main__":
    solve(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), len(sys.argv) > 5 and sys.argv[5] == 'weak')
