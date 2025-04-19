import tkinter as tk
from tkinter import messagebox
import subprocess


# Function to run when button is clicked
def on_run():
    name = name_entry.get()
    obsH = obsH_entry.get()
    obsR = obsR_entry.get()
    nGuards = nGuards_entry.get()
    pos = selected_pos.get()
    randomize = random_var.get()
    alg = selected_alg.get()
    keepNS = keepNS_var.get()
    enableShow = show_var.get()
    verbose = verbose_var.get()
    machineLearning = ml_var.get()

    if machineLearning:
        args = ["python", "psoMain.py", "--name", name, "--height", obsH, "--radius", obsR, "--numGuards", nGuards]
        if keepNS:
            args.append("--keepNS") # Only valid in Machine Learning
    else:
        args = ["python", "opMain.py", "--name", name, "--height", obsH, "--radius", obsR, "--numGuards", nGuards]

    if pos=="squared":
        args.append("--square")
    if alg=="ILP":
        args.append("--ilp")
    if verbose:
        args.append("--verbose")
    if enableShow:
        args.append("--show")
    if randomize:
        args.append("--randomize")

    subprocess.run(args)

# Create main window
root = tk.Tk()
root.title("Drone Input Dialog")
root.geometry("920x250")

# Name label and entry
tk.Label(root, text="Filename:").grid(row=0, column=0, padx=5, pady=5)
name_entry = tk.Entry(root)
name_entry.grid(row=1, column=0, padx=5, pady=5)
name_entry.insert(0, "../tiles/heightmap.png")

# Obs & Guards
obs_frame = tk.LabelFrame(root, text="Guards & Observer", width=350, height=150)
obs_frame.grid(row=2, column=0, padx=5, pady=5)
obs_frame.grid_propagate(False)

tk.Label(obs_frame, text="Obs H:").grid(row=2, column=0, padx=5, pady=5)
obsH_entry = tk.Entry(obs_frame)
obsH_entry.grid(row=2, column=1, padx=5, pady=5)
obsH_entry.insert(0, "10")

tk.Label(obs_frame, text="Obs R:").grid(row=3, column=0, padx=5, pady=10)
obsR_entry = tk.Entry(obs_frame)
obsR_entry.grid(row=3, column=1, padx=5, pady=5)
obsR_entry.insert(0, "60")

tk.Label(obs_frame, text="Number of Guards:").grid(row=4, column=0, padx=5, pady=5)
nGuards_entry = tk.Entry(obs_frame)
nGuards_entry.grid(row=4, column=1, padx=5, pady=5)
nGuards_entry.insert(0, "50")

# Guard Positions
pos_frame = tk.LabelFrame(root, text="Guard Positions", width=170, height=150)
pos_frame.grid(row=2, column=3, padx=5, pady=5)
pos_frame.grid_propagate(False)

selected_pos = tk.StringVar(value="fibonacci")  # default
tk.Label(pos_frame, text="Select guard positions:").grid(row=2, column=3, padx=5, pady=5)
tk.Radiobutton(pos_frame, text="Fibonacci Lattice", variable=selected_pos, value="fibonacci").grid(row=3, column=3, padx=5, pady=5)
tk.Radiobutton(pos_frame, text="Squared uniform", variable=selected_pos, value="squared").grid(row=4, column=3, padx=5, pady=5)
random_var = tk.BooleanVar()
tk.Checkbutton(pos_frame, text="Randomize (Sq Un)", variable=random_var).grid(row=5, column=3, padx=5, pady=5)

# Algorithms 
alg_frame = tk.LabelFrame(root, text="Algorithm", width=140, height=150)
alg_frame.grid(row=2, column=4, padx=5, pady=5)
alg_frame.grid_propagate(False)

selected_alg = tk.StringVar(value="BSF")  # default
tk.Label(alg_frame, text="Select Algorithm:").grid(row=2, column=4, padx=5, pady=5)
tk.Radiobutton(alg_frame, text="BSF", variable=selected_alg, value="BSF").grid(row=3, column=4, padx=5, pady=5)
tk.Radiobutton(alg_frame, text="Mixed ILP", variable=selected_alg, value="ILP").grid(row=4, column=4, padx=5, pady=5)

# Checkboxes
option_frame = tk.LabelFrame(root, text="Options", width=190, height=150)
option_frame.grid(row=2, column=5, padx=5, pady=5)
option_frame.grid_propagate(False)

keepNS_var = tk.BooleanVar()
show_var = tk.BooleanVar()
verbose_var = tk.BooleanVar()
ml_var = tk.BooleanVar()
tk.Checkbutton(option_frame, text="Show Terrain", variable=show_var).grid(row=2, column=5, padx=5, pady=5)
tk.Checkbutton(option_frame, text="Verbose", variable=verbose_var).grid(row=3, column=5, padx=5, pady=5)
tk.Checkbutton(option_frame, text="Machine Learning", variable=ml_var).grid(row=4, column=5, padx=5, pady=5)
tk.Checkbutton(option_frame, text="Keep NS (Only for ML)", variable=keepNS_var).grid(row=5, column=5, padx=5, pady=5)

# Submit button
tk.Button(root, text="Run", command=on_run).grid(row=1, column=3, padx=5, pady=5)

# Run the app
root.mainloop()
