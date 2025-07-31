import os
import shutil
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox

def select_mod_folder():
    folder = filedialog.askdirectory()
    if folder:
        mod_folder_var.set(folder)

def install_mods():
    mod_folder = mod_folder_var.get()
    if not os.path.isdir(mod_folder):
        messagebox.showerror("Помилка", "Невірний шлях до папки модів.")
        return

    kpf_dir = os.getcwd()  # Файли .kpf мають бути біля скрипта

    for folder_name in os.listdir(mod_folder):
        mod_path = os.path.join(mod_folder, folder_name)
        if not os.path.isdir(mod_path):
            continue

        kpf_path = os.path.join(kpf_dir, f"{folder_name}.kpf")
        backup_path = f"{kpf_path}.original"

        if not os.path.isfile(kpf_path):
            print(f"[Пропущено] {kpf_path} не знайдено.")
            continue

        # Створити бекап, якщо ще не існує
        if not os.path.exists(backup_path):
            shutil.copy2(kpf_path, backup_path)
            print(f"[Бекап] Створено {backup_path}")

        # Створюємо тимчасову копію архіву
        temp_zip_path = f"{kpf_path}.temp.zip"
        with zipfile.ZipFile(kpf_path, 'r') as zip_read:
            zip_read.extractall("temp_extract")

        # Копіюємо нові файли з модпапки
        for root, _, files in os.walk(mod_path):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), mod_path)
                dest_path = os.path.join("temp_extract", rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(os.path.join(root, file), dest_path)

        # Перезаписуємо архів з оновленим вмістом
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_write:
            for root, _, files in os.walk("temp_extract"):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, "temp_extract")
                    zip_write.write(full_path, arcname)

        shutil.move(temp_zip_path, kpf_path)
        shutil.rmtree("temp_extract", ignore_errors=True)
        print(f"[Оновлено] {kpf_path}")

    messagebox.showinfo("Готово", "Моди встановлено.")

def rollback_mods():
    kpf_dir = os.getcwd()
    mod_folder = mod_folder_var.get()

    if not os.path.isdir(mod_folder):
        messagebox.showerror("Помилка", "Невірний шлях до папки модів.")
        return

    for folder_name in os.listdir(mod_folder):
        kpf_path = os.path.join(kpf_dir, f"{folder_name}.kpf")
        backup_path = f"{kpf_path}.original"

        if os.path.exists(backup_path):
            if os.path.exists(kpf_path):
                os.remove(kpf_path)
            shutil.copy2(backup_path, kpf_path)
            print(f"[Відновлено] {kpf_path}")
        else:
            print(f"[Пропущено] Бекап для {folder_name}.kpf не знайдено.")

    messagebox.showinfo("Готово", "Відкат завершено.")

# === GUI ===
root = tk.Tk()
root.title("SS2UA Mod Installer")

mod_folder_var = tk.StringVar()

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

tk.Label(frame, text="Шлях до моду:").grid(row=0, column=0, sticky="w")
tk.Entry(frame, textvariable=mod_folder_var, width=50).grid(row=0, column=1)
tk.Button(frame, text="Обрати...", command=select_mod_folder).grid(row=0, column=2, padx=5)

tk.Button(frame, text="Встановити", command=install_mods, bg="lightgreen").grid(row=1, column=1, pady=10, sticky="ew")
tk.Button(frame, text="Відкат", command=rollback_mods, bg="lightcoral").grid(row=2, column=1, pady=5, sticky="ew")

root.mainloop()
