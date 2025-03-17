from django.test import TestCase
import numpy as np
from gurobipy import Model, GRB, quicksum
import time


# ---------------- Helper functions to check allocation properties ----------------

# helper function
def valid_allocation(V, A):
    """
    check if each column (item) in the allocation matrix A is allocated exactly once.
    
    args:
        V (np.ndarray): valuation matrix, shape (n x m)
        A (np.ndarray): allocation matrix, shape (n x m)
    
    returns:
        bool: true if each column is allocated exactly once, false otherwise
    """
    # shape check
    if A.shape != V.shape:
        return False
    
    n, m = A.shape
    for col in range(m):
        # each column should sum to exactly 1
        col_sum = np.sum(A[:, col])
        if col_sum != 1:
            return False
    return True

# ---------------- EQ ----------------
def is_eq(V, A, chores=False):
    """
    Check if allocation A is equitable (EQ) with respect to valuations V.
    Handles both goods and chores instances.

    Args:
        V (np.ndarray): Valuation matrix (n agents x m items).
        A (np.ndarray): Allocation matrix (binary n x m matrix).
        chores (bool): True if valuations represent chores, False if goods.

    Returns:
        bool: True if allocation A satisfies equitability (EQ), False otherwise.
    """
    # number of agents (n) and number of items (m)
    V = np.array(V, dtype=object)
    (n, m) = np.shape(V) # n : agents, m : items
    
    # initialize a utility array to store each agent's utility
    utilities = np.zeros(n)

    # compute the utility for each agent's bundle
    for agent_idx in range(n):
        # extract valuations of the current agent for all items
        agent_valuation = V[agent_idx, :]

        # extract allocated bundle for the current agent
        agent_bundle = A[agent_idx, :]

        # calculate total utility/disutility of the allocated bundle
        total_utility = np.dot(agent_valuation, agent_bundle)

        # store the calculated utility
        utilities[agent_idx] = total_utility

    # first agent's utility
    first_agent_utility = utilities[0]

    # check that every other agent has a utility that is close to the first agent's utility
    for agent_idx in range(1, n):
        if not np.isclose(utilities[agent_idx], first_agent_utility):
            # if any agent's utility is different, the allocation is not equitable
            return False
    # if all agents have (nearly) equal utility, the allocation is equitable
    return True

def is_eq1(V, A, chores=False):
    """
    check if allocation a satisfies equitability-up-to-one-item (eq1)
    with respect to valuations v. this function works for both goods and chores.
    
    args:
        v (np.ndarray): valuation matrix (n agents x m items)
        a (np.ndarray): allocation matrix (binary n x m matrix)
        chores (bool): true if valuations represent chores (negative values), false for goods
    
    returns:
        bool: true if allocation a satisfies eq1, false otherwise
    """
    # convert the valuation matrix to a numpy array and get its shape
    V = np.array(V, dtype=object)
    n, m = np.shape(V)  # n: agents, m: items

    # loop over every distinct pair of agents
    for agent_1 in range(n):
        for agent_2 in range(n):
            if agent_1 == agent_2:
                # skip comparing an agent with itself
                continue

            # compute agent_1's total utility from their own bundle
            valuation_1 = V[agent_1, :]
            bundle_1 = A[agent_1, :]
            utility_1 = np.dot(valuation_1, bundle_1)

            # for agent_2, compute the elementwise product of valuation and allocation
            valuation_2 = V[agent_2, :]
            bundle_2 = A[agent_2, :]
            u2vec = np.multiply(valuation_2, bundle_2)

            if chores:
                # for chores: check if there exists an item index i such that
                # the sum of agent_2's utilities for all items except i is at least utility_1.
                # that is: sum(u2vec excluding i) >= utility_1
                condition_met = any(
                    np.sum(u2vec[np.arange(m) != i]) >= utility_1
                    for i in range(m)
                )
                if not condition_met:
                    return False  # eq1 condition fails for chores for this agent pair
            else:
                # for goods: check if there exists an item index i such that
                # the sum of agent_2's utilities for all items except i is no more than utility_1.
                # that is: sum(u2vec excluding i) <= utility_1
                condition_met = any(
                    np.sum(u2vec[np.arange(m) != i]) <= utility_1
                    for i in range(m)
                )
                if not condition_met:
                    return False  # eq1 condition fails for goods for this agent pair

    # if every pair of agents satisfies eq1, return true
    return True


