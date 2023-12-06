import numpy as np
from ..utils import n_choose, calculate_p, prob_profit
from abc import abstractmethod
from ..payouts import IronCondorPayout, StraddlePayout, StranglePayout

def exp_profits(S, n, u_star, d_start, p, K1, K2, K3, K4,
                initial_capitals, payout_name="iron_condor"):
    q = 1 - p
    range_ = np.arange(n+1)
    prices = S * (u_star ** (n - range_)) * (d_start ** range_)
    probs = (p ** (n - range_)) * (q ** range_)

    
    freq_list = n_choose(n) * probs
    if payout_name == "iron_condor":
        payout = IronCondorPayout(K1, K2, K3, K4, prices)
    elif payout_name == "straddle":
        payout = StraddlePayout(K1, prices)
    elif payout_name == "strangle":
        payout = StranglePayout(K1, K2, prices)
    else:
        payout = IronCondorPayout(K1, K2, K3, K4, prices)

    payout_values = payout.calculate_payout(prices)
    final_profit = initial_capitals - payout_values
    expected_value = final_profit * freq_list
    return np.sum(expected_value)

class RWProbs:
    def __init__(self, model, S, m, r, sigma, T, N, K1, K2, K3, K4):
        """_summary_

        Args:
            model (_type_): Model name
            S (_type_): _description_
            m (_type_): _description_ 
            r (_type_): _description_
            sigma (_type_): _description_
            T (_type_): _description_
            N (_type_): _description_
            K1 (_type_): _description_
            K2 (_type_): _description_
            K3 (_type_): _description_
            K4 (_type_): _description_
        """
        self.model = model
        self.S = S
        self.m = m # m is mu here
        self.r = r
        self.sigma = sigma
        self.T = T
        self.N = N
        self.K1 = K1
        self.K2 = K2
        self.K3 = K3
        self.K4 = K4

        # These two values will be changed by constructors of subclasses.
        self.u_star = 0
        self.d_start = 0
        
        self.p = calculate_p(m, r, sigma, T, N)
        self.q = 1 - self.p
        
    @abstractmethod
    def get_prob_profit(self):
        return
    
    def get_exp_profits(self, initial_capitals, payout_name="iron_condor"):
        return exp_profits(self.S, self.N, self.u_star, self.d_start,
                    self.p, self.K1, self.K2, self.K3, self.K4,
                    initial_capitals, payout_name)
    
    @abstractmethod  
    def get_probs(self):
        return
    
class CoxRossRubinsteinRW(RWProbs):
    def __init__(self, S, m, r, sigma, T, N, K1, K2, K3, K4):
        super().__init__("Cox Ross Rubinstein", S, m, r, sigma, T, N, K1, K2, K3, K4)
        self.u_star = np.exp(self.sigma * np.sqrt(self.T / self.N))
        self.d_start = 1 / self.u_star
    

    def get_prob_profit(self):
        return prob_profit(self.S, self.N, self.u_star, self.d_start,
                           self.p, self.K1, self.K2, self.K3, self.K4)
    
    def get_probs(self):
        range_ = np.arange(self.N+1)
        probs = (self.p ** (self.N-range_)) * (self.q ** range_)
        return probs
    

class SteveShreveRW(RWProbs):
    def __init__(self, S, m, r, sigma, T, N, K1, K2, K3, K4):
        super().__init__("Steve Shreve", S, m, r, sigma, T, N, K1, K2, K3, K4)
        temp = sigma * np.sqrt(T / N)
        temp2 = 1 + r * (T / N)
        self.u_star = temp2 + temp
        self.d_start = temp2 - temp
    
    def get_prob_profit(self):
        return prob_profit(self.S, self.N, self.u_star, self.d_start,
                           self.p, self.K1, self.K2, self.K3, self.K4)
    
    def get_probs(self):
        range_ = np.arange(self.N+1)
        probs = (self.p ** (self.N-range_)) * (self.q ** range_)
        return probs

class HrusaRW(RWProbs):
    def __init__(self, S, m, r, sigma, T, N, K1, K2, K3, K4):
        super().__init__("Hrusa", S, m, r, sigma, T, N, K1, K2, K3, K4)
        temp = sigma * np.sqrt(T / N)
        temp2 = 1 + m * (T / N)
        self.u_star = temp2 + temp
        self.d_start = temp2 - temp
    
    def get_prob_profit(self):
        return prob_profit(self.S, self.N, self.u_star, self.d_start,
                           self.p, self.K1, self.K2, self.K3, self.K4)

    def get_probs(self):
        range_ = np.arange(self.N+1)
        probs = (self.p ** (self.N-range_)) * (self.q ** range_)
        return probs
