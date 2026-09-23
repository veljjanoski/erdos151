"""Erdős #151, structured graphs for larger n: exact tau (ILP over maximal cliques) vs n - H(n).
H(n) = largest k with R(3,k) <= n.  For n <= 39 exact.  For n >= 40 we use PROVEN UPPER BOUNDS U(k) on R(3,k):
R(3,k) <= U(k) <= n  implies  H(n) >= k, so tau(G) > n - k  implies  tau(G) > n - H(n)  (a valid counterexample).
Families: complements of triangle-free graphs, Paley graphs, circulants, Cayley graphs on Z_n, Kneser-type,
strongly regular graphs from networkx, plus random dense graphs with small independence number."""
import itertools, sys, time
import numpy as np, networkx as nx, scipy.sparse as sp
from scipy.optimize import milp, LinearConstraint, Bounds
from sat151 import tau_exact, R3
UPPER = {10: 41, 11: 50, 12: 60, 13: 68}   # Angeltveit 2023 (R(3,10)<=41); Goedgebeur-Radziszowski 2013 (R(3,11)<=50, R(3,13)<=68); R(3,12)<=60 (older, still valid)
def H_lower(n):
    """largest k such that R(3,k) <= n is PROVEN (exact values for k<=9, upper bounds beyond)"""
    best = max(k for k, r in R3.items() if r <= n)
    for k, u in UPPER.items():
        if u <= n and k > best: best = k
    return best
def report(name, G):
    n = G.number_of_nodes(); h = H_lower(n); t = tau_exact(G)
    flag = "COUNTEREXAMPLE" if t > n - h else f"slack {n-h-t}"
    print(f"{name:28s} n={n:3d} H>={h:2d} tau={t:3d} n-H<={n-h:3d}  {flag}", flush=True)
    return t > n - h
def paley(q):
    sq = {(x*x) % q for x in range(1, q)}
    return nx.Graph([(a, b) for a in range(q) for b in range(a+1, q) if (b - a) % q in sq])
if __name__ == "__main__":
    for q in (13, 17, 29, 37):
        report(f"Paley({q})", paley(q))
    for n in (10, 13, 16, 17, 21, 25, 30, 35):
        for _ in range(3):
            S = sorted(set(np.random.default_rng(n*7+_).integers(1, n//2 + 1, size=max(2, n//5))))
            report(f"circulant C{n}{S}", nx.circulant_graph(n, S))
    report("complement Clebsch", nx.complement(nx.Graph([(a,b) for a in range(16) for b in range(a+1,16) if bin(a^b).count('1') in (1,4)])))
    report("Clebsch", nx.Graph([(a,b) for a in range(16) for b in range(a+1,16) if bin(a^b).count('1') in (1,4)]))
    report("Petersen", nx.petersen_graph()); report("complement Petersen", nx.complement(nx.petersen_graph()))
    report("Schlaefli-ish: Kneser(8,3)", nx.kneser_graph(8, 3)); report("Kneser(7,2) complement", nx.complement(nx.kneser_graph(7, 2)))
