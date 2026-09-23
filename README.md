# Erdős problem #151 (Erdős–Gallai–Tuza): no counterexample on small graphs

**Problem.** For a graph G let τ(G) be the clique transversal number: the least number of vertices meeting every
maximal clique of G with at least two vertices. Let H(n) be the largest m such that every triangle-free graph on n
vertices has an independent set of size m, i.e. H(n) = max{k : R(3,k) ≤ n}. Erdős and Gallai asked whether

    τ(G) ≤ n − H(n)   for every graph G on n vertices

(Erdős 1988, p. 82; Problem 1 in Erdős–Gallai–Tuza, Discrete Math. 108 (1992)). Erdős remarked that the conjecture
is "perhaps completely wrongheaded". https://www.erdosproblems.com/151. It is easy that τ(G) ≤ n − √n; the best
general bound is τ(G) ≤ n − c√(n log n) (from the clique chromatic number bound of Joret, Micek, Reed and Smid,
2021), which has the same order as H(n) = Θ(√(n log n)).

**Reformulation used here.** τ(G) > n − H(n) holds iff every set of H(n) vertices contains a maximal clique of G
(the complement of a clique transversal is exactly a vertex set containing no maximal clique). For triangle-free
G the maximal cliques are the edges, so τ(G) = n − α(G) ≤ n − H(n) with equality for Ramsey-extremal graphs; a
counterexample must therefore contain triangles and have independence number at most H(n) − 1.

**Result.** The inequality τ(G) ≤ n − H(n) holds for every graph on n ≤ 22 vertices. For n ≤ 7 this is an exhaustive
check of all graphs (networkx atlas); for 8 ≤ n ≤ 13 a single unsatisfiable SAT instance per n; for 14 ≤ n ≤ 22 a
case split into unsatisfiable SAT instances whose union covers all graphs (certified by `coverage.py`). The bound
is attained for every n by triangle-free graphs with α(G) = H(n) (for which τ = n − α). Graphs containing a
triangle can attain it too: `tri151.py` finds such graphs for n = 6, 7, 9, 10, 11 and proves there are none for n = 5 and n = 8 (`tri151.log`; larger n
were not run to completion). Structured graphs on up to 37 vertices (Paley graphs, circulants,
Clebsch, Petersen, Kneser graphs and their complements) also satisfy the inequality (`struct151.py`). Nothing here
concerns large n.

For n = 23 (where H(n) becomes 7 and the encoding grows about sixfold) the same case split was started: 27 of its
108 pieces were unsatisfiable, no piece was satisfiable, and the run was stopped after the remaining pieces had made no
progress in 10 hours (`jobs23.txt`, `run23.out`, `cubes*_n23.log`). So n = 23 is not certified.

## Method

A counterexample on n vertices is a satisfying assignment of a propositional formula: edge variables e_ab; for every
vertex set C with 2 ≤ |C| ≤ H(n) an indicator m_C that implies "C is a clique" and "no vertex outside C is adjacent
to all of C"; for every H(n)-subset U the clause "some m_C with C ⊆ U is true". Solver: CaDiCaL 1.5.3 (python-sat).
The `weak` variant (H(n)+1 in place of H(n)) asks for τ ≥ n − H(n); it is satisfiable for every n tested (tight graphs
exist for every n), and the cube variants recover the Petersen and Clebsch graphs from their cubes, which is how the
encoding and the case splits were validated. Every satisfying assignment produced by any solver run was re-checked by
an independent integer program for τ over the explicitly enumerated maximal cliques (`tau151.py`); unsatisfiable
results are not independently certified beyond the consistency of the different splits with each other.

Single instances become slow from n = 14, so the search is split into cases that together cover all graphs:

1. `sat151d.py n d`: vertex 0 has maximum degree d, its neighbours are 1..d, and every vertex has degree ≤ d
   (sequential-counter cardinality constraints). Any graph can be relabelled to satisfy this for its own d.
2. `sat151e.py n d g`: additionally the graph induced on {1..d} is the g-th isomorphism type of graphs on d vertices
   (networkx graph atlas); relabelling inside the neighbourhood is free.
3. `sat151f.py n 5 k g2`: for the type "independent neighbourhood" additionally vertex 1 is a neighbour of vertex 0
   of largest degree, its k further neighbours are d+1..d+k (so vertices 2..d have degree ≤ k+1), and the graph
   induced on d+1..d+k is the g2-th type. `sat151g.py n d g k g2`: the same split on the outside neighbourhood of
   vertex 1 without the degree-ordering assumption, valid for every neighbourhood type g.
4. `sat151c.py n d`: an earlier split fixing only the neighbourhood of vertex 0 (any vertex, not necessarily of
   maximum degree). Both kinds of cube may be combined: the vertex of maximum degree has some degree d, so it
   suffices that for every d one of the two cubes is unsatisfiable.

`coverage.py` reads all logs and certifies, for each n, that every degree class d is covered by unsatisfiable
cubes (or reports a witness). `struct151.py` evaluates τ exactly on structured graphs up to 37 vertices.

## Files

`tau151.py` (exact τ, H(n)), `sat151.py`, `sat151b.py`, `sat151c.py`, `sat151d.py`, `sat151e.py`, `sat151f.py`,
`sat151g.py`, `coverage.py`, `struct151.py`, `search151.py`; logs `sat_10_20.log`, `cubes_n*.log`,
`cubesmax_n*.log`, `cubes2_n*.log`, `cubes3_n*.log`, `cubes4_n*.log`, `cubes*_n14.log` and `*_weak.log`
(validation runs). Requirements: numpy, scipy, networkx, python-sat.

Ramsey numbers used: R(3,k) = 3, 6, 9, 14, 18, 23, 28, 36 for k = 2..9 (so H(n) is exact for n ≤ 39).
