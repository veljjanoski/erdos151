Draft comment for https://www.erdosproblems.com/151 (LaTeX, for Daniel's review; not posted)

---

A small-case check. Since the complement of a clique transversal is a vertex set containing no maximal clique, $\tau(G)>n-H(n)$ holds iff every set of $H(n)$ vertices contains a maximal clique of $G$. Encoding this as a SAT problem (edge variables, an indicator for each candidate clique of size at most $H(n)$ forced to imply cliqueness and maximality, one clause per $H(n)$-subset) and splitting into cases by the degree and neighbourhood of a vertex of maximum degree, we verified that

$$\tau(G)\le n-H(n)\quad\text{for every graph } G \text{ on } n\le 22 \text{ vertices,}$$

where $H(n)=\max\{k : R(3,k)\le n\}$ is exact for $n\le 39$. The bound is attained by triangle-free graphs with $\alpha(G)=H(n)$, and also by graphs containing triangles: such tight graphs exist for $n=6,7,9,10,11$ and do not exist for $n=5,8$ (same method, asking for $\tau(G)\ge n-H(n)$ plus a triangle). Every satisfying assignment produced by the solver was rechecked by an independent integer program for $\tau$. For $n=23$ the case split was only partly completed (27 of 108 cases, all unsatisfiable), so nothing is claimed there.

Code, logs and a script certifying the case coverage: https://github.com/veljjanoski/erdos151

AI-usage disclosure: Claude (Anthropic) was used as a coding assistant.
