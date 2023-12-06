import numpy as np

class StraddlePayout:
    def __init__(self, K1, final_prices):
        self.final_prices = final_prices
        self.K1 = K1
    
    def calculate_payout_np(self, final_prices_np):
        call_payout = np.maximum(0, final_prices_np - self.K1)
        put_payout = np.maximum(0, self.K1 - final_prices_np)
        total_payout = call_payout + put_payout
        return total_payout
        
    def calculate_payout(self, final_prices):
        if isinstance(final_prices, list):
            final_prices = np.array(final_prices)
        return self.calculate_payout_np(np.array(final_prices))