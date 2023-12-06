import numpy as np

def Cox_Ross_Rubinstein_Tree (S,K,T,r,sigma,N, Option_type):

    # Underlying price (per share): S
    # Strike price of the option (per share): K
    # Time to maturity (years): T
    # Continuously compounding risk-free interest rate: r
    # Volatility: sigma
    # Number of binomial steps: N

        # The factor by which the price rises (assuming it rises) = u 
        # The factor by which the price falls (assuming it falls) = d 
        # The probability of a price rise = pu 
        # The probability of a price fall = pd 
        # discount rate = disc 

    u=np.exp(sigma*np.sqrt(T/N))
    d=np.exp(-sigma*np.sqrt(T/N))
    pu=((np.exp(r*T/N))-d)/(u-d)
    pd=1-pu
    disc=np.exp(-r*T/N)

    C = np.zeros(N+1)

    S_0 = S * d**N
    ratio = u/d
    St = S_0 * ratio**np.arange(N+1)

    if Option_type == 'P':
        C = np.maximum(K-St, 0)
    elif Option_type == 'C':
        C = np.maximum(St-K, 0)

    for i in range(N, 0, -1):
        C[:i] = disc * (pu * C[1:i+1] + pd * C[:i])

    return C[0]

def Steve_Shreve_Tree (S, K, T, r, sigma, N, Option_type):
    u=1+(r*(T/N))+sigma*np.sqrt(T/N)
    d=1+(r*(T/N))-sigma*np.sqrt(T/N)
    pu=1/2
    pd=1-pu
    disc=np.exp(-r*T/N)

    C = np.zeros(N+1)

    S_0 = S * d**N
    ratio = u/d
    St = S_0 * ratio**np.arange(N+1)

    if Option_type == 'P':
        C = np.maximum(K-St, 0)
    elif Option_type == 'C':
        C = np.maximum(St-K, 0)

    for i in range(N, 0, -1):
        C[:i] = disc * (pu * C[1:i+1] + pd * C[:i])

    return C[0]

def Hrusa_Tree (S, K, T, r, sigma, mu, N, Option_type):
    u=1+(mu*(T/N))+sigma*np.sqrt(T/N)
    d=1+(mu*(T/N))-sigma*np.sqrt(T/N)
    pu=((np.exp(r*T/N))-d)/(u-d)
    pd=1-pu
    disc=np.exp(-r*T/N)
    
    C = np.zeros(N+1)

    S_0 = S * d**N
    ratio = u/d
    St = S_0 * ratio**np.arange(N+1)

    if Option_type == 'P':
        C = np.maximum(K-St, 0)
    elif Option_type == 'C':
        C = np.maximum(St-K, 0)

    for i in range(N, 0, -1):
        C[:i] = disc * (pu * C[1:i+1] + pd * C[:i])

    return C[0]

