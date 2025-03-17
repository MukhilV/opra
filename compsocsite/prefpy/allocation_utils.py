import numpy as np
import networkx as nx
from copy import deepcopy
from gurobipy import Model, GRB, quicksum

# ---------------------------------- Helpers ----------------------------------

def get_valued_instance(V):
    """
    restricts columns to those with positive total value.
    returns (Vprime, valued_indices).
    """
    (n, m) = np.shape(V)
    valued = [i for i in range(m) if np.sum(V[:, i]) > 0]
    Vprime = V[:, valued]
    return Vprime, valued

def get_halls_instance(V):
    """
    restricts to rows that get matched in a max-card allocation.
    returns (Vprime, matched_row_indices).
    """
    (n, m) = np.shape(V)
    A = max_cardinality_allocation(V)
    matched = [j for j in range(V.shape[0]) if np.sum(A[j, :]) > 0]
    Vprime = V[matched, :]
    return Vprime, matched

def recover_from_halls(Xprime, V, matched):
    """
    restores the solution from the matched subset back to all agents.
    returns a full n x m allocation matrix.
    """
    n, m = V.shape
    X = np.zeros((n, m), dtype=Xprime.dtype)
    num_matched = len(matched)  # number of agents that were matched

    for k in range(num_matched):
        j = matched[k]  # original agent index
        X[j, :] = Xprime[k, :]  # assign the recovered allocation

    return X

def recover_from_valued(Xprime, V, valued):
    """
    rebuilds the solution from valued columns back to the original columns.
    returns an n x m allocation matrix.
    """
    n, m = V.shape
    X = np.zeros((n, m), dtype=Xprime.dtype)
    num_valued = len(valued)  # number of valuable columns

    for h in range(num_valued):  # iterate over valued columns
        i = valued[h]  # get the original column index
        X[:, i] = Xprime[:, h]  # restore allocation

    for i in range(m):  # handle unvalued columns
        if i not in valued:
            X[0, i] = 1  # assign default allocation to the first agent

    return X

def mat2set(A):
    """
    converts an n x m binary matrix into a dict of sets: agent -> set of item indices.
    """
    alloc = dict()
    n = len(A)  # number of agents
    for i in range(n):
        alloc[i] = A[i].nonzero()[0]  # get indices of nonzero elements (allocated items)
    return alloc

def compute_utilities(V, A):
    """
    builds an n x n matrix of utilities, where U[j, k] is agent j's utility for agent k's bundle.
    """
    (n, m) = np.shape(V)  # get number of agents and items
    U = np.zeros((n, m))  # initialize utility matrix
    for j in range(n):
        for k in range(n):
            U[j, k] = np.dot(V[j, :], A[k, :])  # compute agent j's utility for agent k's bundle
    return U

# ---------------------------------- Round Robin Helpers ----------------------------------
def round_robin(V):
    """
    performs a round-robin allocation.
    each agent picks its top item in turn until none remain.

    returns (allocated_items, allocation_matrix)
    """
    V = np.array(V, dtype=object)
    (n, m) = np.shape(V) # n : agents, m : items

   # track which items are still unallocated
    unallocated_cols = list(range(m))  # e.g. [0,1,2,...,m-1]
    
    # initializes a list to track items allocated to each specific agent
    allocated_items = [[] for _ in range(n)]
    
    agent_idx = 0
    while unallocated_cols:
        # among the unallocated columns, find which item has
        # the highest valuation for this agent
        row = V[agent_idx]
        
        # best_col is the column in unallocated_cols that
        # maximizes row[col]
        best_col = max(unallocated_cols, key=lambda c: row[c])
        
        # record that pick
        allocated_items[agent_idx].append(best_col)
        
        # remove that column from the set of unallocated items
        unallocated_cols.remove(best_col)
        
        # next agent
        agent_idx = (agent_idx + 1) % n
    
    # build an n x m allocation matrix
    A = np.zeros((n, m), dtype=int)
    for i in range(n):
        for col in allocated_items[i]:
            A[i, col] = 1
    
    return A


# ---------------------------------- MNW Helpers ----------------------------------

def nw(V, A):
    """
    computes nash welfare = product of agent utilities.
    returns (nw_value, utilities_list).
    """
    (n, m) = np.shape(V)
    U = list()
    nw = 0  # initialize Nash welfare

    # compute utility for each agent
    for j in range(n):
        u = np.dot(V[j, :], A[j, :])
        U.append(u)

    # compute Nash welfare only if there are positive utilities
    if not np.all(np.array(U) == 0):
        nw = np.prod([np.float64(u) for u in U if u > 0])

    return nw, U


