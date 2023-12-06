import numpy as np

class IronCondorPayout:
    def __init__(self, K1, K2, K3, K4, final_prices):
        self.final_prices = final_prices
        self.K1 = K1
        self.K2 = K2
        self.K3 = K3
        self.K4 = K4
    
    def calculate_payout_np(self, final_prices_np):
        mask_1 = final_prices_np < self.K1
        mask_2 = (self.K1 <= final_prices_np) & (final_prices_np < self.K2)
        mask_3 = (self.K2 <= final_prices_np) & (final_prices_np < self.K3)
        mask_4 = (self.K3 <= final_prices_np) & (final_prices_np < self.K4)
        mask_5 = final_prices_np >= self.K4
        payouts = np.zeros(len(final_prices_np))
        payouts[mask_1] = self.K2 - self.K1
        payouts[mask_2] = self.K2 - final_prices_np[mask_2]
        payouts[mask_3] = 0
        payouts[mask_4] = final_prices_np[mask_4] - self.K3
        payouts[mask_5] = self.K4 - self.K3
        return payouts

    def calculate_payout(self, final_prices):
    # https://www.macroption.com/iron-condor-payoff/
        if isinstance(final_prices, list):
            final_prices = np.array(final_prices)
        return self.calculate_payout_np(np.array(final_prices))