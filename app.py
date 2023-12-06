import flask
from flask import request, jsonify
from flask_restful import reqparse, abort, Api, Resource
import numpy as np

from backend.gbm import GBM
from backend.payouts import IronCondorPayout, StraddlePayout, StranglePayout
from backend.models import Cox_Ross_Rubinstein_Tree, Steve_Shreve_Tree, Hrusa_Tree
from backend.simulate import calculate_initial_capitals, strike_to_profit_gbm, simulate_exp_gbm_rw
from backend.rw import CoxRossRubinsteinRW, SteveShreveRW, HrusaRW
from backend.model_evaluation import get_evaluations

app = flask.Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class Calculate(Resource):
    # Post method
    def post(self):
        # Get payout_name, S, K1, K2, K3, K4, T, r, sigma, mu
        parser = reqparse.RequestParser()
        parser.add_argument('S', type=float)
        parser.add_argument('K1', type=float)
        parser.add_argument('K2', type=float)
        parser.add_argument('K3', type=float)
        parser.add_argument('K4', type=float)
        parser.add_argument('T', type=float)
        parser.add_argument('r', type=float)
        parser.add_argument('sigma', type=float)
        parser.add_argument('mu', type=float)
        parser.add_argument('payout_name', type=str)
        args = parser.parse_args()

        # Calculate

        ## Configs
        S = args['S']
        K1 = args['K1']
        K2 = args['K2']
        K3 = args['K3']
        K4 = args['K4']
        T = args['T']
        r = args['r']
        sigma = args['sigma']
        mu = args['mu']
        payout_name = args['payout_name']

        N = 365
        n_paths = 1

        # Compute
        b = GBM(mu, sigma, N, n_paths, S, T)
        simulations = b.get_all_paths().tolist() # (n_paths, N+1)
        final_prices = b.get_final_prices()

        # Payout values
        if payout_name == 'Iron Condor':
            payout = IronCondorPayout(K1, K2, K3, K4, final_prices)
            payout_name = 'iron_condor'
        elif payout_name == 'Straddle':
            payout = StraddlePayout(K1, final_prices)
            payout_name = 'straddle'
        elif payout_name == 'Strangle':
            payout = StranglePayout(K3, K4, final_prices)
            payout_name = 'strangle'
        else:
            return {'error': 'Invalid payout name'}
        payout_values = payout.calculate_payout(final_prices)
        avg_payout = np.mean(payout_values)

        prices = dict()
        prices['CRR'] = dict()
        prices['Steve'] = dict()
        prices['Heath'] = dict()

        prices['CRR']['K1'] = Cox_Ross_Rubinstein_Tree(S, K1, T, r, sigma, N, 'P')
        prices['Steve']['K1'] = Steve_Shreve_Tree(S, K1, T, r, sigma, N, 'P')
        prices['Heath']['K1'] = Hrusa_Tree(S, K1, T, r, sigma, mu, N, 'P')

        prices['CRR']['K2'] = Cox_Ross_Rubinstein_Tree(S, K2, T, r, sigma, N, 'P')
        prices['Steve']['K2'] = Steve_Shreve_Tree(S, K2, T, r, sigma, N, 'P')
        prices['Heath']['K2'] = Hrusa_Tree(S, K2, T, r, sigma, mu, N, 'P')

        
        prices['CRR']['K3'] = Cox_Ross_Rubinstein_Tree(S, K3, T, r, sigma, N, 'C')
        prices['Steve']['K3'] = Steve_Shreve_Tree(S, K3, T, r, sigma, N, 'C')
        prices['Heath']['K3'] = Hrusa_Tree(S, K3, T, r, sigma, mu, N, 'C')

        prices['CRR']['K4'] = Cox_Ross_Rubinstein_Tree(S, K4, T, r, sigma, N, 'C')
        prices['Steve']['K4'] = Steve_Shreve_Tree(S, K4, T, r, sigma, N, 'C')
        prices['Heath']['K4'] = Hrusa_Tree(S, K4, T, r, sigma, mu, N, 'C')

        CRR_Tree_value = prices['CRR']['K3'] + prices['CRR']['K2'] - prices['CRR']['K1'] - prices['CRR']['K4']
        Steve_Tree_value = prices['Steve']['K3'] + prices['Steve']['K2'] - prices['Steve']['K1'] - prices['Steve']['K4']
        Hrusa_Tree_value = prices['Heath']['K3'] + prices['Heath']['K2'] - prices['Heath']['K1'] - prices['Heath']['K4']
        
        # Call Spread
        # CRR_Tree_value = prices['CRR']['K4'] - prices['CRR']['K3']
        # Steve_Tree_value = prices['Steve']['K4'] - prices['Steve']['K3']
        # Hrusa_Tree_value = prices['Heath']['K4'] - prices['Heath']['K3']

        prices['CRR']['Initial Capital'] = CRR_Tree_value
        prices['Steve']['Initial Capital'] = Steve_Tree_value
        prices['Heath']['Initial Capital'] = Hrusa_Tree_value

        #IC
        profit_CRR = CRR_Tree_value - avg_payout
        profit_Steve = Steve_Tree_value - avg_payout
        profit_Hrusa = Hrusa_Tree_value - avg_payout
        
        # profit_CRR = CRR_Tree_value + avg_payout
        # profit_Steve = Steve_Tree_value + avg_payout
        # profit_Hrusa = Hrusa_Tree_value + avg_payout

        prices['CRR']['Expected Value Of GBM'] = profit_CRR
        prices['Steve']['Expected Value Of GBM'] = profit_Steve
        prices['Heath']['Expected Value Of GBM'] = profit_Hrusa

        # RW probs
        crr_rw = CoxRossRubinsteinRW(S, mu, r, sigma, T, N, K1, K2, K3, K4)
        steve_rw = SteveShreveRW(S, mu, r, sigma, T, N, K1, K2, K3, K4)
        hrusa_rw = HrusaRW(S, mu, r, sigma, T, N, K1, K2, K3, K4)
        
        # Expected value of RW
        prices['CRR']['Expected Value of RW'] = crr_rw.get_exp_profits(CRR_Tree_value, payout_name)
        prices['Steve']['Expected Value of RW'] = steve_rw.get_exp_profits(Steve_Tree_value, payout_name)
        prices['Heath']['Expected Value of RW'] = hrusa_rw.get_exp_profits(Hrusa_Tree_value, payout_name)

        prices['CRR']['Real-World Profit %'] = crr_rw.get_prob_profit()
        prices['Steve']['Real-World Profit %'] = steve_rw.get_prob_profit()
        prices['Heath']['Real-World Profit %'] = hrusa_rw.get_prob_profit()

        results = {
            "prices": prices,
            "simulation": simulations
        }

        # Return
        return results, 201
    