def mnw_solve(V):
    """
    gurobi-based solver for maximum nash welfare.
    returns (status, w, U, A).
    """
    B_DEFAULT = 1000 # default bound for the log-based constraints
    (n, m) = np.shape(V)

    model = Model('mnw')
    model.setParam('OutputFlag', 0)

    # add binary decision variables for allocation
    xvars = dict()
    for j in range(n):
        for i in range(m):
            xvars[j, i] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name="x_{}_{}".format(j, i))

    # add continuous variables for welfare computation
    wvars = dict()
    for j in range(n):
        wvars[j] = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="w_{}".format(j))

    # ensure each item is assigned exactly once
    for i in range(m):
        model.addConstr(1 == quicksum(xvars[j, i] for j in range(n)))

    # enforce minimum utility constraint (ensuring each agent gets at least 1 total value)
    for j in range(n):
        model.addConstr(1 <= quicksum(V[j, i] * xvars[j, i] for i in range(m)))

    # approximate logarithmic welfare bounds using config.B
    for j in range(n):
        for k in range(1, B_DEFAULT):
            model.addConstr(wvars[j] <= np.log(k) + (np.log(k+1) - np.log(k)) *
                            (quicksum(V[j, i] * xvars[j, i] for i in range(m)) - k))

    # maximize Nash welfare
    model.setObjective(quicksum(wvars[j] for j in range(n)), GRB.MAXIMIZE)

    model.optimize()

    # check solver status
    status = model.Status

    # reconstruct allocation matrix
    A = np.zeros((n, m))
    for j in range(n):
        for i in range(m):
            A[j, i] = np.round(xvars[j, i].X)  # rounding to avoid numerical errors

    A = A.astype(int)  # ensure integer type

    # compute final Nash welfare and utility values
    w, U = nw(V, A)

    status = (status == GRB.OPTIMAL)

    return status, w, U, A


def construct_alloc_graph(V, A):
    (n, m) = np.shape(V)

    nodes = list()
    nodes = nodes + [j for j in range(n)]  # add nodes for agents
    
    edges = list()
    edge_labels = dict()

    # add edges based on allocation overlap
    for j in range(n):
        for k in range(n):
            for i in range(m):
                if V[j, i] == 1 and A[k, i] == 1:
                    edges.append((j, k))  # add directed edge from j to k
                    edge_labels[(j, k)] = i  # store the corresponding item index
                    break  # stop after finding the first match

    G = nx.DiGraph()
    G.add_nodes_from(nodes)  # add all agent nodes to the graph
    G.add_edges_from(edges)  # add edges representing allocations

    return G, edge_labels  # return the constructed graph and edge labels


def max_match_allocation(V):
    """
    finds an allocation by maximum bipartite matching on top agents/items.
    returns an n x m binary allocation matrix.
    """
    (n, m) = np.shape(V)
    G = nx.Graph()

    # add agent and item nodes
    agent_nodes = [('a', j) for j in range(n)]
    G.add_nodes_from(agent_nodes, bipartite=0)

    item_nodes = [('g', i) for i in range(m)]
    G.add_nodes_from(item_nodes, bipartite=1)

    edges = []

    # create edges for agents with max valuation for each item
    for j in range(n):
        for i in range(m):
            if V[j, i] == np.max(V[:, i]):
                edges.append((('a', j), ('g', i)))

    G.add_edges_from(edges)

    # identify agent nodes
    top_nodes = {n for n, d in G.nodes(data=True) if d['bipartite'] == 0}

    # compute max matching
    M = nx.bipartite.maximum_matching(G, top_nodes=top_nodes)
    A = np.zeros((n, m))

    # build allocation matrix
    for match in M:
        if match[0] == 'a':  
            item = M[match]
            j = match[1]  
            i = item[1]  
            A[j, i] = 1  

    # assign unallocated items greedily
    for i in range(m):
        is_allocated = (np.sum(A[:, i]) > 0)
        if is_allocated:
            continue
        j = np.argmax(V[:, i])
        A[j, i] = 1  

    return A



