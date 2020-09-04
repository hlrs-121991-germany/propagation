import numpy as np


def edge_propagate(A, source, p, corr=0., discount=1., depth=None, max_nodes=None):
    """Propagate message in graph A and return number of nodes visited.

    Args:
        A: Sparse adjacency matrix of graph.
        source (int): Initial node.
        p (float): Probability that message passes along an edge.
        discount (float): Discount factor <=1.0 that is multiplied at each level.
        depth (int): Maximum depth.
        max_nodes (int): Maximum number of nodes.

    Returns:
        Number of nodes visited (without initial).

    """
    # print(f"propagate from {source}")
    # return edge_propagate_tree(A, start, p, discount, depth).number_of_nodes() - 1
    if depth is None:
        depth = int(A.shape[0])
    if max_nodes is None:
        max_nodes = int(A.shape[0])
    visited = {source}
    leaves = {source}
    for i in range(depth):
        next_leaves = set()
        for node in leaves:
            children = set(edge_sample(A, node, p, corr))
            children -= visited
            next_leaves |= children
            visited |= children
            if len(visited) > max_nodes:
                return max_nodes
        leaves = next_leaves
        p *= discount
    # print(f"done {len(visited)}")
    return len(visited) - 1


def edge_sample(A, node, p, corr=0., at_least_one=False):
    """Return sample of node's children using probability p.

    Note:
         This is the inner loop, rewrite in Cython might be worthwhile.
    """
    l, r = A.indptr[node], A.indptr[node + 1]
    # return A.indices[l:r][np.random.rand(r - l) < p]
    if l == r:
        return []
    if at_least_one:
        p = 1 - (1 - p) ** (1 / (r - l))
    num = np.random.binomial(r - l, p)
    if num > 0:
        num += np.random.binomial(r - l - num, corr)

    # return A.indices[np.random.choice(r - l, num, replace=False) + l]
    children = A.indices[l:r]
    return np.random.choice(children, num, replace=False)


def simulation_stats(simulation_results):
    """Take simulation results (list of lists) and return mean retweets and retweet probability."""
    retweets = [tweet for source in simulation_results for tweet in source]  # Flatten
    return sum(retweets) / len(retweets), np.count_nonzero(retweets) / len(retweets)


# @timecall
def simulate(A, sources, p, discount=1., corr=0., depth=None, max_nodes=None, samples=1, return_stats=True):
    """ Propagate messages and return mean retweets and retweet probability.

    Args:
        A: Sparse adjacency matrix of graph.
        sources (list): List of source nodes.
        p (float): Probability that message passes along an edge.
        discount (float): Discount factor <=1.0 that is multiplied at each level.
        depth (int): Maximum depth.
        max_nodes (int): Maximum number of nodes.
        samples (int): Number of samples per source node.
        return_stats (bool): If set to false, yield full results (list of lists) instead of stats.

    Returns:
        (int, int): Mean retweets and retweet probability over all runs.
    """
    retweets = ((edge_propagate(A, source, p=p, corr=corr, discount=discount, depth=depth, max_nodes=max_nodes)
                 for _ in range(samples)) for source in sources)
    if return_stats: return simulation_stats(retweets)
    return retweets
