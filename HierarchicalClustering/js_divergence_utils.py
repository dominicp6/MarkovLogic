import operator
import numpy as np


def kl_divergence(p, q):
    assert len(q) >= len(p), "When computing KL divergence of path-probability dictionaries of unequal length, the " \
                             "second dictionary must be the larger one."
    return sum(
        [p[p_path] * np.log(p[p_path] / q[p_path]) for p_path in p.keys() if p_path in q.keys() and p[p_path] != 0])


def js_divergence(p, q):
    m = compute_m_from_p_and_q(p, q)
    return 0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)


def compute_m_from_p_and_q(p, q):
    # computing m := 0.5*(p+q):
    m = {}
    m.update((path, 0.5 * prob) for path, prob in p.items())
    for path, probability in q.items():
        if path in m.keys():
            m[path] += 0.5 * probability
        else:
            m[path] = 0.5 * probability

    return m


def compute_js_divergence(node_cluster1, node_cluster2, n):
    p = node_cluster1.get_top_n_path_probabilities(n)
    q = node_cluster2.get_top_n_path_probabilities(n)
    return js_divergence(p, q)
