import pygame
import tkinter as tk
from tkinter import filedialog, ttk
import os
import subprocess
import json
import ctypes
from PIL import ImageTk, Image

PERSISTENT_FILE = "program_list.json"
GRID_COLUMNS = 3  # Le nombre de colonnes dans la grille de programmes


# Initialisation de pygame
pygame.init()

# Configuration de la manette
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# Fonctions pour gérer les événements de la manette
def button_a_pressed():
    selected_frame = get_selected_frame()
    if selected_frame is None:
        select_first_frame()
        selected_frame = get_selected_frame()

    if selected_frame:
        program_data = selected_frame.program_data
        if program_data[2]:
            command = program_data[2]
        else:
            command = program_data[1]

        if program_data[3]:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", command, None, None, 1)
        else:
            subprocess.Popen(command, shell=True)


def get_selected_frame():
    for frame in programs_grid.grid_slaves():
        if frame.cget("bg") == "blue":
            return frame
    return None

def select_first_frame():
    first_frame = programs_grid.grid_slaves(row=0, column=0)[0]
    first_frame.config(bg="blue")

def navigate_up():
    selected_frame = get_selected_frame()
    if selected_frame is None:
        select_first_frame()
    else:
        row, column = selected_frame.grid_info()["row"], selected_frame.grid_info()["column"]
        if row > 0:
            selected_frame.config(bg="SystemButtonFace")
            programs_grid.grid_slaves(row=row - 1, column=column)[0].config(bg="blue")

def navigate_down():
    selected_frame = get_selected_frame()
    if selected_frame is None:
        select_first_frame()
    else:
        row, column = selected_frame.grid_info()["row"], selected_frame.grid_info()["column"]
        if row < programs_grid.grid_size()[1] - 1:
            selected_frame.config(bg="SystemButtonFace")
            programs_grid.grid_slaves(row=row + 1, column=column)[0].config(bg="blue")

def navigate_left():
    selected_frame = get_selected_frame()
    if selected_frame is None:
        select_first_frame()
    else:
        row, column = selected_frame.grid_info()["row"], selected_frame.grid_info()["column"]
        if column > 0:
            selected_frame.config(bg="SystemButtonFace")
            programs_grid.grid_slaves(row=row, column=column - 1)[0].config(bg="blue")

def navigate_right():
    selected_frame = get_selected_frame()
    if selected_frame is None:
        select_first_frame()
    else:
        row, column = selected_frame.grid_info()["row"], selected_frame.grid_info()["column"]
        if column < programs_grid.grid_size()[0] - 1:
            selected_frame.config(bg="SystemButtonFace")
            programs_grid.grid_slaves(row=row, column=column + 1)[0].config(bg="blue")



# Gestion des événements de la manette
def handle_joystick_events():
    pygame.event.pump()
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # Bouton A
                button_a_pressed()
            elif event.button == 2:  # Bouton X
                add_program_window()
        elif event.type == pygame.JOYHATMOTION:
            if event.value == (0, 1):  # D-pad haut
                navigate_up()
            elif event.value == (0, -1):  # D-pad bas
                navigate_down()
            elif event.value == (-1, 0):  # D-pad gauche
                navigate_left()
            elif event.value == (1, 0):  # D-pad droite
                navigate_right()


def remove_program():
    selected_frame = None
    for frame in programs_grid.grid_slaves():
        if "selected" in frame.state():
            selected_frame = frame
            break

    if selected_frame is not None:
        selected_frame.destroy()
        save_program_list()