def max_cardinality_allocation(V):
    """
    bipartite matching for all items with positive values.
    returns an n x m binary matrix.
    """
    (n, m) = np.shape(V)
    G = nx.Graph()

    # add agent and item nodes to the bipartite graph
    agent_nodes = [('a', j) for j in range(n)]
    G.add_nodes_from(agent_nodes, bipartite=0)

    item_nodes = [('g', i) for i in range(m)]
    G.add_nodes_from(item_nodes, bipartite=1)

    edges = list()

    # create edges for every positive valuation
    for j in range(n):
        for i in range(m):
            if V[j, i] > 0:
                edges.append((('a', j), ('g', i)))

    G.add_edges_from(edges)

    # identify top-level agent nodes
    top_nodes = {n for n, d in G.nodes(data=True) if d['bipartite'] == 0}

    # compute maximum matching
    M = nx.bipartite.maximum_matching(G, top_nodes=top_nodes)
    A = np.zeros((n, m))

    # reconstruct allocation matrix from matching
    for match in M:
        if match[0] == 'a':  # ensure we are processing an agent node
            item = M[match]
            j = match[1]  # agent index
            i = item[1]  # item index
            A[j, i] = 1  # allocate item to agent

    # greedily allocate unassigned items
    for i in range(m):
        is_allocated = (np.sum(A[:, i]) > 0)
        if is_allocated:
            continue
        j = np.argmax(V[:, i])
        A[j, i] = 1  # assign item to highest-valued agent

    return A

# ---------------------------------- Market helpers ----------------------------------

def round_instance(V):
    """
    rounds valuations for numerical stability.
    returns:
    - Vprime: the adjusted valuation matrix.
    - eps: the computed precision factor.
    """
    (n, m) = V.shape
    vmax = np.max(V)
    eps = 1.0 / (6.0 * (m**3) * vmax)
    
    Vprime = np.zeros((n, m))
    for j in range(n):
        for i in range(m):
            if V[j, i] > 0:
                Vprime[j, i] = (1 + eps) ** np.ceil(np.log(V[j, i]) / np.log(1 + eps))
    return Vprime, eps

def is3epef1(X, p, eps):
    """
    checks if allocation X satisfies 3*eps-ef1 with respect to prices.
    returns True if satisfied, False otherwise.
    """
    (n, m) = np.shape(X)  # get number of agents (n) and items (m)
    spending = np.zeros(n)  # initialize spending array

    for j in range(n):  
        spending[j] = np.dot(p, X[j, :])  # calculate total spending per agent

    min_spend = np.min(spending)  # find the least spending agent

    for j in range(n):  # iterate over agents
        if np.sum(X[j, :]) <= 1:  # skip if agent has at most 1 item
            continue

        # compute spending if one item is removed
        vals = [spending[j] - (p[i] * X[j, i]) for i in range(m) if X[j, i] > 0]

        # check if all possible spends remain above (1 + 3*eps) * min_spend
        if np.all(np.array(vals) > (1 + 3 * eps) * min_spend):
            return False  # fails if the condition is not met
    return True  # allocation satisfies 3*eps-ef1

def market_phase1(V, eps):
    """
    phase 1: assigns each item to the agent with the highest value.
    sets prices to the assigned values. checks if 3*eps-ef1 holds.
    returns (status, X, p).
    """
    (n, m) = V.shape  # get number of agents (n) and items (m)
    X = np.zeros((n, m))  # initialize allocation matrix (n x m)
    p = np.zeros(m)  # initialize price vector (m items)

    for i in range(m):  # iterate over all items
        j_star = np.argmax(V[:, i])  # find the agent with highest value for item i
        X[j_star, i] = 1  # assign item i to that agent
        p[i] = V[j_star, i]  # set the price of item i to its highest value

    if is3epef1(X, p, eps):
        return True, X, p  # return success if already fair
    return False, X, p  # otherwise, return status as false

def bpb(V, p):
    """
    computes bang-per-buck (value per unit price) for each agent-item pair.
    returns a matrix BB where BB[j, i] = V[j, i] / p[i].
    """
    (n, m) = np.shape(V)  # get number of agents and items
    BB = np.zeros((n, m))  # initialize bang-per-buck matrix

    for j in range(n):
        for i in range(m):
            BB[j, i] = V[j, i] / p[i]  # compute bang-per-buck

    return BB  # return computed matrix

