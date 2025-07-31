import tkinter as tk
from tkinter import ttk
from tkinter import font

import re
from dataclasses import dataclass
from typing import List, Dict
import codecs

start_src_o = 'C:\\Users\\prayd\\Desktop\\SS2 UA Project\\refactor\\o_sub\\vbriefs.sub'
start_src_m = 'C:\\Users\\prayd\\Desktop\\SS2 UA Project\\refactor\\m_sub\\vbriefs.sub'

original_text = None
tcons = []

class TranslateConnection:
    def __init__(self, title: str, reference: str, content: str):
        self.title = title
        self.reference = reference
        self.content = content

@dataclass
class SubtitleEntry:
    id: int
    start_time: int  # milliseconds
    length: int      # milliseconds
    text: str

@dataclass
class Multisub:
    name: str
    subtitles: List[SubtitleEntry]

def extract_multisubs(content: str) -> Dict[str, str]:
    result = {}
    pattern = re.compile(r'multisub\s+([\w/]+)\s*\{', re.DOTALL)
    
    for match in pattern.finditer(content):
        name = match.group(1)
        start_index = match.end()
        brace_level = 1
        end_index = start_index

        while end_index < len(content) and brace_level > 0:
            if content[end_index] == '{':
                brace_level += 1
            elif content[end_index] == '}':
                brace_level -= 1
            end_index += 1

        block_text = content[start_index:end_index - 1].strip()
        result[name] = block_text

    return result

def parse_sub1(content: str) -> Dict[str, Multisub]:
    raw_multisubs = extract_multisubs(content)
    parsed_result = {}

    for name, block in raw_multisubs.items():
        subtitles = []

        # Прибираємо коментарі // перед обробкою
        block_normalized = re.sub(r'^\s*//\s*', '', block, flags=re.MULTILINE)

        # Шукаємо всі субтитри
        matches = re.findall(
            r'\{\s*time\s+(\d+)\s+length\s+(\d+)\s+text\s+"((?:\\.|[^"\\])*)"\s*\}',
            block_normalized
        )

        for idx, (time_ms, length_ms, text) in enumerate(matches):
            entry = SubtitleEntry(
                id=idx,
                start_time=int(time_ms),
                length=int(length_ms),
                text=text
            )
            subtitles.append(entry)

        parsed_result[name] = Multisub(name=name, subtitles=subtitles)

    return parsed_result

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
        src_orig = file_o.read()
    with open(src_mod_entry.get(), "r", encoding="utf-8") as file_m:
        src_mod = file_m.read()

    tcons.clear()

    parsed = parse_sub1(src_orig)
    parsed2 = parse_sub1(src_mod)

    # for section, multisub in parsed.items():
    #     print(f"\n--- Секція: {section} ---")
    #     for sub in multisub.subtitles:
    #         print(f"{sub.id} . [{sub.start_time} - {sub.start_time + sub.length} ms] {sub.text}")
    # print("-------------------------------------------")
    # for section, multisub in parsed2.items():
    #     print(f"\n--- Секція: {section} ---")
    #     for sub in multisub.subtitles:
    #         print(f"{sub.id+1} . [{sub.start_time} - {sub.start_time + sub.length} ms] {sub.text}")

    #Цикл Читаємо орігу
    #для кожної строчки шукаємо в моді співпадіння
    #при співпадінні створюємо зв'язок

    for key in parsed.keys():
        if key not in parsed2:
            print(f"Відсутній мультисаб '{key}' в модифікованому файлі!")
            continue

        subs1 = parsed[key].subtitles
        subs2 = parsed2[key].subtitles

        min_len = min(len(subs1), len(subs2))

        for i in range(min_len):
            s1 = subs1[i]
            s2 = subs2[i]

            # if s1.id == s2.id and s1.start_time == s2.start_time and s1.length == s2.length:
            #     tcons.append(TranslateConnection(s1.text[1:len(s1.text)], s1.text, s2.text))
            if s1.id == s2.id:
                tcons.append(TranslateConnection(s1.text[1:len(s1.text)], s1.text, s2.text))

    # for t in tcons:
    #     print("\n\nTitle: " + t.title + "\nReference: " + t.reference + "\nContent: " + t.content, end='')

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
    root.title("SS2AR_Sub_Translate_Editor")
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