def is_dupeq1(V, A, chores=False):
    """
    check if allocation a satisfies equitability-up-to-one-duplicated-item (deq1)
    with respect to valuations v. this function works for both goods and chores.
    
    args:
        v (np.ndarray): valuation matrix (n agents x m items)
        a (np.ndarray): allocation matrix (binary n x m matrix)
        chores (bool): true if valuations represent chores (negative values), false for goods
    
    returns:
        bool: true if allocation a satisfies deq1, false otherwise
    """
    # convert v to a numpy array and get its dimensions
    V = np.array(V, dtype=object)
    n, m = np.shape(V)  # n: agents, m: items

    # loop over every distinct pair of agents
    for agent_1 in range(n):
        for agent_2 in range(n):
            if agent_1 == agent_2:
                # skip comparing an agent with itself
                continue

            # extract valuations and allocations for the two agents
            valuation_1 = V[agent_1, :]
            valuation_2 = V[agent_2, :]
            bundle_1 = A[agent_1, :]
            bundle_2 = A[agent_2, :]

            # compute agent_1's total utility from their own bundle
            utility_1 = np.dot(valuation_1, bundle_1)
            # compute agent_2's elementwise utility for their bundle
            u2vec = np.multiply(valuation_2, bundle_2)

            if chores:
                # for chores: check if there exists an item index i such that
                # the sum of agent_2's utilities for all items except i is at least
                # agent_1's utility plus the utility (disutility) of item i from agent_2's perspective.
                # in formula: sum(u2vec excluding i) >= utility_1 + u2vec[i]
                condition_met = any(
                    np.sum(u2vec[np.arange(m) != i]) >= utility_1 + u2vec[i]
                    for i in range(m)
                )
                if not condition_met:
                    return False  # deq1 condition fails for chores in this agent pair
            else:
                # for goods: check if there exists an item index i such that
                # the sum of agent_2's utilities for all items except i is no more than
                # agent_1's utility.
                # in formula: sum(u2vec excluding i) <= utility_1
                condition_met = any(
                    np.sum(u2vec[np.arange(m) != i]) <= utility_1
                    for i in range(m)
                )
                if not condition_met:
                    return False  # deq1 condition fails for goods in this agent pair

    # if every pair of agents satisfies deq1, return true
    return True


def is_eqx(V, A, chores=False):
    """
    check if allocation a satisfies equitability-up-to-any-item (eqx)
    with respect to valuations v. this function works for both goods and chores.
    
    args:
        V (np.ndarray): valuation matrix (n agents x m items)
        A (np.ndarray): allocation matrix (binary n x m matrix)
        chores (bool): true if valuations represent chores (negative values), false for goods
    
    returns:
        bool: true if allocation a satisfies eqx, false otherwise
    """
    # convert the valuation matrix to a numpy array
    V = np.array(V, dtype=object)
    n, m = np.shape(V)  # n: agents, m: items

    # iterate over each pair of distinct agents
    for agent_1 in range(n):
        for agent_2 in range(n):
            if agent_1 == agent_2:
                # skip comparing an agent with itself
                continue

            # extract valuations and allocations for the two agents
            valuation_1 = V[agent_1, :]
            valuation_2 = V[agent_2, :]
            bundle_1 = A[agent_1, :]
            bundle_2 = A[agent_2, :]

            # compute agent_1's utility for their own bundle
            util_own = np.dot(valuation_1, bundle_1)

            # for comparison, compute agent_1's evaluation of agent_2's bundle elementwise
            u2vec = np.multiply(valuation_1, bundle_2)

            if chores:
                # for chores:
                # extract the negative values from u2vec (rounding them as in fairdivision)
                u2neg = np.round(np.array([u2vec[i] for i in range(m) if u2vec[i] < 0]))
                if len(u2neg) <= 1:
                    # if there's at most one chore, removal trivially resolves envy
                    continue
                # check if for every chore (each index in u2neg), removing that chore results in a remaining sum
                # that is at least util_own. if so, agent_1 would not envy agent_2.
                if all(np.sum(u2neg[np.arange(len(u2neg)) != i]) >= util_own for i in range(len(u2neg))):
                    continue
                else:
                    return False  # eqx fails for this pair in chores scenario
            else:
                # for goods:
                # extract the positive values from u2vec
                u2pos = np.array([u2vec[i] for i in range(m) if u2vec[i] > 0])
                if len(u2pos) <= 1:
                    # if there's at most one good, removal trivially resolves envy
                    continue
                # check if for every good (each index in u2pos), removing that good results in a remaining sum
                # that is no more than util_own. if so, agent_1's envy is resolved.
                if all(np.sum(u2pos[np.arange(len(u2pos)) != i]) <= util_own for i in range(len(u2pos))):
                    continue
                else:
                    return False  # eqx fails for this pair in goods scenario

    # if no violation is found for any agent pair, eqx holds
    return True