def build_mbb_graph(V, p):
    (n, m) = np.shape(V)  # get number of agents (n) and items (m)
    
    BB = bpb(V, p)  # compute bang-per-buck (BPB) values for all agent-item pairs
    
    MBB = list()  # list to store the most preferred items for each agent
    MBB_edges = list()  # list of edges for the MBB graph

    for j in range(n):  
        # find items that maximize agent j's bang-per-buck
        MBB_items_j = np.argwhere(BB[j, :] == np.amax(BB[j, :])).flatten().tolist()
        MBB.append(MBB_items_j)  # store best items for agent j
        
        # add directed edges from agent j to their most preferred items
        MBB_edges = MBB_edges + [(('a', j), ('g', i)) for i in MBB_items_j]

    G_MBB = nx.DiGraph()  # create a directed graph

    nodes = [('a', j) for j in range(n)]  # create agent nodes
    nodes = nodes + [('g', i) for i in range(m)]  # create item nodes
    
    G_MBB.add_nodes_from(nodes)  # add nodes to the graph
    G_MBB.add_edges_from(MBB_edges)  # add edges representing MBB preferences
    return G_MBB, MBB_edges, MBB  # return graph, edges, and MBB lists

def augment_mbb_graph(G_MBB, X):
    """
    adds edges item->agent if agent holds that item in X.
    returns the augmented graph and the new edges.
    """
    (n, m) = np.shape(X)  # get number of agents and items
    X_edges = list()  # store new edges

    for j in range(n):
        for i in range(m):
            if X[j, i] > 0:
                X_edges.append((('g', i), ('a', j)))  # item i -> agent j

    G_Augmented = deepcopy(G_MBB)  # create a copy of MBB graph
    G_Augmented.add_edges_from(X_edges)  # add new edges

    return G_Augmented, X_edges  # return augmented graph and edges

def build_augmented_mbb_graph(V, X, p):
    """
    builds the augmented market-based bipartite (MBB) graph.
    adds edges from MBB graph and augments it with item-to-agent allocations from X.
    returns the augmented graph.
    """
    G_MBB, MBB_edges, MBB = build_mbb_graph(V, p)  # get MBB graph and edges
    G_Augmented, X_edges = augment_mbb_graph(G_MBB, X)  # add item-agent edges
    return G_Augmented

def build_hierarchy(j, G, X):
    """
    builds BFS-like layers from agent j in the augmented graph.
    returns a dictionary H[level] = list of agents at that level.
    """
    (n, m) = np.shape(X)  # get number of agents (n) and items (m)

    H = dict()  # initialize hierarchy levels
    for l in range(n):
        H[l] = list()

    for k in range(n):
        try:
            l = nx.shortest_path_length(G, source=('a', j), target=('a', k)) / 2  # compute level
            H[l].append(k)  # add agent k to level l
        except nx.NetworkXNoPath:
            continue  # skip if no path exists

    return H  # return hierarchy mapping

def market_phase2(V, eps, X, p):
    """
    phase 2: attempt to fix envy by redistributing an item from a higher spender to jstar.
    returns (status, next_phase, X, p, jstar).
    """
    print('in phase 2')  # debug print
    (n, m) = np.shape(X)  # number of agents (n) and items (m)
    spending = np.zeros(n)  # initialize spending array

    for j in range(n):
        spending[j] = np.dot(p, X[j, :])  # compute total spending per agent

    jstar = np.argmin(spending)  # find the least spender
    G = build_augmented_mbb_graph(V, X, p)  # build the market-based bipartite graph
    H = build_hierarchy(jstar, G, X)  # build hierarchy based on shortest paths

    l = 1  # level starts at 1
    if l in H:
        while len(H[l]) > 0 and not is3epef1(X, p, eps):
            for k in H[l]:  # iterate over all agents in the current level
                jstar_k_paths = nx.all_shortest_paths(G, source=('a', jstar), target=('a', k))
                for path in jstar_k_paths:
                    i = path[-2][1]  # item index being reallocated
                    lminus1 = path[-3][1]  # previous agent in path
                    
                    # check if moving item i from k to lminus1 helps reduce envy
                    if spending[k] - p[i] > (1 + eps) * spending[jstar]:
                        X[k, i] -= 1  # remove item i from agent k
                        X[lminus1, i] += 1  # give item i to agent lminus1
                        return False, 2, X, p, jstar  # continue phase 2

            l += 1  # move to the next level
            if l not in H:  # stop if no further levels exist
                break

    if is3epef1(X, p, eps):
        return True, 0, X, p, jstar  # phase 2 succeeded, move to termination
    return False, 3, X, p, jstar  # move to phase 3

