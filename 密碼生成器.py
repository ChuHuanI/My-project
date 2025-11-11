import random
import string
import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkFont

# --- LOGIC (remains the same) ---
def generate_password(length, use_uppercase, use_lowercase, use_numbers, use_special):
    char_set = ''
    password = []
    if use_uppercase:
        char_set += string.ascii_uppercase
        password.append(random.choice(string.ascii_uppercase))
    if use_lowercase:
        char_set += string.ascii_lowercase
        password.append(random.choice(string.ascii_lowercase))
    if use_numbers:
        char_set += string.digits
        password.append(random.choice(string.digits))
    if use_special:
        # Modified: Restrict special characters to !@#$%
        char_set += "!@#$%"
        password.append(random.choice("!@#$%"))
    if not char_set:
        return None
    remaining_length = length - len(password)
    if remaining_length < 0:
        random.shuffle(password)
        return "".join(password[:length])
    for _ in range(remaining_length):
        password.append(random.choice(char_set))
    random.shuffle(password)
    return "".join(password)

# --- GUI HANDLERS (remains the same) ---
def on_generate_password():
    try:
        length = int(length_entry.get())
        if length <= 0:
            messagebox.showerror("錯誤", "密碼長度必須是正數。")
            return
    except ValueError:
        messagebox.showerror("錯誤", "請輸入有效的數字作為長度。")
        return
    use_uppercase = uppercase_var.get()
    use_lowercase = lowercase_var.get()
    use_numbers = numbers_var.get()
    use_special = special_var.get()
    if not (use_uppercase or use_lowercase or use_numbers or use_special):
        messagebox.showerror("錯誤", "您必須至少選擇一種類型的字符。")
        return
    password = generate_password(length, use_uppercase, use_lowercase, use_numbers, use_special)
    if password:
        password_output.config(state=tk.NORMAL)
        password_output.delete(0, tk.END)
        password_output.insert(0, password)
        password_output.config(state='readonly')

def copy_to_clipboard():
    if not password_output.get():
        messagebox.showwarning("警告", "沒有可複製的密碼。")
        return
    root.clipboard_clear()
    root.clipboard_append(password_output.get())
    messagebox.showinfo("成功", "密碼已複製到剪貼簿！")

# --- UI SETUP (Updated Fonts) ---

# Colors & Fonts

BG_COLOR = "#2E2E2E"

FRAME_COLOR = "#3C3C3C"

TEXT_COLOR = "#EAEAEA"

# Updated BUTTON_COLOR

BUTTON_COLOR = "#FF8C00" # DarkOrange

BUTTON_TEXT_COLOR = "#FFFFFF"

OUTPUT_BG = "#252525"



# --- Window ---

root = tk.Tk()

root.title("密碼生成器")

root.geometry("660x578")

root.resizable(False, False)

root.config(bg=BG_COLOR)



# Define custom fonts (MOVED HERE)

# Chinese font for labels, buttons, etc.

CHINESE_FONT_NORMAL = tkFont.Font(family="標楷體", size=18)

CHINESE_FONT_BOLD = tkFont.Font(family="標楷體", size=21, weight="bold") # Increased size

# English font for password output and entry fields

ENGLISH_FONT_NORMAL = tkFont.Font(family="Times New Roman", size=18)

ENGLISH_FONT_OUTPUT = tkFont.Font(family="Times New Roman", size=20) # Not monospaced, but requested



# --- Main Frame ---

main_frame = tk.Frame(root, bg=BG_COLOR, padx=33, pady=33)

main_frame.pack(fill=tk.BOTH, expand=True)



# --- Options Frame ---

options_frame = tk.LabelFrame(main_frame, text="選項", bg=FRAME_COLOR, fg=TEXT_COLOR, font=CHINESE_FONT_BOLD, padx=26, pady=17, relief=tk.FLAT)

options_frame.pack(fill="x")



# Length

length_frame = tk.Frame(options_frame, bg=FRAME_COLOR)

length_frame.pack(fill="x", pady=8)

tk.Label(length_frame, text="密碼長度:", bg=FRAME_COLOR, fg=TEXT_COLOR, font=CHINESE_FONT_NORMAL).pack(side=tk.LEFT, padx=(0, 15))

length_entry = tk.Entry(length_frame, width=12, font=ENGLISH_FONT_NORMAL, bg=OUTPUT_BG, fg=TEXT_COLOR, relief=tk.FLAT, insertbackground=TEXT_COLOR)

length_entry.pack(side=tk.LEFT)

length_entry.insert(0, "8")



# Checkboxes

checkbox_frame = tk.Frame(options_frame, bg=FRAME_COLOR)

checkbox_frame.pack(fill="x", pady=8)



uppercase_var = tk.BooleanVar(value=True)

cb_uppercase = tk.Checkbutton(checkbox_frame, text="大寫字母 (A-Z)", variable=uppercase_var, bg=FRAME_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR, activebackground=FRAME_COLOR, activeforeground=TEXT_COLOR, font=CHINESE_FONT_NORMAL, relief=tk.FLAT)

cb_uppercase.pack(anchor="w")



lowercase_var = tk.BooleanVar(value=True)

cb_lowercase = tk.Checkbutton(checkbox_frame, text="小寫字母 (a-z)", variable=lowercase_var, bg=FRAME_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR, activebackground=FRAME_COLOR, activeforeground=TEXT_COLOR, font=CHINESE_FONT_NORMAL, relief=tk.FLAT)

cb_lowercase.pack(anchor="w")



numbers_var = tk.BooleanVar(value=True)

cb_numbers = tk.Checkbutton(checkbox_frame, text="數字 (0-9)", variable=numbers_var, bg=FRAME_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR, activebackground=FRAME_COLOR, activeforeground=TEXT_COLOR, font=CHINESE_FONT_NORMAL, relief=tk.FLAT)

cb_numbers.pack(anchor="w")



special_var = tk.BooleanVar(value=True)

cb_special = tk.Checkbutton(checkbox_frame, text="特殊符號 (!@#$%)", variable=special_var, bg=FRAME_COLOR, fg=TEXT_COLOR, selectcolor=BG_COLOR, activebackground=FRAME_COLOR, activeforeground=TEXT_COLOR, font=CHINESE_FONT_NORMAL, relief=tk.FLAT)

cb_special.pack(anchor="w")



# --- Generate Button ---

generate_button = tk.Button(main_frame, text="生成密碼", command=on_generate_password, font=CHINESE_FONT_BOLD, bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, relief=tk.RAISED, bd=2, activebackground="#CC7000", activeforeground=BUTTON_TEXT_COLOR, padx=30, pady=15) # Beautified

generate_button.pack(pady=(33, 17))



# --- Output Frame ---

output_frame = tk.Frame(main_frame, bg=BG_COLOR)

output_frame.pack(fill="x")



password_output = tk.Entry(output_frame, font=ENGLISH_FONT_OUTPUT, state='readonly', relief=tk.FLAT, justify=tk.CENTER, readonlybackground=OUTPUT_BG, fg=TEXT_COLOR)

password_output.pack(side=tk.LEFT, fill="x", expand=True, ipady=14)



copy_button = tk.Button(output_frame, text="複製", command=copy_to_clipboard, font=CHINESE_FONT_NORMAL, bg="#555555", fg=TEXT_COLOR, relief=tk.FLAT, activebackground="#666666", activeforeground=TEXT_COLOR)

copy_button.pack(side=tk.RIGHT, padx=(8, 0))



# --- Main Loop ---

root.mainloop()
