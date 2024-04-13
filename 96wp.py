import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import ImageTk, Image
import re
from matplotlib.patches import Patch

def update_plot(plate, label):
    """
    Update the matplotlib plot to visually represent the wells with legend values.
    Highlight wells with different colors based on legend values.
    Add legends for each unique legend_name sorted by their appearance in the plate.
    """
    rows = len(plate)
    cols = len(plate[0])

    # Create a color map for visualization
    unique_legend_entries = set(entry for row in plate for entry in row if entry)
    color_map = {entry: f'C{i}' for i, entry in enumerate(unique_legend_entries)}

    # Plot the 8x12 grid
    fig, ax = plt.subplots(figsize=(15, 10))  # Adjust the figure size as needed
    ax.set_xticks([])
    ax.set_yticks([])

    # Add numbers on top above the first row
    for j in range(cols):
        ax.text(j + 0.5, rows + 0.7, str(j + 1), ha='center', va='center', color='black', fontsize=26)

    # Fill the grid with colors based on legend values
    for i in range(rows):
        for j in range(cols):
            entry = plate[i][j]
            if entry:
                color = color_map.get(entry, 'whitesmoke')
                ax.fill_between([j, j + 1], i, i + 1, color=color, edgecolor='black')
            else:
                # Empty squares are whitesmoke
                ax.fill_between([j, j + 1], i, i + 1, color='whitesmoke', edgecolor='black')

    ax.set_xlim(-1, cols)
    ax.set_ylim(0, rows + 1)
    ax.invert_yaxis()  # Invert y-axis to match the plate layout

    # Add letters on the left side
    for i in range(rows):
        ax.text(-0.5, i + 0.5, chr(65 + i), ha='center', va='center', color='black', fontsize=26)

    # Add legends for each unique legend_name sorted by their appearance in the plate
    legends = [Patch(color=color, label=entry) for entry, color in sorted(color_map.items(), key=lambda x: plate_to_str(plate).find(x[0]))]
    ax.legend(handles=legends, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=26)

    # Remove the surrounding square from the plot
    ax.axis('off')
    
    ax.set_title(f"{label}\n", fontsize=26)

    # Show the plot
    plt.tight_layout()  # Adjust subplot parameters to give specified padding
    plt.show()
    
    # Create the variable name for the plot dynamically
    variable_name = f"plot_plate_{label}"
    
    # Store the plot as a variable
    globals()[variable_name] = fig
    
    # Add the plot to the dictionary
    plots[label] = fig

# Dictionary to store the plots
plots = {}

def plate_to_str(plate):
    """
    Convert the plate into a string representation.
    """
    return ''.join(''.join(row) for row in plate)


def display_all_plots(plots, figsize=(29.7, 21)):
    # Calculate the number of plots
    num_plots = len(plots)
    
    # Calculate the number of rows and columns for the subplot grid
    num_rows = 2
    num_cols = (num_plots + 1) // 2  # Ensure at least 2 columns

    # Set the figsize for the entire grid of plots
    fig, axs = plt.subplots(num_rows, num_cols, figsize=figsize)
        
    # Flatten the axs array if it's more than one row
    axs = axs.flatten() if num_rows > 1 else [axs]

    # Iterate over the plots dictionary and display each plot in a subplot
    for i, (label, plot) in enumerate(plots.items()):
        # Display each plot in the corresponding subplot
        axs[i].imshow(plot.canvas.renderer._renderer)
        axs[i].axis('off')

    # Hide any remaining empty subplots
    for j in range(num_plots, num_rows * num_cols):
        axs[j].axis('off')

    # Display the figure
    plt.savefig('plot.jpg', dpi=300)

# Start Window

window = ctk.CTk()
window.title('Plate Layout')
window.geometry('300x400')

labels = ['ConditionName', 'ConditionValue', 'CellsPerWell', 'Donor']




####

def update_button_text(button, entry, label):
    row, col = button.grid_info()["row"] - 1, button.grid_info()["column"] - 1
    if button.cget("text") == "":
        button.configure(text=entry.get(), bg="dark gray")
        plate_dict[label][row][col] = entry.get()  
    else:
        button.configure(text="", bg="SystemButtonFace")
        plate_dict[label][row][col] = ''
        
    # Save plate information to file
    with open(f"{label}_plate.json", "w") as f:
        json.dump(plate_dict[label], f)

def load_plate(label):
    try:
        with open(f"{label}_plate.json", "r") as f:
            plate = json.load(f)
            return plate
    except FileNotFoundError:
        return [['' for _ in range(12)] for _ in range(8)]


# Dictionary to store plate variables for each label
plate_dict = {}
for label in labels:
    # Load plate information from file or initialize a new plate
    plate_dict[label] = load_plate(label)

def new_window(label):
    new_window = ctk.CTkToplevel()
    new_window.title(label)
    new_window.geometry('1000x500')
    
    menu_frame = ctk.CTkFrame(master=new_window)
    plate_frame = ctk.CTkFrame(master=new_window)
    
    # Menu place layout
    menu_frame.place(x=0, y=0, relwidth=0.2, relheight=1)  # to the left

    label_n = ctk.CTkLabel(master=menu_frame, text=label)
    label_n.pack()

    entry = ctk.CTkEntry(master=menu_frame)
    entry.pack()

    # Plate frame layout
    plate_frame.place(relx=0.2, y=0, relwidth=0.8, relheight=1)

    buttons = []
    for row in range(1, 9):
        row_buttons = []
        for col in range(1, 13):
            btn_text = plate_dict[label][row-1][col-1]  # Get the text from the plate dictionary
            btn = tk.Button(plate_frame, text=btn_text, width=8, height=4, font=('Arial', 16))
            btn.grid(row=row, column=col, padx=5, pady=5)
            btn.configure(command=lambda b=btn, e=entry, l=label: update_button_text(b, e, l))  
            row_buttons.append(btn)
        buttons.append(row_buttons)
        
    # Label
    for col in range(1, 13):
        label = ctk.CTkLabel(plate_frame, text=col)
        label.grid(row=0, column=col, padx=1, pady=1)

    for row, letter in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']):
        label = ctk.CTkLabel(plate_frame, text=letter)
        label.grid(row=row + 1, column=0, padx=1, pady=1)   
        
        
          
# Buttons Start Window

def graph(label):
    plate = plate_dict[label] 
    update_plot(plate, label)

    

for label in labels:
    # Frame to hold the buttons
    frame = ctk.CTkFrame(window)
    frame.pack(fill="x", padx=10, pady=5)

    # Button to open new window
    start_button = ctk.CTkButton(frame, text=label, command=lambda l=label: new_window(l))
    start_button.pack(side="left", fill="both", expand=True)
    
    # Plot button
    plot_button = ctk.CTkButton(frame, text="Plot", command=lambda l=label: graph(l))
    plot_button.pack(side="left", fill="both", expand=True, padx=5)

####

def graph_all():
    display_all_plots(plots)

plot_all = ctk.CTkButton(window, text = 'Plot All', command = graph_all)
plot_all.pack(expand = True)

        
####


def reset_plates():
    for label in plate_dict:
        plate_dict[label] = [['' for _ in range(12)] for _ in range(8)]
        
## Reset Button

reset_button = ctk.CTkButton(master=window, text='Reset', command=reset_plates)
reset_button.pack(expand=True)


## Quit Button

def close_window():
    window.destroy()

quit_button = ctk.CTkButton(master=window, text='Quit', command=close_window)
quit_button.pack(expand=True)

####
    
    
# Run
window.mainloop()

