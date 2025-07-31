import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class SyntaxCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Перевірка синтаксису")
        self.file_path = None
        self.lines = []
        self.current_line_index = 0  # Звідки продовжувати пошук

        # --- GUI ---
        frame = tk.Frame(root)
        frame.pack(padx=10, pady=10, fill='x')

        self.path_entry = tk.Entry(frame, width=60)
        self.path_entry.pack(side='left', padx=(0,5))

        browse_btn = tk.Button(frame, text="Огляд...", command=self.browse_file)
        browse_btn.pack(side='left')

        self.process_btn = tk.Button(root, text="Процес", command=self.process_file)
        self.process_btn.pack(pady=5)

        self.output = scrolledtext.ScrolledText(root, width=80, height=20, state='disabled', font=("Consolas", 10))
        self.output.pack(padx=10, pady=10)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Виберіть файл",
            filetypes=[("Text files", "*.txt *.str *.cfg"), ("All files", "*.*")]
        )
        if filename:
            self.file_path = filename
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, filename)
            self.load_file()
            self.current_line_index = 0
            self.clear_output()

    def load_file(self):
        try:
            with open(self.file_path, encoding='utf-8') as f:
                self.lines = f.readlines()
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося відкрити файл:\n{e}")
            self.lines = []

    def clear_output(self):
        self.output.configure(state='normal')
        self.output.delete(1.0, tk.END)
        self.output.configure(state='disabled')

    def append_output(self, text):
        self.output.configure(state='normal')
        self.output.insert(tk.END, text + '\n')
        self.output.configure(state='disabled')
        self.output.see(tk.END)

    def process_file(self):
        if not self.file_path:
            messagebox.showwarning("Увага", "Спочатку виберіть файл.")
            return
        if not self.lines:
            messagebox.showwarning("Увага", "Файл порожній або не завантажений.")
            return

        errors, last_err_line = self.check_syntax(self.lines, self.current_line_index)

        if errors:
            for err_line_num, err_text, err_msg in errors:
                self.append_output(f"Рядок {err_line_num}: {err_msg}")
                self.append_output(f"   >> {err_text.strip()}")
                self.append_output('')

            self.current_line_index = last_err_line + 1  # Продовжимо пошук з останньої помилки
        else:
            if self.current_line_index >= len(self.lines):
                self.append_output("Перевірка завершена. Помилок не знайдено.")
            else:
                self.append_output("Перевірка завершена. Більше помилок не знайдено.")
            self.current_line_index = len(self.lines)  # Всі рядки перевірені

    def check_syntax(self, lines, start_line):
        section_pattern = re.compile(r'^\[\w+\/?\w*\]$')
        var_pattern = re.compile(r'^\$([\w/]+)\s*=\s*"(.*)"$')
        escape_sequences = ['\\n', '\\t', '\\"', '\\\\']

        errors = []
        current_section = None

        for i in range(start_line, len(lines)):
            line_num = i + 1
            line = lines[i].strip()

            # Ігноруємо повністю коментарі, що починаються з //
            if line.startswith('//') or not line:
                continue

            # Видаляємо коментарі, які можуть йти після коду, починаючи з //
            if '//' in line:
                line = line.split('//', 1)[0].rstrip()

            if not line:
                continue

            if line.startswith('[') and line.endswith(']'):
                if not section_pattern.match(line):
                    errors.append((line_num, lines[i], "Некоректна секція"))
                    return errors, i
                else:
                    current_section = line
                continue

            m = var_pattern.match(line)
            if not m:
                errors.append((line_num, lines[i], "Некоректний формат змінної"))
                return errors, i

            var_name, var_value = m.groups()

            if var_value.count('"') % 2 != 0:
                errors.append((line_num, lines[i], "Непарні лапки у значенні"))
                return errors, i

            escapes_found = re.findall(r'\\.', var_value)
            for esc in escapes_found:
                if esc not in escape_sequences:
                    errors.append((line_num, lines[i], f"Невідома escape-послідовність {esc}"))
                    return errors, i

            format_specifiers = re.findall(r'%[ds]', var_value)
            for fs in format_specifiers:
                if fs not in ['%d', '%s']:
                    errors.append((line_num, lines[i], f"Непідтримуваний форматний специфікатор {fs}"))
                    return errors, i

        return errors, len(lines)



if __name__ == "__main__":
    root = tk.Tk()
    app = SyntaxCheckerApp(root)
    root.mainloop()