def is_dupeqx(V, A, chores=False):
    """
    check if allocation a satisfies equitability-up-to-any-duplicated-item (deqx)
    with respect to valuations v. this function works for both goods and chores.
    
    args:
        V (np.ndarray): valuation matrix (n agents x m items)
        A (np.ndarray): allocation matrix (binary n x m matrix)
        chores (bool): true if valuations represent chores (negative values), false for goods
    
    returns:
        bool: true if allocation a satisfies deqx, false otherwise
    """
    # get dimensions from the valuation matrix
    n, m = np.shape(V)
    
    # loop over every distinct pair of agents
    for j1 in range(n):
        for j2 in range(n):
            if j1 == j2:
                # skip comparing an agent with itself
                continue

            # extract agent j1's and agent j2's valuations and allocations
            v1 = V[j1, :]
            v2 = V[j2, :]
            a1 = A[j1, :]
            a2 = A[j2, :]

            # compute agent j1's total utility from their own bundle
            u1 = np.dot(v1, a1)
            # compute agent j2's evaluation of their own bundle elementwise (using their valuation)
            u2vec = np.multiply(v2, a2)

            if chores:
                # for chores:
                # round the negative utilities from agent j2's bundle
                u2neg = np.round(np.array([u2vec[i] for i in range(m) if u2vec[i] < 0]))
                if len(u2neg) <= 1:
                    # if there is at most one chore, removal trivially satisfies deqx
                    continue
                # check if for every chore in agent j2's bundle, removing that chore
                # results in a remaining sum that is at least u1 plus the value of that chore.
                if all(np.sum(u2neg[np.arange(len(u2neg)) != i]) >= u1 + u2neg[i]
                       for i in range(len(u2neg))):
                    continue
                else:
                    # deqx condition fails for this pair in the chores scenario
                    return False
            else:
                # for goods:
                # extract the positive utilities from agent j2's bundle
                u2pos = np.array([u2vec[i] for i in range(m) if u2vec[i] > 0])
                if len(u2pos) <= 1:
                    # if there is at most one good, removal trivially satisfies deqx
                    continue
                # check if for every good in agent j2's bundle, removing that good
                # results in a remaining sum that is no more than u1.
                if all(np.sum(u2pos[np.arange(len(u2pos)) != i]) <= u1
                       for i in range(len(u2pos))):
                    continue
                else:
                    # deqx condition fails for this pair in the goods scenario
                    return False
    # if no violations found for any pair, deqx is satisfied
    return True


# ---------------- EF ----------------
def is_ef(V, A, chores=False):
    """
    check if allocation a is envy-free (ef) with respect to valuations v.
    this function works for both goods and chores.
    
    args:
        V (np.ndarray): valuation matrix (n agents x m items)
        A (np.ndarray): allocation matrix (binary n x m matrix)
        chores (bool): true if valuations represent chores, false if goods
    
    returns:
        bool: true if allocation a is envy-free, false otherwise
    """
    # convert v to a numpy array and get its dimensions
    V = np.array(V, dtype=object)
    n, m = np.shape(V)  # n: agents, m: items

    # loop over every pair of distinct agents
    for agent_1 in range(n):
        for agent_2 in range(n):
            if agent_1 == agent_2:
                # skip comparing an agent with itself
                continue

            # extract agent_1's valuation and allocation
            valuation_1 = V[agent_1, :]
            bundle_1 = A[agent_1, :]

            # extract agent_2's allocation (agent_1's evaluation is used)
            bundle_2 = A[agent_2, :]

            # compute agent_1's utility for their own bundle and for agent_2's bundle
            utility_own = np.dot(valuation_1, bundle_1)
            utility_other = np.dot(valuation_1, bundle_2)

            if chores:
                # for chores, higher (less negative) utility is better.
                # agent_1 envies agent_2 if utility_other is less than utility_own.
                if utility_other < utility_own:
                    return False
            else:
                # for goods, higher utility is better.
                # agent_1 envies agent_2 if utility_other is greater than utility_own.
                if utility_other > utility_own:
                    return False

    # if no envy is detected, the allocation is envy-free
    return True