def create_program_frame(container, program):
    program_name, file_path, custom_command, run_as_admin, image_path = program

    frame = tk.Frame(container, bd=2, relief="groove", padx=10, pady=10)
    frame.grid_propagate(False)

    # Ajout de l'attribut program_data à l'objet Frame
    frame.program_data = program

    if image_path and os.path.exists(image_path):
        image = Image.open(image_path).resize((100, 100), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        image_label = tk.Label(frame, image=photo)
        image_label.image = photo
        image_label.pack()

    label = tk.Label(frame, text=program_name, wraplength=100)
    label.pack()

    return frame


def save_program_list():
    program_list = []
    for frame in programs_grid.grid_slaves():
        program_data = frame.program_data
        program_list.append(program_data)

    with open(PERSISTENT_FILE, "w") as f:
        json.dump(program_list, f)


def load_program_list():
    if os.path.exists(PERSISTENT_FILE):
        with open(PERSISTENT_FILE, "r") as f:
            program_list = json.load(f)

        row, column = 0, 0
        for program in program_list:
            frame = create_program_frame(programs_grid, tuple(program))
            frame.grid(row=row, column=column, sticky="nsew")

            column += 1
            if column >= GRID_COLUMNS:
                column = 0
                row += 1


def add_program_to_grid(program_info):
    program_name, file_path, custom_command, run_as_admin, image_path = program_info
    try:
        image = Image.open(image_path).resize((100, 100), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
    except:
        photo = None

    frame = ttk.Frame(programs_grid)
    frame.grid(row=len(program_list) // 3, column=len(program_list) % 3)

    image_label = ttk.Label(frame, image=photo)
    image_label.image = photo
    image_label.pack()

    text_label = ttk.Label(frame, text=program_name)
    text_label.pack()

    program_list.append((program_name, file_path, custom_command, run_as_admin, image_path))


def add_program_window():
    def add_program():
        file_path = filedialog.askopenfilename()
        program_name = os.path.basename(file_path)
        file_path_var.set(file_path)
        program_name_var.set(program_name)

    def add_image():
        image_path = filedialog.askopenfilename()
        image_path_var.set(image_path)

    def submit():
        program_name = program_name_var.get()
        file_path = file_path_var.get()
        custom_command = custom_command_var.get()
        run_as_admin = run_as_admin_var.get()
        image_path = image_path_var.get()

        program = (program_name, file_path, custom_command, run_as_admin, image_path)
        frame = create_program_frame(programs_grid, program)
        index = len(programs_grid.grid_slaves())
        frame.grid(row=index//3, column=index % 3, sticky=tk.W+tk.E+tk.N+tk.S)

        save_program_list()
        add_program_win.destroy()

    add_program_win = tk.Toplevel(root)
    add_program_win.title("Ajouter un programme")
    add_program_win.transient(root)

    program_name_var = tk.StringVar()
    file_path_var = tk.StringVar()
    custom_command_var = tk.StringVar()
    run_as_admin_var = tk.BooleanVar()
    image_path_var = tk.StringVar()

    ttk.Label(add_program_win, text="Nom du programme :").grid(row=0, column=0, sticky=tk.W)
    ttk.Entry(add_program_win, textvariable=program_name_var).grid(row=0, column=1)

    ttk.Label(add_program_win, text="Chemin du programme :").grid(row=1, column=0, sticky=tk.W)
    ttk.Entry(add_program_win, textvariable=file_path_var).grid(row=1, column=1)
    ttk.Button(add_program_win, text="Parcourir", command=add_program).grid(row=1, column=2)

    ttk.Label(add_program_win, text="Commande personnalisée :").grid(row=2, column=0, sticky=tk.W)
    ttk.Entry(add_program_win, textvariable=custom_command_var).grid(row=2, column=1)

    ttk.Checkbutton(add_program_win, text="Exécuter en tant qu'administrateur", variable=run_as_admin_var).grid(row=3, columnspan=2)

    ttk.Label(add_program_win, text="Image du programme :").grid(row=4, column=0, sticky=tk.W)
    ttk.Entry(add_program_win, textvariable=image_path_var).grid(row=4, column=1)
    ttk.Button(add_program_win, text="Parcourir", command=add_image).grid(row=4, column=2)

    ttk.Button(add_program_win, text="Ajouter", command=submit).grid(row=5, columnspan=2)

    # Centre la fenêtre d'ajout de programme
    add_program_win.update_idletasks()  # Mise à jour des tâches en attente pour obtenir les dimensions correctes
    width = add_program_win.winfo_width()
    height = add_program_win.winfo_height()
    screen_width = add_program_win.winfo_screenwidth()
    screen_height = add_program_win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    add_program_win.geometry(f"{width}x{height}+{x}+{y}")


root = tk.Tk()
root.title("Lanceur de programmes")
root.state('zoomed')

program_list = []

scrollbar = ttk.Scrollbar(root, orient="vertical")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

programs_grid = ttk.Frame(root)
programs_grid.pack(fill=tk.BOTH, expand=True)

programs_grid.columnconfigure(0, weight=1)
programs_grid.columnconfigure(1, weight=1)
programs_grid.columnconfigure(2, weight=1)

# Charger la liste des programmes sauvegardés
load_program_list()

add_button = tk.Button(root, text="Ajouter", command=add_program_window)
add_button.pack(side=tk.LEFT)

remove_button = tk.Button(root, text="Supprimer", command=remove_program)
remove_button.pack(side=tk.RIGHT)

while True:
    # Gérer les événements de la manette
    handle_joystick_events()

    # Mettre à jour l'interface graphique
    root.update_idletasks()
    root.update()