def market_phase3(V, eps, X, p, jstar):
    (n, m) = np.shape(V)

    # initialize spending for each agent
    spending = np.zeros(n)
    for j in range(n):
        spending[j] = np.dot(p, X[j, :])

    # compute bang-per-buck ratios
    BB = bpb(V, p)
    mbbr = dict()
    for j in range(n):
        mbbr[j] = np.max(BB[j, :])

    # construct hierarchy and identify relevant agents/items
    G = build_augmented_mbb_graph(V, X, p)
    H = build_hierarchy(jstar, G, X)

    Hagents = []
    for l in range(n):
        for j in H[l]:
            Hagents.append(j)
    other_agents = [j for j in range(n) if j not in Hagents]

    Hitems = []
    for j in Hagents:
        for i in range(m):
            if X[j, i] > 0:
                Hitems.append(i)
    other_items = [i for i in range(m) if i not in Hitems]

    # compute a1: min ratio of bang-per-buck if agent tries an outside item
    a1 = 0
    vals = []
    for j in Hagents:
        for i in other_items:
            vals.append(mbbr[j] / (V[j, i] / p[i]))
    if len(vals) > 0:
        a1 = np.min(vals)

    # compute a2: scale so jstar's spending can catch an outside agent
    a2 = 0
    vals1 = []
    for k in other_agents:
        vals2 = []
        for i in range(m):
            if X[k, i] > 0:
                vals2.append(spending[k] - p[i])
        #if vals2: # in case there are no items to remove
        min_vals2 = np.min(vals2)
        vals1.append(min_vals2)
    if vals1 and spending[jstar] > 0:
        a2 = (1 / spending[jstar]) * np.max(vals1)
    if spending[jstar] == 0:
        a2 = np.infty

    # compute a3: scale to surpass some outside agent
    a3 = 0
    if len(other_agents) > 0 and spending[jstar] > 0:
        jhat = other_agents[np.argmin([spending[k] for k in other_agents])]
        s = 0
        while (1 + eps) ** s <= spending[jhat] / spending[jstar]:
            s += 1
        a3 = (1 + eps) ** s
    else:
        a3 = np.infty

    # determine the final scaling factor
    a = np.min([a1, a2, a3])

    # scale prices of items in Hitems
    for i in Hitems:
        p[i] *= a

    if a == a2:
        return True, 0, X, p
    return False, 2, X, p

def market_solve(V):
    """
    runs the market-based allocation mechanism to find an ef1 + po allocation.
    returns (status, allocation matrix X, price vector p).
    """
    (n, m) = V.shape

    # round valuations for numerical stability
    V, eps = round_instance(V)

    # phase 1: initial allocation and pricing
    status, X, p = market_phase1(V, eps)

    # compute initial utilities and spending
    U = [np.dot(X[j, :], V[j, :]) for j in range(n)]    # utilities per agent
    P = [np.dot(X[j, :], p) for j in range(n)]          # spending per agent

    # if phase 1 already satisfies ef1, return solution
    if status:
        return status, X, p

    # initialize variables for phase transitions
    status = False
    next_phase = 2
    jstar = None  # least spender

    # iterate through market phases until convergence
    while not status:
        if next_phase == 2:
            # phase 2: swap items to balance envy
            status, next_phase, X, p, jstar = market_phase2(V, eps, X, p)
            
            # update utilities and spending after adjustments
            U = [np.dot(X[j, :], V[j, :]) for j in range(n)]
            P = [np.dot(X[j, :], p) for j in range(n)]
        
        elif next_phase == 3:
            # phase 3: price adjustments to correct remaining envy
            status, next_phase, X, p = market_phase3(V, eps, X, p, jstar)

        else:
            # invalid phase, terminate with failure
            return False, X, p

    return status, X, p

# ---------------------------------- Market_eq helpers ----------------------------------

def round_eq_instance(V):
    """
    rounds valuations for eq-based approach.
    returns (Vprime, eps).
    """
    (n, m) = np.shape(V)
    vmax = np.max(V)
    
    # compute small tolerance epsilon for rounding
    eps = 1 / (16 * m * np.power(np.float64(vmax), 4))  # cast as float64 to ensure 64-bit precision
    
    # initialize rounded valuation matrix
    Vprime = np.zeros((n, m))

    for j in range(n):
        for i in range(m):
            if V[j, i] > 0:
                # round valuations to a (1+eps)-logarithmic grid
                Vprime[j, i] = (1 + eps) ** np.ceil(np.log(V[j, i]) / np.log(1 + eps))

    return Vprime, eps