def is_ef1(V, A, chores=False):
    """
    check if allocation a satisfies envy-free up to one item (ef1)
    with respect to valuations v. this function works for both goods and chores.
    
    args:
        V (np.ndarray): valuation matrix (n agents x m items)
        A (np.ndarray): allocation matrix (binary n x m matrix)
        chores (bool): true if valuations represent chores (negative values), false for goods
    
    returns:
        bool: true if allocation a satisfies ef1, false otherwise
    """
    V = np.array(V, dtype=object)
    n, m = np.shape(V)
    
    # loop over every pair of distinct agents
    for agent_1 in range(n):
        for agent_2 in range(n):
            if agent_1 == agent_2:
                continue  # skip comparing an agent with itself
            
            # extract the bundles for the two agents
            bundle_1 = A[agent_1, :]
            bundle_2 = A[agent_2, :]
            
            if chores:
                # for chores: use agent_2's valuation to check if eliminating one chore
                # from agent_2's bundle removes envy from agent_1.
                valuation_2 = V[agent_2, :]
                # agent_1's envy is measured by agent_2's evaluation of agent_1's bundle
                utility_eval = np.dot(valuation_2, bundle_1)
                # compute agent_2's evaluation of its own bundle elementwise
                u2vec = np.multiply(valuation_2, bundle_2)
                # check if there exists an item index i such that, when removed,
                # the sum of the remaining values is at least utility_eval.
                if any(np.sum(u2vec[np.arange(m) != i]) >= utility_eval for i in range(m)):
                    continue
                else:
                    return False
            else:
                # for goods: use agent_1's valuation to check if eliminating one good
                # from agent_2's bundle removes envy from agent_1.
                valuation_1 = V[agent_1, :]
                utility_own = np.dot(valuation_1, bundle_1)
                # compute agent_1's evaluation of agent_2's bundle elementwise
                u12vec = np.multiply(valuation_1, bundle_2)
                # check if there exists an item index i such that, when removed,
                # the sum of the remaining values is no more than utility_own.
                if any(np.sum(u12vec[np.arange(m) != i]) <= utility_own for i in range(m)):
                    continue
                else:
                    return False
    return True


            
def is_efx(V, A, chores=False):
    """
    check if allocation a satisfies envy-free up to any item (efx)
    with respect to valuations v. this function works for both goods and chores.
    
    args:
        V (np.ndarray): valuation matrix (n agents x m items)
        A (np.ndarray): allocation matrix (binary n x m matrix)
        chores (bool): true if valuations represent chores (negative values), false for goods
    
    returns:
        bool: true if allocation a satisfies efx, false otherwise
    """
    V = np.array(V, dtype=object)
    n, m = np.shape(V)
    
    # loop over every distinct pair of agents
    for agent_1 in range(n):
        for agent_2 in range(n):
            if agent_1 == agent_2:
                continue

            if chores:
                # for chores: use agent_2's valuation to evaluate both bundles
                valuation_2 = V[agent_2, :]
                bundle_1 = A[agent_1, :]
                bundle_2 = A[agent_2, :]
                # agent_1's envy is measured by agent_2's evaluation of agent_1's bundle
                utility_eval = np.dot(valuation_2, bundle_1)
                # compute agent_2's evaluation of its own bundle elementwise
                u2vec = np.multiply(valuation_2, bundle_2)
                # extract negative values (chores) from u2vec, rounding them for numerical stability
                u2neg = np.round(np.array([u2vec[i] for i in range(m) if u2vec[i] < 0]))
                if len(u2neg) <= 1:
                    # if there is at most one chore, removal trivially resolves envy
                    continue
                # check if for every chore in agent_2's bundle, removal results in a remaining sum
                # that is at least utility_eval
                if all(np.sum(u2neg[np.arange(len(u2neg)) != i]) >= utility_eval for i in range(len(u2neg))):
                    continue
                else:
                    return False
            else:
                # for goods: use agent_1's valuation to evaluate the bundles
                valuation_1 = V[agent_1, :]
                bundle_1 = A[agent_1, :]
                bundle_2 = A[agent_2, :]
                utility_own = np.dot(valuation_1, bundle_1)
                # compute agent_1's evaluation of agent_2's bundle elementwise
                u12vec = np.multiply(valuation_1, bundle_2)
                # extract positive values (goods) from u12vec
                u12pos = np.array([u12vec[i] for i in range(m) if u12vec[i] > 0])
                if len(u12pos) <= 1:
                    # if there is at most one good, removal trivially resolves envy
                    continue
                # check if for every good in agent_2's bundle, removal results in a remaining sum
                # that is no more than utility_own
                if all(np.sum(u12pos[np.arange(len(u12pos)) != i]) <= utility_own for i in range(len(u12pos))):
                    continue
                else:
                    return False
    return True


