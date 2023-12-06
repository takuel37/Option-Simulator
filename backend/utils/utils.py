import numpy as np
from scipy.special import comb

def n_choose(n):
    """Compute the n choose k function for all k in [0, n]

    Args:
        n (int): the number of trials
    """
    return comb(n, np.arange(n+1), exact=False)

def calculate_p(m, r, sigma, T, N):
    """Calculate the probability of an up move

    Args:
        m (_type_): _description_
        r (_type_): _description_
        sigma (_type_): _description_
        T (_type_): _description_
        N (_type_): _description_
    """
    return (1/2) - ((r - m)*(T/N)/((2*sigma)*np.sqrt(T / N)))

def prob_profit(S, n, u_star, d_start, p, K1, K2, K3, K4):
    """Calculate the probability of profit

    Args:
        S (_type_): _description_
        n (_type_): _description_
        u_star (_type_): _description_
        d_start (_type_): _description_
        p (_type_): _description_
        K1 (_type_): _description_
        K2 (_type_): _description_
        K3 (_type_): _description_
        K4 (_type_): _description_
    """
    q = 1 - p
    range_ = np.arange(n+1)
    prices = S * (u_star ** (n-range_)) * (d_start ** range_)

    lower_bound = (K2 + K1)/2
    upper_bound = (K3 + K4)/2

    lower_mask = prices > lower_bound
    upper_mask = prices < upper_bound
    mask = np.logical_and(lower_mask, upper_mask)

    probs = (p ** (n-range_)) * (q ** range_)
    freq_list = n_choose(n) * probs

    return np.sum(freq_list[mask])