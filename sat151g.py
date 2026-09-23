r"""Third-level cube for any fixed neighbourhood type: vertex 0 has maximum degree d, N(0)={1..d} induces atlas type g
(labels fixed as in the atlas), and N(1) minus N[0] = {d+1..d+k} induces atlas type g2 (free relabelling of the
vertices outside N[0]).  All degrees <= d.  Lossless for every g.  Usage: python sat151g.py n d g k g2 -> cubes4_n{n}.log"""
import sys, itertools, time, networkx as nx
from networkx.generators.atlas import graph_atlas_g
from sat151 import H, tau_exact
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
def atlas(k): return [g for g in graph_atlas_g() if g.number_of_nodes() == k] if k >= 1 else [nx.empty_graph(0)]
def solve(n, d, g, k, g2):
    h = H(n); kk = h
    A = atlas(d)[g]; nodesA = sorted(A.nodes()); B = atlas(k)[g2]; nodesB = sorted(B.nodes())
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
    for j in range(1, n): s.add_clause([E(0, j)] if j <= d else [-E(0, j)])
    for i, a in enumerate(nodesA):
        for j, b in enumerate(nodesA):
            if i < j: s.add_clause([E(i + 1, j + 1)] if A.has_edge(a, b) else [-E(i + 1, j + 1)])
    for j in range(d + 1, n): s.add_clause([E(1, j)] if j <= d + k else [-E(1, j)])     # N(1) outside N[0]
    for i, a in enumerate(nodesB):
        for j, b in enumerate(nodesB):
            if i < j: s.add_clause([E(d + 1 + i, d + 1 + j)] if B.has_edge(a, b) else [-E(d + 1 + i, d + 1 + j)])
    top = cnt[0]
    for v in range(1, n):
        cnf = CardEnc.atmost(lits=[E(v, u) for u in range(n) if u != v], bound=d, top_id=top, encoding=EncType.seqcounter)
        for cl in cnf.clauses: s.add_clause(cl)
        top = max(top, cnf.nv)
    t0 = time.time(); ok = s.solve(); dt = time.time() - t0
    line = f"n={n} d={d} g={g} k={k} g2={g2}/{len(atlas(k))} H={h} [strict maxdeg+N0+N1]: {'SAT' if ok else 'UNSAT'} ({dt:.0f}s)"
    if ok:
        model = set(l for l in s.get_model() if l > 0); G = nx.Graph(); G.add_nodes_from(range(n))
        G.add_edges_from([(a, b) for (a, b), v in e.items() if v in model]); t = tau_exact(G)
        line += f"  witness tau={t} (threshold {n-h}) check={'OK' if t > n-h else 'MISMATCH'} edges={sorted(G.edges())}"
    open(f"cubes4_n{n}.log", "a").write(line + "\n"); print(line)
def jobs(n, d, g):
    A = atlas(d)[g]; deg1 = A.degree(sorted(A.nodes())[0]); kmax = d - 1 - deg1
    return [(n, d, g, k, g2) for k in range(kmax + 1) for g2 in range(len(atlas(k)))]
if __name__ == "__main__":
    solve(*map(int, sys.argv[1:6]))
