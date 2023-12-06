import requests

BASE = "http://127.0.0.1:5000/"

def get_main_results(S, r, T, sigma, mu, K1, K2, K3, K4, payout_name):
    print(payout_name)
    # send post request to backend
    response = requests.post(BASE + "calculate", json={
        "S": S,
        "r": r,
        "T": T,
        "sigma": sigma,
        "mu": mu,
        "K1": K1,
        "K2": K2,
        "K3": K3,
        "K4": K4,
        "payout_name": payout_name
    }, timeout=20)
    # get response from backend
    response_json = response.json()
    return response_json

def get_simulation_k(S, r, T, sigma, mu, final_prices, payout_name):
    print(payout_name)
    response = requests.post(BASE + "simulation", json={
        "S": S,
        "r": r,
        "T": T,
        "sigma": sigma,
        "mu": mu,
        "final_prices": final_prices,
        "payout_name": payout_name
    }, timeout=120)
    response_json = response.json()
    return response_json

