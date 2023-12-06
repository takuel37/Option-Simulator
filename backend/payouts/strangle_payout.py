import numpy as np

class StranglePayout:
    def __init__(self, K1, K2, final_prices):
        self.K1 = K1  # strike price of the put option
        self.K2 = K2  # strike price of the call option
        self.final_prices = final_prices  # final price of the underlying

    def calculate_payout_np(self, final_prices_np):
        call_payout = np.maximum(0, final_prices_np - self.K1)
        #forstrangput_payout = np.maximum(0, self.K1 - final_prices_np)
        callk2_payout = np.maximum(0, final_prices_np - self.K2)
        #total_payout = call_payout + put_payout
        payouts = call_payout - callk2_payout
        return payouts

    def calculate_payout(self, final_prices):
        if isinstance(final_prices, list):
            final_prices = np.array(final_prices)
        return self.calculate_payout_np(np.array(final_prices))