def isepeq1(V, X, eps=1e-6):
    """
    checks if allocation X is eq1 (equitable up to one item) w.r.t. valuations V
    and a small tolerance eps.
    
    eq1 means that for every pair of agents (j, k), if we remove at most one 
    item from k's bundle, j's utility must be at least k's adjusted utility.
    
    returns true if eq1 holds, false otherwise.
    """
    (n, m) = np.shape(X)
    
    # compute each agent's utility for their allocated bundle
    U = np.zeros(n)  # initialize utility array
    for j in range(n):
        U[j] = np.dot(V[j, :], X[j, :])  # compute total utility of agent j
    
    for j in range(n):
        # if agent j has at most one item, eq1 trivially holds
        if np.sum(X[j, :]) <= 1:
            continue
        
        # compute the utility of j minus each of their items
        vals = []
        for i in range(m):
            if X[j, i] > 0:  # check items allocated to agent j
                vals.append(U[j] - V[j, i])  # compute utility without item i
        
        vals = np.array(vals)  # convert list to numpy array for efficiency

        for k in range(n):
            # check if removing any one item keeps eq1 satisfied
            if np.all(vals > (1 + eps) * U[k]):
                return False  # eq1 fails for this (j, k) pair

    return True  # eq1 holds for all agent pairs



def market_eq_phase1(V, eps):
    """
    phase 1: assign each item to the agent with the highest value and set price accordingly.
    then check if eq1 is satisfied. returns (status, X, p).
    status = True if eq1 is already satisfied, else False.
    """
    (n, m) = np.shape(V)
    X = np.zeros((n, m))  # allow default float type for flexibility
    p = np.zeros(m)

    for i in range(m):
        ivals = V[:, i]  # extract valuations for item i
        j = np.argmax(ivals)  # find agent with max value for item i
        X[j, i] = 1  # assign item i to agent j
        p[i] = V[j, i]  # set price to max valuation

    # check eq1 condition
    if isepeq1(V, X, eps):
        return True, X, p
    return False, X, p


def market_eq_phase2(V, eps, X, p):
    """
    attempts to fix eq1 envy by swapping items. returns (status, next_phase, X, p, jstar).
    """
    (n, m) = np.shape(V)  # get number of agents and items
    U = np.zeros(n)  # initialize utility array

    # compute each agent's utility for their allocated bundle
    for j in range(n):
        U[j] = np.dot(V[j, :], X[j, :])  

    # find the least satisfied agent (minimum utility)
    jstar = np.argmin(U)  

    # build the augmented mbb graph
    G = build_augmented_mbb_graph(V, X, p)  

    # build hierarchical layers from jstar using bfs
    H = build_hierarchy(jstar, G, X)  

    l = 1  # start at level 1
    while len(H[l]) > 0 and False == isepeq1(V, X, eps):  # exactly match prof's condition
        for k in H[l]:  # iterate through agents at level l
            jstar_k_paths = nx.all_shortest_paths(G, source=('a', jstar), target=('a', k))
            for path in jstar_k_paths:
                i = path[-2][1]  # item index being reallocated
                lminus1 = path[-3][1]  # previous agent in path

                # check if letting jstar have item i from k is beneficial
                if U[k] - V[k, i] > (1 + eps) * U[jstar]:  
                    X[k, i] -= 1  # remove item i from agent k
                    X[lminus1, i] += 1  # give item i to agent lminus1
                    return False, 2, X, p, jstar  

        l += 1  # move to the next level
        if not l in H:  
            break  

    # check if eq1 is satisfied after adjustments
    if isepeq1(V, X, eps):  
        return True, 0, X, p, jstar  

    return False, 3, X, p, jstar  # move to phase 3



