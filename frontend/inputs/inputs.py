import tkinter as tk
from tkinter import ttk
from pandastable import Table, TableModel
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 

pd.set_option('display.float_format', '{:.10f}'.format)


from ..backend_calls.calls import get_main_results, get_simulation_k

class Inputs:
    def __init__(self, window, frame_name):
        self.frame_name = frame_name

        input_box = tk.Frame(window)
        input_box.grid(row=0, column=0, sticky="nw")
        # Create a box for the table with the same height as the input box
        table_frame = tk.Frame(window)
        table_frame.grid(row=0, column=1, columnspan=1, sticky="nsew")


        S_label = tk.Label(input_box, text="Current stock price")
        S_label.grid(row=0)
        S_entry = tk.Entry(input_box)
        S_entry.grid(row=0, column=1)

        K1_label = tk.Label(input_box, text="K1 (Long Put) price")
        K1_label.grid(row=1)
        K1_entry = tk.Entry(input_box)
        K1_entry.grid(row=1, column=1)

        K2_label = tk.Label(input_box, text="K2 (Short Put) price")
        K2_label.grid(row=2)
        K2_entry = tk.Entry(input_box)
        K2_entry.grid(row=2, column=1)

        K3_label = tk.Label(input_box, text="K3 (Short Call) price")
        K3_label.grid(row=3)
        K3_entry = tk.Entry(input_box)
        K3_entry.grid(row=3, column=1)

        K4_label = tk.Label(input_box, text="K4 (Long Call) price")
        K4_label.grid(row=4)
        K4_entry = tk.Entry(input_box)
        K4_entry.grid(row=4, column=1)

        T_label = tk.Label(input_box, text="T")
        T_label.grid(row=5)
        T_entry = tk.Entry(input_box)
        T_entry.grid(row=5, column=1)

        r_label = tk.Label(input_box, text="Risk-free interest rate in %")
        r_label.grid(row=6)
        r_entry = tk.Entry(input_box)
        r_entry.grid(row=6, column=1)

        sigma_label = tk.Label(input_box, text="Volatility in %")
        sigma_label.grid(row=7)
        sigma_entry = tk.Entry(input_box)
        sigma_entry.grid(row=7, column=1)

        mu_label = tk.Label(input_box, text="Mu in %")
        mu_label.grid(row=8)
        mu_entry = tk.Entry(input_box)
        mu_entry.grid(row=8, column=1)

        calculate_button = tk.Button(input_box, text="Calculate", command=lambda : self.calculate_callback())
        calculate_button.grid(row=9, column=0, columnspan=2)

        self.S_entry = S_entry
        self.K1_entry = K1_entry
        self.K2_entry = K2_entry
        self.K3_entry = K3_entry
        self.K4_entry = K4_entry
        self.T_entry = T_entry
        self.r_entry = r_entry
        self.sigma_entry = sigma_entry
        self.mu_entry = mu_entry
        self.window = window
        self.input_box = input_box
        self.table_frame = table_frame
        self.final_prices = None

        self.simulate_frame = tk.Frame(window)
        self.simulate_frame.grid(row=0, column=3, rowspan=2, sticky="nsew")

        self.simulate_results_frame = tk.Frame(window)
        self.simulate_results_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")


    
    def calculate_callback(self):
        try:
            S = float(self.S_entry.get())
            K1 = float(self.K1_entry.get())
            K2 = float(self.K2_entry.get())
            K3 = float(self.K3_entry.get())
            K4 = float(self.K4_entry.get())
            T = float(self.T_entry.get())
            r = float(self.r_entry.get())/100
            sigma = float(self.sigma_entry.get())/100
            mu = float(self.mu_entry.get())/100
            payout_name = self.frame_name
            results = get_main_results(S, r, T, sigma, mu, K1, K2, K3, K4, payout_name)
            results_df = pd.DataFrame(results["prices"])
            print(results_df)
            # Display the results in the window as a table

            
            # Clear the previous table frame before adding a new one
            for widget in self.table_frame.winfo_children():
                widget.destroy()
            for widget in self.simulate_frame.winfo_children():
                widget.destroy()
            for widget in self.simulate_results_frame.winfo_children():
                widget.destroy()
            # Make a table of the results with all decimals
            table = Table(self.table_frame, dataframe=results_df,
                          width=300, height=100,
                          showtoolbar=False, showstatusbar=True)
            # table.autoResizeColumns()
            table.showIndex()
            table.show()

            # Make a plot of the simulations
            simulations = results["simulation"]
            simulations = np.array(simulations)
            self.final_prices = simulations[:, -1].tolist()
            # print(self.final_prices)
            n_steps = simulations.shape[1]

            fig = Figure(figsize=(6, 4))
            a = fig.add_subplot(111)
            a.plot(simulations.T)
            a.set_title(f'GBM with mu= {mu}, sigma= {sigma}, n_steps: {n_steps}')
            a.set_xlabel('Time')
            a.set_ylabel('GBM')

            # Put the plot below the table
            canvas = FigureCanvasTkAgg(fig, master=self.window)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, sticky="nsew")

            # Create a button to simulate the option price
            simulate_button = tk.Button(self.simulate_frame, text="Simulate", command=lambda : self.simulate_callback())
            simulate_button.grid(row=0, column=0, columnspan=2)

        except Exception as e:
            print("[ERROR] ", e)
        
        
    def simulate_callback(self):
        try:
            S = float(self.S_entry.get())
            T = float(self.T_entry.get())
            r = float(self.r_entry.get())/100
            sigma = float(self.sigma_entry.get())/100
            mu = float(self.mu_entry.get())/100
            payout_name = self.frame_name

            results = get_simulation_k(S, r, T, sigma, mu, self.final_prices, payout_name)
            results_df = pd.DataFrame(results)
            print(results_df)
            # Display the results in the window as a table

            # Clear the previous table frame before adding a new one
            for widget in self.simulate_results_frame.winfo_children():
                widget.destroy()

            table = Table(self.simulate_results_frame, dataframe=results_df,
                          width=300, height=100,
                          showtoolbar=False, showstatusbar=True)
            # table.autoResizeColumns()
            table.showIndex()
            table.show()
        except Exception as e:
            print("[ERROR] ", e)


def create_inputs_box(window, frame_name):
    inputs = Inputs(window, frame_name)

    return inputs