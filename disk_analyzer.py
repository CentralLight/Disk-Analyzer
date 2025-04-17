import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import pyperclip
import ctypes

def is_hidden(path):
    """Verifica se una cartella è nascosta"""
    if os.name == 'nt':  # Controllo su Windows
        attribute = ctypes.windll.kernel32.GetFileAttributesW(path)
        return attribute & 2  # FILE_ATTRIBUTE_HIDDEN (valore 2)
    else:  # Controllo su Linux/macOS
        return os.path.basename(path).startswith('.')


def get_size(path):
    """Calcola la dimensione della cartella o dei file (se l'opzione è attivata)."""
    total_size = 0
    try:
        if os.path.isfile(path):  
            return os.path.getsize(path)

        for item in os.scandir(path):
            if is_hidden(item.path):
                print("Nascosto: " + item.path)
                continue

            root_window.update_idletasks()
            
            if analyze_files and os.path.isfile(item.path):  
                total_size += item.stat().st_size  
            elif not analyze_files and os.path.isdir(item.path):  
                total_size += get_size(item.path)  
            elif not analyze_files and os.path.isfile(item.path):
                total_size += item.stat().st_size  
    except Exception as e:
        log_error(f"Errore durante il calcolo della dimensione per {path}: {e}")

    return total_size

def format_size(size):
    """Formatta la dimensione in MB o GB e imposta il colore della riga"""
    if size > 10**10:
        return f"{size / 10**9:.2f} GB", 'yellow'
    elif size > 10**9:
        return f"{size / 10**9:.2f} GB", 'black'
    else:
        return f"{size / 10**6:.2f} MB", 'black'

def analyze_folder():
    """Analizza la cartella selezionata e ne calcola le dimensioni"""
    global analyzing, last_folder
    analyzing = True
    cancel_button.config(state=tk.NORMAL)
    repeat_button.config(state=tk.DISABLED)
    folder = filedialog.askdirectory()
    if not folder:
        return
    
    last_folder = folder
    run_analysis(folder)

def run_analysis(folder):
    """Esegue l'analisi sulla cartella specificata"""
    global analyzing
    tree.delete(*tree.get_children())
    progress_label.config(text=f"Sto analizzando {os.path.basename(folder)}")  
    progress_bar['value'] = 0
    
    items = []
    def scan():
        """Esegue la scansione della cartella e aggiorna la UI"""
        nonlocal items
        all_items = list(os.scandir(folder))
        total_items = len(all_items)

        if not all_items:  # Se la cartella è vuota, mostra un popup
            messagebox.showinfo("Attenzione", f"Non è stata trovata nessuna cartella in '{folder}'!")
            progress_label.config(text="Nessuna cartella trovata")
            cancel_button.config(state=tk.DISABLED)
            repeat_button.config(state=tk.NORMAL)
            return

        for index, item in enumerate(all_items):
            if not analyzing:
                break
            
            if analyze_files and os.path.isfile(item.path):
                size = os.path.getsize(item.path)  
                progress_label.config(text=f"Sto analizzando {os.path.basename(item.path)}")
                items.append((item.name, size, item.path))
            elif not analyze_files and os.path.isdir(item.path):
                size = get_size(item.path)
                progress_label.config(text=f"Sto analizzando {os.path.basename(item.path)}") 
                items.append((item.name, size, item.path))
            
            progress_bar['value'] = (index + 1) / total_items * 100
            root_window.update_idletasks()

        items.sort(key=lambda x: x[1], reverse=True)  

        for name, size, path in items:
            size_formatted, color = format_size(size)
            tree.insert("", tk.END, values=(name, size_formatted, path), tags=(color,))

        progress_label.config(text="Analisi completata")
        cancel_button.config(state=tk.DISABLED)
        repeat_button.config(state=tk.NORMAL)
        progress_bar['value'] = 100
    
    threading.Thread(target=scan, daemon=True).start()

def repeat_analysis():
    """Ripete l'ultima analisi effettuata"""
    if last_folder:
        run_analysis(last_folder)

def cancel_analysis():
    """Interrompe l'analisi in corso"""
    global analyzing
    analyzing = False
    progress_label.config(text="Analisi annullata")
    cancel_button.config(state=tk.DISABLED)

def open_folder(event):
    """Apre la cartella selezionata con doppio click"""
    item = tree.selection()
    if item:
        path = tree.item(item, "values")[2]
        subprocess.Popen(f'explorer "{path}"')

def copy_path():
    """Copia il percorso della cartella selezionata"""
    item = tree.selection()
    if item:
        path = tree.item(item, "values")[2]
        pyperclip.copy(path)

def log_error(message):
    """Registra gli errori in un file di log"""
    os.makedirs("logs", exist_ok=True)
    with open("logs/error.log", "a") as log_file:
        log_file.write(message + "\n")

def toggle_analyze_files():
    """Attiva o disattiva l'analisi dei file"""
    global analyze_files
    analyze_files = not analyze_files
    analyze_menu.entryconfig(0, label=f"Analizza File {'✓' if analyze_files else ''}")

# Configurazione della finestra principale
root_window = tk.Tk()
root_window.geometry("400x500")
root_window.configure(bg="#232323")
root_window.title("Disk Analyzer")

# Menu Opzioni
menu_bar = tk.Menu(root_window)
analyze_menu = tk.Menu(menu_bar, tearoff=0)
analyze_menu.add_command(label="Analizza File", command=toggle_analyze_files)
menu_bar.add_cascade(label="Opzioni", menu=analyze_menu)
root_window.config(menu=menu_bar)

# Menu contestuale
context_menu = tk.Menu(root_window, tearoff=0)
context_menu.add_command(label="Copy path", command=copy_path)

def show_context_menu(event):
    """Mostra il menu contestuale"""
    context_menu.post(event.x_root, event.y_root)

tree = ttk.Treeview(root_window, columns=("Name", "Size", "Path"), show="headings")
tree.heading("Name", text="Folder")
tree.heading("Size", text="Size")
tree.heading("Path", text="Path")
tree.column("Name", width=100)
tree.column("Size", width=100)
tree.column("Path", width=150)
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

tree.tag_configure("yellow", background="yellow")
tree.bind("<Double-1>", open_folder)
tree.bind("<Button-3>", show_context_menu)

progress_label = tk.Label(root_window, text="", fg="white", bg="#232323")
progress_label.pack()

progress_bar = ttk.Progressbar(root_window, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

top_frame = tk.Frame(root_window, bg="#232323")
top_frame.pack(pady=10)

select_button = tk.Button(top_frame, text="Select Folder", command=analyze_folder, fg="white", bg="#333")
select_button.pack(side=tk.LEFT, padx=5)

cancel_button = tk.Button(top_frame, text="Cancel", command=cancel_analysis, state=tk.DISABLED, fg="white", bg="#333")
cancel_button.pack(side=tk.LEFT, padx=5)

repeat_button = tk.Button(top_frame, text="Repeat", command=repeat_analysis, state=tk.DISABLED, fg="white", bg="#333")
repeat_button.pack(side=tk.LEFT, padx=5)

analyzing = False
analyze_files = False
last_folder = None

root_window.mainloop()