class Simulation(Resource):
    def post(self):
        # Parse args S, T, r, sigma, mu, final_prices
        parser = reqparse.RequestParser()
        parser.add_argument('S', type=float)
        parser.add_argument('T', type=float)
        parser.add_argument('r', type=float)
        parser.add_argument('sigma', type=float)
        parser.add_argument('mu', type=float)
        parser.add_argument('final_prices', action='append', type=float)
        parser.add_argument('payout_name', type=str)

        args = parser.parse_args()

        S = args['S']
        T = args['T']
        r = args['r']
        sigma = args['sigma']
        mu = args['mu']
        final_prices = args['final_prices']
        final_prices = np.array(final_prices)
        payout_name = args['payout_name']
        if payout_name == 'Iron Condor':
            payout_name = 'iron_condor'
        elif payout_name == 'Strangle':
            payout_name = 'strangle'
        elif payout_name == 'Straddle':
            payout_name = 'straddle'

        # Get evaluations
        N = 1000
        results = simulate_exp_gbm_rw(S, r, T, N, sigma, mu, final_prices, payout_name)
        return results, 200
        



api.add_resource(HelloWorld, '/')
api.add_resource(Calculate, '/calculate')
api.add_resource(Simulation, '/simulation')


if __name__ == '__main__':
    app.run(debug=True, port=5000)