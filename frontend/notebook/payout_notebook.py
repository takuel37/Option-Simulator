from tkinter.ttk import Notebook
import tkinter as tk

# Create a notebook
def create_notebook(window):
    notebook = Notebook(window)
    notebook.pack(fill="both", expand=True)
    for payout_name in ["Iron Condor", "Straddle", "Strangle"]:
        notebook.add(tk.Frame(notebook), text=payout_name)
    return notebook