import os

import tkinter as tk
from tkinter import ttk

types = []
count = []

def recursive_folder_scan(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1]  # розширення
            file_extension = file_extension.upper()
            if file_extension not in types:
                types.append(file_extension)
                count.append(1)
            else:
                t_id = types.index(file_extension)
                count[t_id] += 1

def create_table(tab, columns):
    tree = ttk.Treeview(tab, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')

    tree.pack(expand=True, fill='both')

    return tree

def sort_column(tree, col, reverse):
    def convert(val):
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return val.lower()
    
    data = [(tree.set(k, col), k) for k in tree.get_children('')]
    data.sort(key=lambda x: convert(x[0]), reverse=reverse)
    for index, (_, k) in enumerate(data):
        tree.move(k, '', index)
    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

def main():
    root = tk.Tk()
    root.title("File Format Table")
    root.geometry("600x800")

    tab_control = ttk.Notebook(root)

    # Таб 1
    tab1 = ttk.Frame(tab_control)
    tab_control.add(tab1, text='Files')
    table1 = create_table(tab1, ['Type', 'Count'])

    for _ in range(len(types)):
        table1.insert('', tk.END, values=[types[_], count[_]])
    sort_column(table1, 1, reverse=True)

    tab_control.pack(expand=1, fill='both')
    root.mainloop()

if __name__ == '__main__':
    recursive_folder_scan('.')
    main()