# ---------------- PO ----------------
def is_po(V, A, chores=False, tol=1e-5):
    """
    check if allocation a is pareto optimal (po) with respect to valuations v.
    this function works for both goods and chores.
    
    args:
        V (np.ndarray): valuation matrix (n agents x m items)
        A (np.ndarray): allocation matrix (binary n x m matrix)
        chores (bool): true if valuations represent chores, false for goods
        tol (float): numerical tolerance parameter for ilp feasibility
    
    returns:
        bool: true if allocation a is pareto optimal, false otherwise
    """
    # convert V to a numpy array with object type and get its dimensions
    V = np.array(V, dtype=object)
    n, m = np.shape(V)  # n: number of agents, m: number of items

    # check that A has the correct shape and each item is allocated exactly once
    assert A.shape == (n, m), "allocation matrix shape must match valuation matrix shape"
    assert np.all(np.sum(A, axis=0) == 1), "each item must be allocated exactly once"

    # compute the current utility for each agent
    current_utilities = []
    for j in range(n):
        # get the valuation vector and allocation for agent j
        agent_valuation = V[j]
        agent_allocation = A[j]
        # compute the total utility for agent j
        agent_utility = np.dot(agent_valuation, agent_allocation)
        current_utilities.append(agent_utility)
    # convert the list of utilities to a numpy array of type int
    U = np.array(current_utilities, dtype=int)

    # create an ilp model to search for a pareto improvement
    model = Model('pareto_optimality')
    model.setParam('OutputFlag', 0)
    model.setParam('IntFeasTol', tol)

    # create binary decision variables: x_vars[j, i] is 1 if agent j gets item i in the new allocation
    x_vars = {}
    for j in range(n):
        for i in range(m):
            var_name = f"x_{j}_{i}"
            x_vars[j, i] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=var_name)

    # create utility variables for the new allocation: vb_vars[j] is agent j's new utility
    vb_vars = {}
    for j in range(n):
        # for chores, the best-case (least disutility) is 0; for goods, it is the sum of all values
        if chores:
            lower_bound = U[j]
            upper_bound = 0
        else:
            lower_bound = U[j]
            upper_bound = np.sum(V[j, :])
        var_name = f"vb_{j}"
        vb_vars[j] = model.addVar(lb=lower_bound, ub=upper_bound, vtype=GRB.INTEGER, name=var_name)

    # add constraint: each item i must be allocated to exactly one agent in the new allocation
    for i in range(m):
        item_allocation_sum = quicksum(x_vars[j, i] for j in range(n))
        model.addConstr(item_allocation_sum == 1)

    # link each agent's new utility variable with the new allocation decision variables
    for j in range(n):
        utility_expression = quicksum(V[j, i] * x_vars[j, i] for i in range(m))
        model.addConstr(vb_vars[j] == utility_expression)

    # set the objective to maximize the total new utility (utilitarian welfare)
    total_new_utility = quicksum(vb_vars[j] for j in range(n))
    model.setObjective(total_new_utility, GRB.MAXIMIZE)

    # optimize the ilp model
    model.optimize()

    # if the model is infeasible, try increasing the tolerance and solve again
    if model.Status == GRB.INFEASIBLE:
        if tol < 0.1:
            return ispo(V, A, chores=chores, tol=tol * 10)
        else:
            return False

    # retrieve new utilities from the optimized solution into a list
    new_utilities = []
    for j in range(n):
        new_util = vb_vars[j].X
        new_utilities.append(new_util)
    UB = np.array(new_utilities)

    # calculate the total current utility and total new utility
    total_current = np.sum(U)
    total_new = np.sum(UB)

    # if the ilp solution is optimal, check for improvement
    if model.Status == GRB.OPTIMAL:
        # if the total new utility is not greater than the current, then no improvement exists
        if total_new <= total_current:
            return True
        # if any agent's utility increases by more than the tolerance, the allocation is not pareto optimal
        if np.any(UB - U > tol):
            return False
        else:
            return True

    # if the model status is not optimal, return False by default
    return False

