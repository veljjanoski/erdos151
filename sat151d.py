"""As sat151c.py but with the lossless symmetry choice 'vertex 0 has maximum degree': N(0) = {1..d} and every other
vertex has degree <= d (sequential-counter at-most-d constraints).  Usage: python sat151d.py n d -> cubesmax_n{n}.log"""
import sys, itertools, time, networkx as nx
from sat151 import H, tau_exact
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
def solve_cube(n, d):
    h = H(n); k = h
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
    top = cnt[0]
    for v in range(1, n):
        lits = [E(v, u) for u in range(n) if u != v]
        cnf = CardEnc.atmost(lits=lits, bound=d, top_id=top, encoding=EncType.seqcounter)
        for cl in cnf.clauses: s.add_clause(cl)
        top = max(top, cnf.nv)
    t0 = time.time(); ok = s.solve(); dt = time.time() - t0
    line = f"n={n} d={d} H={h} [maxdeg]: {'SAT' if ok else 'UNSAT'} ({dt:.0f}s)"
    if ok:
        model = set(l for l in s.get_model() if l > 0); G = nx.Graph(); G.add_nodes_from(range(n))
        G.add_edges_from([(a, b) for (a, b), v in e.items() if v in model]); t = tau_exact(G)
        line += f"  witness tau={t} (threshold {n-h}) check={'OK' if t > n-h else 'MISMATCH'} maxdeg={max(dict(G.degree()).values())} edges={sorted(G.edges())}"
    open(f"cubesmax_n{n}.log", "a").write(line + "\n"); print(line)
if __name__ == "__main__":
    solve_cube(int(sys.argv[1]), int(sys.argv[2]))
