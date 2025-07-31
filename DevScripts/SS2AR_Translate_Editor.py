import tkinter as tk
from tkinter import ttk
from tkinter import font

start_src_o = 'C:\\Users\\prayd\\Desktop\\SS2 UA Project\\refactor\\o_src\\main.str'
start_src_m = 'C:\\Users\\prayd\\Desktop\\SS2 UA Project\\refactor\\m_src\\main.str'

original_text = None
tcons = []

class TranslateConnection:
    def __init__(self, title: str, reference: str, content: str):
        self.title = title
        self.reference = reference
        self.content = content

def validate_str_line(line):
    if line and not line.isspace():
        if not line.startswith("//"):
            return line
    return None

def escape_multiline_string(s: str) -> str:
    return s.replace('\n', '\\n')

def revert():
    set_new_text(original_text)

def fix_double_quotes(s):
    if s.endswith("\"\"\n"):
        return s[:len(s)-2]
    return s

def read_input():
    with open(src_orig_entry.get(), "r", encoding="utf-8") as file_o:
        src_orig = file_o.readlines()
    with open(src_mod_entry.get(), "r", encoding="utf-8") as file_m:
        src_mod = file_m.readlines()

    tcons.clear()

    #Цикл Читаємо орігу
    #для кожної строчки шукаємо в моді співпадіння
    #при співпадінні створюємо зв'язок

    # SRC_O read
    for line in src_orig:
        if validate_str_line(line):
            splt = line.split(':')
            # SRC_M read
            multiline = False
            for line2 in src_mod:
                if validate_str_line(line2) or multiline:
                    if not multiline:
                        splt2 = line2.split(':', 1)
                        # print(splt2)
                        if splt2[0] == splt[0]:
                            tcons.append(TranslateConnection(splt[0], splt[1][1:len(splt[1])-2], ""))

                            if splt2[1].count('"') % 2 != 0:
                                tcons[-1].content = splt2[1]
                                multiline = True
                            else:
                                tcons[-1].content = fix_double_quotes(splt2[1].rstrip())
                    else:
                        tcons[-1].content += fix_double_quotes(line2)
                        if line2[len(line2.rstrip())-1].rstrip() == '"':
                            multiline = False

    for t in tcons:
        print("\n\nTitle: " + t.title + "\nReference: " + t.reference + "\nContent: " + t.content, end='')

def remember_text_frame():
    global original_text
    original_text = text_area.get("1.0", tk.END)

def process_input():
    current_text = text_area.get("1.0", tk.END)
    lines = current_text.splitlines()

    updated_lines = []
    for line in lines:
        updated = False
        for t in tcons:
            if line.strip().startswith(t.reference + " = "):
                content = t.content.strip()

                # Видаляємо лапки на початку і в кінці, якщо є
                if content.startswith('"') and content.endswith('"'):
                    content = content[1:-1]

                content = escape_multiline_string(content)
                new_line = f'{t.reference} = "{content}"'

                updated_lines.append(new_line)
                updated = True
                break
        if not updated:
            updated_lines.append(line)

    updated_text = "\n".join(updated_lines)
    if validate_str_line(updated_text):
        set_new_text(updated_text)

def set_new_text(text):
    text_area.delete("1.0", tk.END)          # Очистити поле
    text_area.insert("1.0", text)  # Вставити новий текст

def main():
    global src_orig_entry, src_mod_entry, text_area

    # Створення головного вікна
    root = tk.Tk()
    root.title("SS2AR_Translate_Editor")
    root.geometry("800x800")

    # Фрейм для полів вводу та кнопки
    input_frame = ttk.Frame(root, padding="10")
    input_frame.pack(fill="x")

    # Поле SRC_ORIG
    ttk.Label(input_frame, text="SRC_ORIG:").grid(row=0, column=0, sticky="w")
    src_orig_entry = ttk.Entry(input_frame, width=60)
    src_orig_entry.grid(row=0, column=1, pady=5, padx=5, sticky="w")
    src_orig_entry.insert(0, start_src_o)

    # Поле SRC_MOD
    ttk.Label(input_frame, text="SRC_MOD:").grid(row=1, column=0, sticky="w")
    src_mod_entry = ttk.Entry(input_frame, width=60)
    src_mod_entry.grid(row=1, column=1, pady=5, padx=5, sticky="w")
    src_mod_entry.insert(0, start_src_m)

    # Кнопка Read праворуч
    read_button = ttk.Button(input_frame, text="Read", command=read_input)
    read_button.grid(row=0, column=2, padx=10)

    # Кнопка Remember праворуч
    remember_button = ttk.Button(input_frame, text="Remember", command=remember_text_frame)
    remember_button.grid(row=0, column=3, padx=10)

    # Кнопка Process праворуч
    process_button = ttk.Button(input_frame, text="Process..", command=process_input)
    process_button.grid(row=1, column=2, padx=10)

    # Кнопка Revert праворуч
    revert_button = ttk.Button(input_frame, text="Revert", command=revert)
    revert_button.grid(row=1, column=3, padx=10)

    # Текстове поле monospace
    text_frame = ttk.Frame(root, padding="10")
    text_frame.pack(fill="both", expand=True)

    monospace_font = font.Font(family="Courier New", size=12)
    text_area = tk.Text(text_frame, wrap="word", font=monospace_font)
    text_area.pack(fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()
