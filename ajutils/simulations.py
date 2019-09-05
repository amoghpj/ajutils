import numpy as np

def SSA(reaction_matrix, tspan, initial_state, propensityfunc, max_steps = 100000):
    """Implementation of Gillespie's Direct SSA
    :param reaction_matrix: Ndarray containing stoichiometry
    :type reaction_matrix: array
    :param tspan: tuple specifying start and end time of simulation
    :type tspan: tuple
    :param initial_state: Ndarray specifying initial state of system
    :type initial_state: array
    :param propensityfunc: Function that returns array containing propensities.
    :type propensityfun: callable
    :returns: Time course in ndarray
    """
    # preallocate space
    state = np.zeros((max_steps, len(initial_state)))
    time = np.zeros((max_steps, 1))
    t0, tmax = tspan
    time[0] = t0
    state[0,:] = initial_state
    # taulist will hold the actual time steps. This is not deterministic.
    taulist = np.zeros((max_steps,1))
    idx = 0
    while time[idx] < tmax and (idx + 1)< max_steps:
        curr_prop = propensityfunc(state[idx, :])
        sum_curr_prop = np.sum(curr_prop) # this will be the denominator
        idx += 1                
        # Sample two random values
        rand = np.random.random(2)
        ## 1. Pick a time step size. 
        # Smaller the p of reactions,
        # larger the step size, and vice versa
        tau = -np.log(rand[0])/sum_curr_prop 
        taulist[idx] = tau
        ## 2. Find the first reaction which satisfies a cutoff on propensity
        threshold = rand[1]*sum_curr_prop

        for reactionID in range(curr_prop.shape[0]):
            cumsum = curr_prop[0:reactionID+1].sum()
            if cumsum >= threshold:
                break
        time[idx] = time[idx - 1] + tau
        state[idx,:] = state[idx - 1,:] + reaction_matrix[reactionID, :]
    time = time[0:idx]
    state = state[0:idx,:]
    return(state, time)
