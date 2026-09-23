"""Deeper cube for Erdős #151: vertex 0 has MAXIMUM degree d, N(0) = {1..d}, all degrees <= d, and the induced graph
on N(0) is a fixed graph from the atlas of graphs on d vertices (all isomorphism types; relabelling within N(0) is
free, so this is lossless).  Usage: python sat151e.py n d gid [weak]   -> cubes2_n{n}.log
gid indexes the list of atlas graphs with exactly d vertices.  weak = search tau >= n-H (validation)."""
import sys, itertools, time, networkx as nx
from networkx.generators.atlas import graph_atlas_g
from sat151 import H, tau_exact
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
def atlas(d): return [g for g in graph_atlas_g() if g.number_of_nodes() == d]
def solve(n, d, gid, weak=False):
    h = H(n); k = h + 1 if weak else h
    A = atlas(d)[gid]
    cnt = [0]; e = {}
    def new(key):
        cnt[0] += 1; return cnt[0]
    for a, b in itertools.combinations(range(n), 2): e[(a, b)] = new(('e', a, b))
    def E(a, b): return e[(a, b)] if a < b else e[(b, a)]
    s = Cadical153(); m = {}
    for size in range(2, k + 1):
        for C in itertools.combinations(range(n), size):
            mc = new(('m', C)); m[C] = mc
            for a, b in itertools.combinations(C, 2): s.add_clause([-mc, E(a, b)])
            for v in range(n):
                if v in C: continue
                t = new(('t', C, v)); s.add_clause([-mc, t]); s.add_clause([-t] + [-E(v, c) for c in C])
    for U in itertools.combinations(range(n), k):
        s.add_clause([m[C] for size in range(2, k + 1) for C in itertools.combinations(U, size)])
        s.add_clause([E(a, b) for a, b in itertools.combinations(U, 2)])
    for j in range(1, n): s.add_clause([E(0, j)] if j <= d else [-E(0, j)])
    nodes = sorted(A.nodes())
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if i < j: s.add_clause([E(i + 1, j + 1)] if A.has_edge(a, b) else [-E(i + 1, j + 1)])
    top = cnt[0]
    for v in range(1, n):
        cnf = CardEnc.atmost(lits=[E(v, u) for u in range(n) if u != v], bound=d, top_id=top, encoding=EncType.seqcounter)
        for cl in cnf.clauses: s.add_clause(cl)
        top = max(top, cnf.nv)
    t0 = time.time(); ok = s.solve(); dt = time.time() - t0
    line = f"n={n} d={d} g={gid}/{len(atlas(d))} H={h} [{'weak' if weak else 'strict'} maxdeg+N0]: {'SAT' if ok else 'UNSAT'} ({dt:.0f}s)"
    if ok:
        model = set(l for l in s.get_model() if l > 0); G = nx.Graph(); G.add_nodes_from(range(n))
        G.add_edges_from([(a, b) for (a, b), v in e.items() if v in model]); t = tau_exact(G)
        good = (t >= n - h) if weak else (t > n - h)
        line += f"  witness tau={t} (threshold {n-h}) check={'OK' if good else 'MISMATCH'} edges={sorted(G.edges())}"
    open(f"cubes2_n{n}{'_weak' if weak else ''}.log", "a").write(line + "\n"); print(line)
if __name__ == "__main__":
    solve(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), len(sys.argv) > 4 and sys.argv[4] == 'weak')