def market_eq_phase3(V, eps, X, p, jstar):
    """
    scales prices in jstar's 'hierarchy' to reduce eq1 envy.
    returns (status, next_phase, X, p).
    """
    (n, m) = np.shape(V)  # get number of agents and items

    # initialize utility array
    U = np.zeros(n)
    for j in range(n):
        U[j] = np.dot(V[j, :], X[j, :])  # compute each agent's utility

    # compute bang-per-buck ratios
    BB = bpb(V, p)  
    mbbr = dict()
    for j in range(n):
        mbbr[j] = np.max(BB[j, :])  # max bang-per-buck for each agent

    # build augmented MBB graph and hierarchy
    G = build_augmented_mbb_graph(V, X, p)  
    H = build_hierarchy(jstar, G, X)  

    # collect agents in jstar's hierarchy
    Hagents = []
    for l in range(n):
        for j in H[l]:
            Hagents.append(j)  
    other_agents = [j for j in range(n) if j not in Hagents]  

    # collect items in jstar's hierarchy
    Hitems = []
    for j in Hagents:
        for i in range(m):
            if X[j, i] > 0:
                Hitems.append(i)  
    other_items = [i for i in range(m) if i not in Hitems]  

    # compute scaling factor D
    vals = []
    for j in Hagents:
        for i in other_items:
            vals.append(mbbr[j] / (V[j, i] / p[i]))  

    D = np.min(vals)  # take the minimum scaling factor

    # scale prices of items in jstar's hierarchy
    for i in Hitems:
        p[i] *= D  

    return False, 2, X, p  # return updated prices, move to phase 2



def market_eq_solve(V):
    """
    orchestrates eq-based phases:
      1) assign items to top agent
      2) fix eq envy via item-swaps
      3) scale prices
    returns (status, X, p).
    """
    # round valuations for numerical stability
    V, eps = round_eq_instance(V)

    # phase 1: initial allocation and pricing
    status, X, p = market_eq_phase1(V, eps)
    if status:
        return status, X, p  # if phase 1 is already eq1, return result

    # initialize phase tracking variables
    status = False
    next_phase = 2
    jstar = None  # least spender

    # iterate through market phases until convergence
    while False == status:
        if next_phase == 2:
            status, next_phase, X, p, jstar = market_eq_phase2(V, eps, X, p)
        elif next_phase == 3:
            status, next_phase, X, p = market_eq_phase3(V, eps, X, p, jstar)
        else:
            return False, X, p  # invalid phase, return failure

    return status, X, p  # return final allocation and price vector



# ---------------------------------- Leximin helpers ----------------------------------
def leximin_solve(V, B=1000, chores=False):
    """
    solves a leximin allocation problem on valuations V.
    V: n x m float array of valuations.
    B: bounding parameter (e.g. config.B).
    chores: if True, valuations are for chores (<=0). otherwise, goods.

    returns (status, sw, U, A):
      status : bool (True if gurobi found an optimal solution)
      sw     : sum of utilities in the final allocation
      U      : list of each agent's utility
      A      : n x m binary allocation matrix
    """
    (n, m) = np.shape(V)  # get number of agents and items
    b = list()  # stores lower bound levels
    A = np.zeros((n, m))  # initialize allocation matrix
    status = 0  # track solver status
    sw = 0  # sum of utilities
    U = np.zeros(n)  # initialize utilities

    # iterate from k=1..n, gradually lifting the minimum utility
    for k in range(1, n + 1):
        A = np.zeros((n, m))  # reset allocation matrix
        model = Model('leximin@{}'.format(k))  # initialize gurobi model
        model.setParam('OutputFlag', 0)
        model.setParam('TimeLimit', 5 * 60)

        # add variable for lower bound for level k
        if k == 1:
            bvar = model.addVar(lb=-1 * int(chores) * B, ub=(1 - int(chores)) * B, 
                                vtype=GRB.CONTINUOUS, name='b')
        else:
            bvar = model.addVar(lb=b[k-2], ub=(1 - int(chores)) * B, 
                                vtype=GRB.CONTINUOUS, name='b')

        # add allocation variables
        xvars = dict()
        for j in range(n):
            for i in range(m):
                xvars[j, i] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, 
                                           name='x_{}_{}'.format(j, i))

        # add utility variables
        uvars = dict()
        for j in range(n):
            uvars[j] = model.addVar(lb=-1 * int(chores) * B, ub=(1 - int(chores)) * B, 
                                    vtype=GRB.CONTINUOUS, name='u_{}'.format(j))

        # add level constraints
        yvars = dict()  # indicate whether agent is above lower bound for a level
        zvars = dict()  # count number of agents meeting lower bound
        for l in range(0, k):
            for j in range(n):
                yvars[j, l] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, 
                                           name='y_{}_{}'.format(j, l))
            zvars[l] = model.addVar(lb=0, ub=n, vtype=GRB.INTEGER, name='z_{}'.format(l))

        # enforce allocation constraints
        for i in range(m):
            model.addConstr(1 == quicksum(xvars[j, i] for j in range(n)))

        # enforce utility constraints
        for j in range(n):
            model.addConstr(uvars[j] == quicksum(V[j, i] * xvars[j, i] for i in range(m)))

        # enforce lower bound constraints for each level
        for l in range(0, k - 1):
            bl = b[l]
            for j in range(n):
                model.addConstr(yvars[j, l] >= (1 + uvars[j] - bl) / B)
                model.addConstr(yvars[j, l] <= (B + uvars[j] - bl) / B)
            model.addConstr(zvars[l] == quicksum(yvars[j, l] for j in range(n)))
            model.addConstr(zvars[l] >= n - l)

        # enforce final lower bound constraint
        for j in range(n):
            model.addConstr(yvars[j, k-1] >= (1 + uvars[j] - bvar) / B)
            model.addConstr(yvars[j, k-1] <= (B + uvars[j] - bvar) / B)
        model.addConstr(zvars[k-1] == quicksum(yvars[j, k-1] for j in range(n)))
        model.addConstr(zvars[k-1] >= n - (k-1))

        # maximize lower bound variable
        model.setObjective(bvar, GRB.MAXIMIZE)
        model.optimize()

        status = model.Status
        status = (status == GRB.OPTIMAL)
        if not status:
            return False, None, None, None  # infeasible solution

        # store the found bound
        b.append(bvar.X)

        # build final allocation matrix
        for j in range(n):
            for i in range(m):
                A[j, i] = xvars[j, i].X
        A = np.array(A).astype(int)

        # compute utilities
        U = list()
        for j in range(n):
            u = np.dot(V[j, :], A[j, :])
            U.append(u)
        sw = np.sum(U)

    return status, sw, U, A

