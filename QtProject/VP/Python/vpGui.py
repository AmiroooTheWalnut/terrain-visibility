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
    runML = ml_var.get()
    mlAlg = ml_alg.get()

    if runML:
        if mlAlg == "PSO":
            args = ["python", "psoMain.py", "--name", name, "--height", obsH, "--radius", obsR, "--numGuards", nGuards]
        elif mlAlg == "PSO Staged":
            args = ["python", "psoMainStages.py", "--name", name, "--height", obsH, "--radius", obsR, "--numGuards", nGuards]
        elif mlAlg == "RL":
            args = ["python", "rlMain.py", "--name", name, "--height", obsH, "--radius", obsR, "--numGuards", nGuards]
    else:
        args = ["python", "opMain.py", "--name", name, "--height", obsH, "--radius", obsR, "--numGuards", nGuards]

    if (runML and not mlAlg == "RL") and keepNS:
        args.append("--keepNS") # Only valid in Machine Learning
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
  
    #print(args)
    subprocess.run(args)

def on_ml():
    if ml_var.get():
        r1.config(state="normal")
        r2.config(state="normal")
        r3.config(state="normal")
        r4.config(state="normal")
    else:
        ml_alg.set("x") # Clear all the radio buttons
        keepNS_var.set(False) # Clear check box value
        r1.config(state="disabled")
        r2.config(state="disabled")
        r3.config(state="disabled")
        r4.config(state="disabled")


# Create main window
root = tk.Tk()
root.title("Input Dialog")
root.geometry("860x350")

# Name label and entry
tk.Label(root, text="Filename:").grid(row=0, column=0, padx=5, pady=5)
name_entry = tk.Entry(root)
name_entry.grid(row=1, column=0, padx=5, pady=5)
name_entry.insert(0, "../tiles/heightmap.png")

# Obs & Guards
obs_frame = tk.LabelFrame(root, text="Guards & Observer", width=350, height=250)
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
random_var = tk.BooleanVar()
selected_pos = tk.StringVar(value="fibonacci")  # default
tk.Label(obs_frame, text="Initial Guard Positions:").grid(row=6, column=0, padx=5, pady=5)
tk.Radiobutton(obs_frame, text="Fibonacci Lattice", variable=selected_pos, value="fibonacci").grid(row=5, column=1, padx=5, pady=5)
tk.Radiobutton(obs_frame, text="Squared uniform", variable=selected_pos, value="squared").grid(row=6, column=1, padx=5, pady=5)
tk.Checkbutton(obs_frame, text="Randomize (Sq Un)", variable=random_var).grid(row=7, column=1, padx=5, pady=5)

# Algorithms 
alg_frame = tk.LabelFrame(root, text="Algorithm", width=140, height=150)
alg_frame.grid(row=2, column=2, padx=5, pady=5)
alg_frame.grid_propagate(False)

selected_alg = tk.StringVar(value="BSF")  # default
tk.Radiobutton(alg_frame, text="BSF", variable=selected_alg, value="BSF").grid(row=3, column=2, padx=5, pady=5)
tk.Radiobutton(alg_frame, text="Mixed ILP", variable=selected_alg, value="ILP").grid(row=4, column=2, padx=5, pady=5)

# Checkboxes
option_frame = tk.LabelFrame(root, text="General Options", width=140, height=150)
option_frame.grid(row=2, column=3, padx=5, pady=5)
option_frame.grid_propagate(False)
show_var = tk.BooleanVar()
verbose_var = tk.BooleanVar()
tk.Checkbutton(option_frame, text="Show Terrain", variable=show_var).grid(row=2, column=3, padx=5, pady=5)
tk.Checkbutton(option_frame, text="Verbose", variable=verbose_var).grid(row=3, column=3, padx=5, pady=5)

# Machine Learning
ml_frame = tk.LabelFrame(root, text="ML Options", width=180, height=200)
ml_frame.grid(row=2, column=4, padx=5, pady=5)
ml_frame.grid_propagate(False)
ml_var = tk.BooleanVar()
tk.Checkbutton(ml_frame, text="Machine Learning", variable=ml_var, command=on_ml).grid(row=3, column=4, padx=5, pady=5)

ml_alg = tk.StringVar(value="x")  # default to none of them
r1 = tk.Radiobutton(ml_frame, text="PSO", variable=ml_alg, value="PSO", state="disabled")
r1.grid(row=4, column=4, padx=5, pady=5)

r2 = tk.Radiobutton(ml_frame, text="PSO multi-stage", variable=ml_alg, value="PSO Staged", state="disabled")
r2. grid(row=5, column=4, padx=5, pady=5)

r3 = tk.Radiobutton(ml_frame, text="RL (PPO)", variable=ml_alg, value="RL", state="disabled")
r3.grid(row=7, column=4, padx=5, pady=5)

keepNS_var = tk.BooleanVar()
r4 = tk.Checkbutton(ml_frame, text="Keep NS (for PSO)", variable=keepNS_var, state="disabled")
r4.grid(row=6, column=4, padx=5, pady=5)

# Submit button
tk.Button(root, text="Run", command=on_run).grid(row=1, column=3, padx=5, pady=5)

# Run the app
root.mainloop()
