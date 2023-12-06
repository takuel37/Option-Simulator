import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 


'''
dS/s = mu * dt + sigma * dW_t
'''
class GBM:
    def __init__(self, mu, sigma, n_steps, n_paths, s, T):
        self.mu = mu
        self.sigma = sigma
        self.n_steps = n_steps
        self.n_paths = n_paths
        self.dt = T/n_steps
        self.s = s
        self.T = T
        self.paths = None
    
    def get_all_paths(self):
        randomNormals = np.random.randn(self.n_paths, self.n_steps) 
        dW = randomNormals * np.sqrt(self.dt) 
        dS = (self.mu - 0.5 * self.sigma ** 2) * self.dt + self.sigma * dW
        dS[:, 0] = 0
        S = np.cumsum(dS, axis=1)
        S = self.s * np.exp(S)
        self.paths = S
        return S
    
    def get_final_prices(self):
        if self.paths is None:
            self.paths = self.get_all_paths()
        return self.paths[:, -1]  # Take the last price from each path
    
    def simulate(self):
        if self.paths is None:
            self.paths = self.get_all_paths()
        fig = Figure(figsize=(6, 4))
        a = fig.add_subplot(111)
        a.plot(self.paths.T)
        a.set_title(f'GBM with mu= {self.mu}, sigma= {self.sigma}, n_steps: {self.n_steps}')
        return fig  

