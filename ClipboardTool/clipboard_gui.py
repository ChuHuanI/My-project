
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import queue
import pyperclip
import time
import json
import os

class ClipboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("剪貼簿增強工具")
        self.root.geometry("800x600")

        # --- File Paths ---
        self.history_file = "clipboard_history.json"
        self.snippets_file = "snippets.json"
        self.snippets = []

        # --- Styling ---
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("TkDefaultFont", 14))
        style.configure("TButton", font=("TkDefaultFont", 14))
        style.configure("TLabel", font=("TkDefaultFont", 14))
        style.configure("TEntry", font=("TkDefaultFont", 14))
        style.configure("Treeview.Heading", font=("TkDefaultFont", 14, "bold"))
        style.configure("Treeview", font=("TkDefaultFont", 14))

        # --- Main UI Structure (Notebook for Tabs) ---
        # The Help button will be placed on top of this frame
        main_frame = ttk.Frame(root)
        main_frame.pack(expand=True, fill='both')

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Place Help button in the top-right corner of the main_frame
        help_button = ttk.Button(main_frame, text="說明", command=self.show_help)
        help_button.place(relx=1.0, x=-10, y=10, anchor='ne')

        self.history_frame = ttk.Frame(self.notebook)
        self.snippets_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.history_frame, text='剪貼簿歷史')
        self.notebook.add(self.snippets_frame, text='快捷片段 (Snippets)')

        # --- Setup each tab ---
        self.setup_history_tab()
        self.setup_snippets_tab()

        # --- Status Bar ---
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("TkDefaultFont", 12))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Load Data ---
        self.load_history()
        self.load_snippets()

        # --- Bind Events & Start Threads ---
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.start_clipboard_monitor()

    def setup_history_tab(self):
        # --- GUI Widgets for History ---
        button_frame = ttk.Frame(self.history_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        ttk.Button(button_frame, text="清除選取項目", command=self.clear_selected_history_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清除全部歷史", command=self.clear_history).pack(side=tk.LEFT, padx=5)

        list_frame = ttk.Frame(self.history_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.history_listbox = tk.Listbox(list_frame, height=20, width=80, font=("TkDefaultFont", 14))
        self.scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        self.history_listbox.config(yscrollcommand=self.scrollbar.set)
        
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox.bind("<Double-1>", self.copy_history_selection)

    def setup_snippets_tab(self):
        # --- GUI Widgets for Snippets ---
        button_frame = ttk.Frame(self.snippets_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        ttk.Button(button_frame, text="新增片段", command=self.add_snippet_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="編輯片段", command=self.edit_snippet_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刪除片段", command=self.delete_snippet).pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(self.snippets_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.snippets_tree = ttk.Treeview(tree_frame, columns=("keyword", "content"), show="headings")
        self.snippets_tree.heading("keyword", text="關鍵字")
        self.snippets_tree.heading("content", text="內容")
        self.snippets_tree.column("keyword", width=150)
        self.snippets_tree.column("content", width=500)
        
        snippet_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.snippets_tree.yview)
        self.snippets_tree.config(yscrollcommand=snippet_scrollbar.set)

        self.snippets_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        snippet_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.snippets_tree.bind("<Double-1>", self.copy_snippet_selection)

    # --- Generic Methods ---
    def on_closing(self):
        self.save_history()
        self.save_snippets()
        self.root.destroy()

    def clear_status(self):
        self.status_var.set("")

    def show_help(self):
        help_win = tk.Toplevel(self.root)
        help_win.title("使用說明")
        help_win.geometry("700x500")
        help_win.resizable(False, False)

        help_text = tk.Text(help_win, wrap=tk.WORD, font=("TkDefaultFont", 14), padx=10, pady=10, bg=help_win.cget('bg'), relief=tk.FLAT)
        help_text.pack(expand=True, fill=tk.BOTH)

        help_text.tag_configure("h1", font=("TkDefaultFont", 18, "bold"), spacing3=10)
        help_text.tag_configure("h2", font=("TkDefaultFont", 14, "bold"), spacing1=10, spacing3=5)
        help_text.tag_configure("p", font=("TkDefaultFont", 14), lmargin1=20, lmargin2=20)

        help_text.insert(tk.END, "剪貼簿增強工具\n", "h1")
        
        help_text.insert(tk.END, "剪貼簿歷史\n", "h2")
        help_text.insert(tk.END, "• 自動記錄：您在電腦上複製的任何文字都會自動出現在此列表中。\n", "p")
        help_text.insert(tk.END, "• 重新複製：雙擊列表中的任一項目，即可將其內容再次複製到剪貼簿。\n", "p")
        help_text.insert(tk.END, "• 管理記錄：使用按鈕可以刪除選取的項目，或清除所有歷史記錄。\n\n", "p")

        help_text.insert(tk.END, "快捷片段 (Snippets)\n", "h2")
        help_text.insert(tk.END, "• 功能：此處用於管理您常用的文字片段，如Email、地址、程式碼塊等。\n", "p")
        help_text.insert(tk.END, "• 新增/編輯/刪除：使用上方的按鈕來管理您的快捷片段。\n", "p")
        help_text.insert(tk.END, "• 使用片段：雙擊列表中的任一項目，即可將其內容複製到剪貼簿，方便隨處貼上。\n\n", "p")

        help_text.insert(tk.END, "通用\n", "h2")
        help_text.insert(tk.END, "• 自動儲存：所有歷史記錄和快捷片段都會在關閉程式時自動儲存。\n", "p")

        help_text.config(state=tk.DISABLED)

        ttk.Button(help_win, text="關閉", command=help_win.destroy).pack(pady=10)

        help_win.transient(self.root)
        help_win.grab_set()
        self.root.wait_window(help_win)

    # --- History Methods ---
    def load_history(self):
        if not os.path.exists(self.history_file): return
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                for item in json.load(f):
                    self.history_listbox.insert(tk.END, item)
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_listbox.get(0, tk.END), f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving history: {e}")

    def start_clipboard_monitor(self):
        self.queue = queue.Queue()
        try:
            self.last_item = pyperclip.paste()
        except Exception:
            self.last_item = ""
        
        self.monitor_thread = threading.Thread(target=self.clipboard_monitor, daemon=True)
        self.monitor_thread.start()
        self.process_queue()

    def clipboard_monitor(self):
        while True:
            try:
                new_item = pyperclip.paste()
                if new_item and isinstance(new_item, str) and new_item != self.last_item:
                    self.last_item = new_item
                    self.queue.put(new_item)
            except Exception:
                pass # Ignore pyperclip errors on certain content
            time.sleep(0.5)

    def process_queue(self):
        try:
            while not self.queue.empty():
                item = self.queue.get_nowait()
                all_items = self.history_listbox.get(0, tk.END)
                if item in all_items:
                    self.history_listbox.delete(all_items.index(item))
                self.history_listbox.insert(0, item)
        finally:
            self.root.after(100, self.process_queue)

    def copy_history_selection(self, event):
        selected_indices = self.history_listbox.curselection()
        if not selected_indices: return
        selected_item = self.history_listbox.get(selected_indices[0])
        pyperclip.copy(selected_item)
        self.status_var.set(f"已複製歷史: {selected_item[:60]}...")
        self.root.after(3000, self.clear_status)

    def clear_history(self):
        if messagebox.askyesno("確認", "您確定要清除所有歷史記錄嗎？"):
            self.history_listbox.delete(0, tk.END)
            self.save_history()
            self.status_var.set("歷史記錄已清除。")
            self.root.after(3000, self.clear_status)

    def clear_selected_history_item(self):
        selected_indices = self.history_listbox.curselection()
        if not selected_indices: return
        self.history_listbox.delete(selected_indices[0])
        self.save_history()
        self.status_var.set("已清除選取項目。")
        self.root.after(3000, self.clear_status)

    # --- Snippet Methods ---
    def load_snippets(self):
        if not os.path.exists(self.snippets_file):
            self.snippets = []
            return
        try:
            with open(self.snippets_file, 'r', encoding='utf-8') as f:
                self.snippets = json.load(f)
            self.populate_snippets_treeview()
        except (json.JSONDecodeError, FileNotFoundError):
            self.snippets = []

    def save_snippets(self):
        try:
            with open(self.snippets_file, 'w', encoding='utf-8') as f:
                json.dump(self.snippets, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving snippets: {e}")

    def populate_snippets_treeview(self):
        for item in self.snippets_tree.get_children():
            self.snippets_tree.delete(item)
        for i, snippet in enumerate(self.snippets):
            self.snippets_tree.insert("", tk.END, iid=i, values=(snippet['keyword'], snippet['content']))

    def add_snippet_dialog(self):
        SnippetDialog(self.root, "新增快捷片段", callback=self.add_snippet_callback)

    def add_snippet_callback(self, snippet):
        if snippet:
            self.snippets.append(snippet)
            self.save_snippets()
            self.populate_snippets_treeview()
            self.status_var.set(f"已新增片段: {snippet['keyword']}")
            self.root.after(3000, self.clear_status)

    def edit_snippet_dialog(self):
        selected_item = self.snippets_tree.focus()
        if not selected_item:
            messagebox.showwarning("注意", "請先選擇一個要編輯的片段。")
            return
        snippet_index = int(selected_item)
        snippet_to_edit = self.snippets[snippet_index]
        SnippetDialog(self.root, "編輯快捷片段", snippet=snippet_to_edit, callback=lambda updated_snippet: self.edit_snippet_callback(snippet_index, updated_snippet))

    def edit_snippet_callback(self, index, snippet):
        if snippet:
            self.snippets[index] = snippet
            self.save_snippets()
            self.populate_snippets_treeview()
            self.status_var.set(f"已更新片段: {snippet['keyword']}")
            self.root.after(3000, self.clear_status)

    def delete_snippet(self):
        selected_item = self.snippets_tree.focus()
        if not selected_item:
            messagebox.showwarning("注意", "請先選擇一個要刪除的片段。")
            return
        if messagebox.askyesno("確認刪除", "您確定要刪除所選的片段嗎？"):
            snippet_index = int(selected_item)
            del self.snippets[snippet_index]
            self.save_snippets()
            self.populate_snippets_treeview()
            self.status_var.set("片段已刪除。")
            self.root.after(3000, self.clear_status)

    def copy_snippet_selection(self, event):
        selected_item = self.snippets_tree.focus()
        if not selected_item: return
        snippet_index = int(selected_item)
        selected_snippet = self.snippets[snippet_index]
        pyperclip.copy(selected_snippet['content'])
        self.status_var.set(f"已複製片段: {selected_snippet['keyword']}")
        self.root.after(3000, self.clear_status)

class SnippetDialog(tk.Toplevel):
    def __init__(self, parent, title, callback, snippet=None):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.callback = callback
        self.snippet = snippet if snippet else {}

        body = ttk.Frame(self, padding="10")
        body.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        ttk.Label(body, text="關鍵字:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.keyword_entry = ttk.Entry(body, width=50)
        self.keyword_entry.grid(row=1, column=0, sticky=tk.EW, pady=(0, 5))

        ttk.Label(body, text="內容:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.content_text = tk.Text(body, width=50, height=10)
        self.content_text.grid(row=3, column=0, sticky=tk.EW)
        
        body.grid_columnconfigure(0, weight=1)

        if self.snippet:
            self.keyword_entry.insert(0, self.snippet.get('keyword', ''))
            self.content_text.insert("1.0", self.snippet.get('content', ''))

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="確定", command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.RIGHT)

        self.grab_set()
        self.wait_window(self)

    def on_ok(self):
        keyword = self.keyword_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()

        if not keyword or not content:
            messagebox.showwarning("輸入不完整", "關鍵字和內容都必須填寫。", parent=self)
            return

        self.callback({"keyword": keyword, "content": content})
        self.destroy()

if __name__ == "__main__":
    app_root = tk.Tk()
    app_root.option_add('*Font', 'TkDefaultFont 12')
    app = ClipboardApp(app_root)
    app_root.mainloop()
