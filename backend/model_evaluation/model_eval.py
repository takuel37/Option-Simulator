import numpy as np
import tkinter as tk

def compute_stats(final_prices, high, low, invert=False):
    """
    final_prices: ndarray of final prices
    high: above this price is success
    low: below this price is failure
    """
    total = len(final_prices)
    success = np.sum(final_prices > high)
    failure = np.sum(final_prices < low)

    if invert:
        success, failure = failure, success
        high, low = low, high

    # Calculate the probability of success
    p_success = success / total * 100
    p_fail = failure / total * 100
    return p_success, p_fail

def get_evaluations(initial_capitals, payout_values, invert=False):
    """
    initial_capitals: dict of initial capitals
    payout_values: list of payout values
    """
    evaluations = dict()
    for idx, (model_name, initial_capital) in enumerate(
        initial_capitals.items()
    ):
        p_success, p_fail = compute_stats(
            payout_values,
            initial_capital * 1.01,
            initial_capital * 0.99,
            invert=invert,
        )
        evaluations[model_name] = (p_success, p_fail)
    return evaluations

def view_evaluations(window, evaluations):
    """
    window: tkinter window
    evaluations: dictionary of evaluations
    """
    for idx, (model_name, (p_success, p_fail)) in enumerate(evaluations.items()):
        probability_label = tk.Label(
            window, 
            text=f"[{model_name}] Probability of profit: {p_success:.2f}%, loss: {p_fail:.2f}%", 
            font=("Helvetica", 16, "bold")  # ('fontname', fontsize, 'fontweight')
        )
        probability_label.grid(row=20 + idx, column=0, columnspan=2)