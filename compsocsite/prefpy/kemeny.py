"""
Credits to Vlad Niculae http://vene.ro/blog/kemeny-young-optimal-rank-aggregation-in-python.html for most of the code
Brute force and LP formulation for computing Kemeny-Young rule.
LP formulation is from V Conitzer, A Davenport, J Kalagnanam, Improved bounds for computing Kemeny rankings, AAAI 2006. 
"""


import logging
import sys
import numpy as np
from itertools import combinations, permutations
from scipy.optimize import linprog
from random import shuffle


def kendalltau_dist(rank_a, rank_b):
    """
    :param rank_a: list
    :param rank_b: list
    :return: int Kendall Tau distance 
    """
    tau = 0
    n_candidates = len(rank_a)
    for i, j in combinations(range(n_candidates), 2):
        tau += (np.sign(rank_a[i] - rank_a[j]) ==
                -np.sign(rank_b[i] - rank_b[j]))
    return tau


def test_kendalltau_dist(cols, ranks):
    kendalltau_dist(ranks[0], ranks[0])


def rankaggr_brute(ranks):
    """
    :param ranks: 2D array (list of lists), ranks[i][j] is the rank of candidate j in vote i
    :return: 
        min_dist: int, optimal (minimum) Kendall Tau distance, summed over all votes
        best_rank: list, an optimal ranking, list containing the ranking of the candidate in the optimal ranking
    """
    min_dist = np.inf
    best_rank = None
    n_voters, n_candidates = ranks.shape
    for candidate_rank in permutations(range(n_candidates)):
        dist = np.sum(kendalltau_dist(candidate_rank, rank) for rank in ranks)
        if dist < min_dist:
            min_dist = dist
            best_rank = candidate_rank
    return min_dist, best_rank


def test_rankaggr_brute(cols, ranks):
    """
    Test and report of the brute force algorithm
    :param cols: 
    :param ranks: 
    :return: 
    """
    dist, aggr = rankaggr_brute(ranks)
    print("Brute force: A Kemeny-Young aggregation with score {} is: {}".format(
        dist, ", ".join(cols[i] for i in np.argsort(aggr))))


def _build_graph(ranks):
    """
    Builds the graph for the LP formulation in Conitzer et al. 2006
    :param ranks: 
    :return: edge_weights: 2D array, adjacency matrix with edge weights as entries
    """
    n_voters, n_candidates = ranks.shape
    edge_weights = np.zeros((n_candidates, n_candidates))
    for i, j in combinations(range(n_candidates), 2):
        preference = ranks[:, i] - ranks[:, j]
        h_ij = np.sum(preference < 0)  # prefers i to j
        h_ji = np.sum(preference > 0)  # prefers j to i
        if h_ij > h_ji:
            edge_weights[i, j] = h_ij - h_ji
        elif h_ij < h_ji:
            edge_weights[j, i] = h_ji - h_ij
    return edge_weights


def test_build_graph(cols, ranks):
    """
    Test the building of the graph
    :param cols: 
    :param ranks: 
    :return: 
    """
    print(_build_graph(ranks))


def rankaggr_lp(ranks):
    """
    Kemeny-Young optimal rank aggregation using LP formulation in Conitzer et al. 2006
    TODO: Better LP solver?
    :param ranks: 2D array (list of lists), ranks[i][j] is the rank of candidate j in vote i
    :return: 
        min_dist: int, optimal (minimum) Kendall Tau distance, summed over all votes
        best_rank: list, an optimal ranking, list containing the ranking of the candidate in the optimal ranking
    """
    n_voters, n_candidates = ranks.shape
    # maximize c.T * x
    edge_weights = _build_graph(ranks)
    c = 1 * edge_weights.ravel()
    idx = lambda i, j: n_candidates * i + j
    # constraints for every pair
    pairwise_constraints = np.zeros((int((n_candidates * (n_candidates - 1)) / 2),
                                     n_candidates ** 2))
    for row, (i, j) in zip(pairwise_constraints,
                           combinations(range(n_candidates), 2)):
        row[[idx(i, j), idx(j, i)]] = 1
    # and for every cycle of length 3
    triangle_constraints = np.zeros(((n_candidates * (n_candidates - 1) *
                                      (n_candidates - 2)),
                                     n_candidates ** 2))
    for row, (i, j, k) in zip(triangle_constraints,
                              permutations(range(n_candidates), 3)):
        row[[idx(i, j), idx(j, k), idx(k, i)]] = -1

    result = linprog(c, triangle_constraints, -np.ones(len(
        triangle_constraints)), pairwise_constraints, np.ones(len(pairwise_constraints)))
    x = result.x
    obj = result.fun
    x = np.array(x).reshape((n_candidates, n_candidates))
    aggr_rank = x.sum(axis=1)
    return obj, aggr_rank


def test_rankaggr_lp(cols, ranks):
    """
    Test and report on the LP solver
    :param cols: 
    :param ranks: 
    :return: 
    """
    _, aggr = rankaggr_lp(ranks)
    score = np.sum(kendalltau_dist(aggr, rank) for rank in ranks)
    print("LP Solver: A Kemeny-Young aggregation with score {} is: {}".format(
        score,
        ", ".join(cols[i] for i in np.argsort(aggr))))


def main():
    """
    Run test code
    :return: None 
    """

    """ Simple test"""
    cols = "Alicia Ginny Gwendolyn Robin Debbie".split()
    ranks = np.array([[0, 1, 2, 3, 4],
                      [0, 1, 3, 2, 4],
                      [4, 1, 2, 0, 3],
                      [4, 1, 0, 2, 3],
                      [4, 1, 3, 2, 0]])
    test_kendalltau_dist(cols, ranks)
    test_rankaggr_brute(cols, ranks)
    # test_build_graph()
    test_rankaggr_lp(cols, ranks)

    """ Performance test"""
    m = 7
    n = 20
    cols = [str(i) for i in range(m)]
    ranks = list()
    for i in range(n):
        ranking = [j for j in range(m)]
        shuffle(ranking)
        ranks.append(ranking)
    ranks = np.array(ranks)
    test_rankaggr_brute(cols, ranks)
    test_rankaggr_lp(cols, ranks)


if __name__ == '__main__':
    FORMAT = "%(asctime)s %(levelname)s %(module)s %(lineno)d %(funcName)s:: %(message)s"
    logging.basicConfig(filename='common.log', filemode='a', level=logging.DEBUG, format=FORMAT)
    main()
