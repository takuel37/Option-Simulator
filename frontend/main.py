import tkinter as tk
from tkinter import ttk
from .notebook import create_notebook
from .inputs import create_inputs_box

def main():
    # Create a window
    window = tk.Tk()
    # Set the title
    window.title("Model Evaluation")
    # Set the size of the window
    window.geometry("1000x1000")
    # Set the background color of the window
    window.config(background="white")
    # Create notebook
    notebook = create_notebook(window)
    # Get current tab name
    current_tab_name = notebook.tab(notebook.select(), "text")
    # Create a label
    # label = tk.Label(
    #     window, 
    #     text=f"Current tab: {current_tab_name}", 
    #     font=("Helvetica", 16, "bold")  # ('fontname', fontsize, 'fontweight')
    # )
    # # Place the label in the window
    # label.pack(pady=10)

    # Get the frames in the notebook
    frames = notebook.winfo_children()
    # For each frame, create a box of inputs
    for frame in frames:
        # Get the name of the tab
        frame_name = notebook.tab(frame, "text")
        create_inputs_box(frame, frame_name)
    



    # Place the box in the window at the top left corner


    # Run the application
    window.mainloop()

if __name__ == "__main__":
    main()