# ---------------------------------- MNW Binary Helpers ----------------------------------

def get_path(G, pair):
    """
    returns the shortest path between two agents in the allocation graph.
    """
    (j, k) = pair
    return nx.shortest_path(G, source=j, target=k)


def get_reachability(V, G):
    """
    Computes the reachability set of each agent in the allocation graph.
    Returns a list of agent pairs that can swap items.
    """
    (n, m) = np.shape(V)
    reachability = []
    for j in range(n):
        for k in range(n):
            if nx.has_path(G, source=j, target=k):
                reachability.append((j, k))
    return reachability


def do_swaps(V, A, pair, G, labels):
    """
    performs swaps along a given path to improve the allocation.
    """
    path = get_path(G, pair)
    B = deepcopy(A)
    cur = 0
    while cur < len(path) - 1:
        j = path[cur]
        k = path[cur + 1]
        i = labels[(j, k)]
        # swap item i from agent k to agent j
        B[j, i] = 1
        B[k, i] = 0
        cur = cur + 1
    return B



def solve_mnw_binary(V):
    """
    runs the MNW binary allocation procedure.
    iteratively swaps allocations to maximize Nash Welfare.
    returns an n x m binary allocation matrix.
    """
    (n, m) = np.shape(V)  # get number of agents and items

    # initialize an allocation to start from
    A = max_match_allocation(V)
    Acur = deepcopy(A)

    # iterate over potential swaps to improve Nash Welfare
    for t in np.arange(1, 2 * m * (n + 1) * np.log(n * m) + 1, 1):
        Aprev = deepcopy(Acur)  # store previous allocation
        Gprev, labels = construct_alloc_graph(V, Aprev)  # construct allocation graph
        R = get_reachability(V, Gprev)  # get reachable agent pairs

        Apairs = list()  # store candidate allocations
        nwApairs = list()  # store corresponding Nash Welfare values

        # compute new allocations for each reachable pair
        for pair in R:
            Apair = do_swaps(V, Aprev, pair, Gprev, labels)  # swap allocations
            Apairs.append(Apair)  # store new allocation
            nwApair, U = nw(V, Apair)  # compute Nash Welfare
            nwApairs.append(nwApair)  # store Nash Welfare value

        # find the best swap that improves Nash Welfare
        max_nw_pairs = np.max(nwApairs)
        nw_prev, U = nw(V, Aprev)  # compute previous allocation's welfare

        if max_nw_pairs > nw_prev:
            max_pair_idx = np.argmax(nwApairs)  # find best swap
            Acur = deepcopy(Apairs[max_pair_idx])  # apply the best swap
        else:
            return Aprev  # return previous allocation if no improvement

    return Acur  # return final optimized allocation


