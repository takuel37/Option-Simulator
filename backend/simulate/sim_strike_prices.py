from ..payouts import IronCondorPayout, StraddlePayout, StranglePayout
import numpy as np
from pprint import pprint
# from RW_probs import RW_EXPV_Cox, RW_EXPV_Hrusa, RW_EXPV_Steve_Shreve, Hrusa_Tree_RW_Prob
from ..models import Cox_Ross_Rubinstein_Tree, Steve_Shreve_Tree, Hrusa_Tree
from ..rw import CoxRossRubinsteinRW, SteveShreveRW, HrusaRW
from ..model_evaluation import get_evaluations
import pandas as pd
from tqdm import tqdm

def calculate_initial_capitals(S, K1, K2, K3, K4, T, r, sigma, mu):
    prices = [[Cox_Ross_Rubinstein_Tree(S, K1, T, r, sigma, 1000, 'P'),
               Steve_Shreve_Tree(S, K1, T, r, sigma, 1000, 'P'),
               Hrusa_Tree(S, K1, T, r, sigma, mu, 1000, 'P')],

              [Cox_Ross_Rubinstein_Tree(S, K2, T, r, sigma, 1000, 'P'),
               Steve_Shreve_Tree(S, K2, T, r, sigma, 1000, 'P'),
               Hrusa_Tree(S, K2, T, r, sigma, mu, 1000, 'P')],

              [Cox_Ross_Rubinstein_Tree(S, K3, T, r, sigma, 1000, 'C'),
               Steve_Shreve_Tree(S, K3, T, r, sigma, 1000, 'C'),
               Hrusa_Tree(S, K3, T, r, sigma, mu, 1000, 'C')],

              [Cox_Ross_Rubinstein_Tree(S, K4, T, r, sigma, 1000, 'C'),
               Steve_Shreve_Tree(S, K4, T, r, sigma, 1000, 'C'),
               Hrusa_Tree(S, K4, T, r, sigma, mu, 1000, 'C')]]

    # Calculate the values for each pricing model
    CRR_Tree_value = prices[1][0] + prices[2][0] - prices[0][0] - prices[3][0]
    Steve_Shreve_Tree_value = prices[1][1] + prices[2][1] - prices[0][1] - prices[3][1]
    Hrusa_Tree_value = prices[1][2] + prices[2][2] - prices[0][2] - prices[3][2]
    initial_capitals = [CRR_Tree_value, Steve_Shreve_Tree_value, Hrusa_Tree_value]
    initial_capitals = {
        'CRR': CRR_Tree_value,
        'Steve': Steve_Shreve_Tree_value,
        'Heath': Hrusa_Tree_value
    }
    return initial_capitals

def strike_to_profit_gbm(K1, K2, K3, K4, final_prices, initial_capital,
                         payout_name = 'iron_condor'):
    if payout_name == 'iron_condor':
        payout = IronCondorPayout(K1, K2, K3, K4, final_prices)
    elif payout_name == 'straddle':
        payout = StraddlePayout(K1, final_prices)
    elif payout_name == 'strangle':
        payout = StranglePayout(K1, K2, final_prices)
    else:
        # Default to Iron Condor
        payout = IronCondorPayout(K1, K2, K3, K4, final_prices)

    payout_values = payout.calculate_payout(final_prices)
    average_payout = np.mean(payout_values)
    return initial_capital - average_payout

def simulate_exp_gbm_rw(S, r, T, N, sigma, mu, final_prices,
                        payout_name = 'iron_condor'):
    results = dict()
    S = int(S)
    K_params = []
    for k1 in range(0, S, 10):
        for k2 in range(k1+5, S, 10):
            for k3 in range(105, 200, 10):
                for k4 in range(k3 + 5, 200, 10):
                    K_params.append((k1, k2, k3, k4))

    results["CRR"] = dict()
    results["Steve"] = dict()
    results["Heath"] = dict()
    for model in ["CRR", "Steve", "Heath"]:
        results[model]["GBM_OPTIMAL_K"] = None
        results[model]["GBM_EXP"] = None
        results[model]["RW_EXP"] = None
        results[model]["RW_EXP"] = None        

    for k1, k2, k3, k4 in tqdm(K_params):
        initial_capitals = calculate_initial_capitals(S, k1, k2, k3, k4, T, r, sigma, mu)
        # CRR
        if payout_name == 'iron_condor':
            payout = IronCondorPayout(k1, k2, k3, k4, final_prices)
        elif payout_name == 'straddle':
            payout = StraddlePayout(k1, final_prices)
        elif payout_name == 'strangle':
            payout = StranglePayout(k1, k2, final_prices)
        else:
            # Default to Iron Condor
            payout = IronCondorPayout(k1, k2, k3, k4, final_prices)

        # payout_values = payout.calculate_payout(final_prices)
        # evaluations = get_evaluations(initial_capitals=initial_capitals, payout_values=payout_values)
        for model in ["CRR", "Steve", "Heath"]:
            gbm_exp = strike_to_profit_gbm(k1, k2, k3, k4, final_prices, initial_capitals[model]
                                           , payout_name = payout_name)
            if model == "CRR":
                rw = CoxRossRubinsteinRW(S, mu, r, sigma, T, N,
                                        k1, k2,
                                        k3, k4)
            elif model == "Steve":
                rw = SteveShreveRW(S, mu, r, sigma, T, N,
                                        k1, k2,
                                        k3, k4)
            elif model == "Heath":
                rw = HrusaRW(S, mu, r, sigma, T, N,
                                        k1, k2,
                                        k3, k4)
            rw_exp = rw.get_exp_profits(initial_capitals[model], payout_name)
            # Compare
            if results[model]["GBM_EXP"] is None or gbm_exp > results[model]["GBM_EXP"]:
                results[model]["GBM_EXP"] = gbm_exp
                results[model]["GBM_OPTIMAL_K"] = "K1 = {}, K2 = {}, K3 = {}, K4 = {}".format(k1, k2, k3, k4)
            if results[model]["RW_EXP"] is None or rw_exp > results[model]["RW_EXP"]:
                results[model]["RW_EXP"] = rw_exp
                results[model]["RW_OPTIMAL_K"] = "K1 = {}, K2 = {}, K3 = {}, K4 = {}".format(k1, k2, k3, k4)
                # Compute the probability of success?
                results[model]["RW_EXP_P"] = rw.get_prob_profit()

    return results