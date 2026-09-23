"""Does any graph WITH a triangle attain tau(G) = n - H(n)?  Weak instance (every (H+1)-subset contains a maximal
clique, i.e. tau >= n-H) plus 'some triangle exists'.  Single instance per n.  Usage: python tri151.py nmin nmax"""
import sys, itertools, time, networkx as nx
from sat151 import H, tau_exact
from pysat.solvers import Cadical153
def run(n):
    h = H(n); k = h + 1
    cnt = [0]; e = {}
    def new():
        cnt[0] += 1; return cnt[0]
    for a, b in itertools.combinations(range(n), 2): e[(a, b)] = new()
    def E(a, b): return e[(a, b)] if a < b else e[(b, a)]
    s = Cadical153(); m = {}
    for size in range(2, k + 1):
        for C in itertools.combinations(range(n), size):
            mc = new(); m[C] = mc
            for a, b in itertools.combinations(C, 2): s.add_clause([-mc, E(a, b)])
            for v in range(n):
                if v in C: continue
                t = new(); s.add_clause([-mc, t]); s.add_clause([-t] + [-E(v, c) for c in C])
    for U in itertools.combinations(range(n), k):
        s.add_clause([m[C] for size in range(2, k + 1) for C in itertools.combinations(U, size)])
        s.add_clause([E(a, b) for a, b in itertools.combinations(U, 2)])
    tri = []
    for a, b, c in itertools.combinations(range(n), 3):
        t = new(); tri.append(t)
        s.add_clause([-t, E(a, b)]); s.add_clause([-t, E(a, c)]); s.add_clause([-t, E(b, c)])
    s.add_clause(tri)
    t0 = time.time(); ok = s.solve(); dt = time.time() - t0
    line = f"n={n} H={h}: tight graph WITH a triangle: {'EXISTS' if ok else 'none'} ({dt:.0f}s)"
    if ok:
        model = set(l for l in s.get_model() if l > 0); G = nx.Graph(); G.add_nodes_from(range(n))
        G.add_edges_from([(a, b) for (a, b), v in e.items() if v in model]); t = tau_exact(G)
        ntri = sum(nx.triangles(G).values()) // 3
        line += f"  tau={t} (n-H={n-h}) check={'OK' if t == n-h else 'MISMATCH'} triangles={ntri} edges={sorted(G.edges())}"
    print(line, flush=True); open("tri151.log", "a").write(line + "\n")
if __name__ == "__main__":
    for n in range(int(sys.argv[1]), int(sys.argv[2]) + 1): run(n)
