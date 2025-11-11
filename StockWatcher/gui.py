import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font
import json
import threading
from collections import defaultdict
import yfinance as yf

# 從 core.py 匯入我們的核心邏輯函式
import core

# --- 全域變數和輔助函式 ---
TW_STOCK_LIST = []

def load_tw_stock_list(logger):
    """載入台股字典檔案"""
    global TW_STOCK_LIST
    try:
        with open('tw_stock_list.json', 'r', encoding='utf-8') as f:
            TW_STOCK_LIST = json.load(f)
        logger(f"成功載入 {len(TW_STOCK_LIST)} 筆台股字典資料。" )
    except FileNotFoundError:
        logger("錯誤：找不到 'tw_stock_list.json'。請先執行 'update_stock_list.py'。" )
    except Exception as e:
        logger(f"載入台股字典時發生錯誤: {e}")

class StockWatcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("股票價格監控小助理")
        self.root.geometry("1210x600")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', font=('Microsoft JhengHei UI', 11))
        style.configure('Treeview.Heading', font=('Microsoft JhengHei UI', 11, 'bold'))

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.LabelFrame(main_frame, text="監控清單")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.tree = self.create_treeview(left_frame)
        
        sort_button_frame = ttk.Frame(left_frame)
        sort_button_frame.pack(fill=tk.X, pady=(5,0))
        ttk.Button(sort_button_frame, text="上移", command=self.move_stock_up).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(sort_button_frame, text="下移", command=self.move_stock_down).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X)
        self.create_buttons(button_frame)

        log_frame = ttk.LabelFrame(right_frame, text="日誌")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.log_text = self.create_log_text(log_frame)
        self.log_text.tag_configure("target_met", foreground="blue", font=('Microsoft JhengHei UI', 13, "bold"))

        self.log("歡迎使用！正在載入台股字典...")
        load_tw_stock_list(self.log)
        self.refresh_stock_list()
        self.run_price_check_threaded()

    def create_treeview(self, parent):
        columns = ("symbol", "name", "condition", "target_price")
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        tree.heading("symbol", text="股票代號")
        tree.heading("name", text="公司名稱")
        tree.heading("condition", text="條件")
        tree.heading("target_price", text="目標價")
        tree.column("symbol", width=100, anchor=tk.W)
        tree.column("name", width=180, anchor=tk.W)
        tree.column("condition", width=50, anchor=tk.CENTER)
        tree.column("target_price", width=80, anchor=tk.E)
        tree.pack(fill=tk.BOTH, expand=True)
        return tree

    def create_buttons(self, parent):
        parent.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        ttk.Button(parent, text="刷新列表", command=self.refresh_stock_list).grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(parent, text="新增股票", command=self.add_stock_window).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(parent, text="編輯股票/分類", command=self.edit_stock).grid(row=0, column=2, sticky="ew", padx=2)
        ttk.Button(parent, text="刪除選取", command=self.remove_selected_stock).grid(row=0, column=3, sticky="ew", padx=2)
        ttk.Button(parent, text="執行檢查", command=self.run_price_check_threaded).grid(row=0, column=4, sticky="ew", padx=2)
        ttk.Button(parent, text="清除日誌", command=self.clear_log).grid(row=0, column=5, sticky="ew", padx=2)

    def create_log_text(self, parent):
        log_font = ('Microsoft JhengHei UI', 13) # 字體放大
        log_text = tk.Text(parent, wrap=tk.WORD, state="disabled", height=10, font=log_font)
        log_text.pack(fill=tk.BOTH, expand=True)
        return log_text

    def log(self, message, tag=None):
        self.root.after(0, self._log_thread_safe, message, tag)

    def _log_thread_safe(self, message, tag=None):
        self.log_text.config(state="normal")
        if tag:
            self.log_text.insert(tk.END, message + "\n", tag)
        else:
            self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
    
    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

    def refresh_stock_list(self):
        self.log("正在刷新股票清單...")
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        stocks = core.load_stocks()
        
        grouped_stocks = defaultdict(list)
        for stock in stocks:
            category = stock.get('category', '未分類')
            grouped_stocks[category].append(stock)

        for category, stock_list in sorted(grouped_stocks.items()):
            category_id = self.tree.insert("", tk.END, text=category, open=True, values=(category, "", "", ""))
            for stock in stock_list:
                condition = stock.get('condition', '>=' )
                self.tree.insert(category_id, tk.END, values=(stock['symbol'], stock.get('name', 'N/A'), condition, stock['target_price']))
        
        self.log("刷新完畢。" )

    def add_stock_window(self):
        dialog = AddStockDialog(self.root, "新增股票")
        if dialog.result:
            query, target_price_str, condition, category = dialog.result
            try:
                target_price = float(target_price_str)
                self.find_and_add_stock(query, target_price, condition, category)
            except ValueError:
                messagebox.showerror("錯誤", "目標價必須是有效的數字。" )
            except Exception as e:
                messagebox.showerror("錯誤", f"新增股票時發生錯誤: {e}")

    def find_and_add_stock(self, query, target_price, condition, category):
        found_stock = None
        query = query.strip()

        if not query:
            messagebox.showwarning("提示", "請輸入股票代號或名稱。" )
            return

        if not category:
            category = "未分類"

        if '.' in query:
            for stock in TW_STOCK_LIST:
                if stock['symbol'].upper() == query.upper():
                    found_stock = stock
                    break
        else:
            for stock in TW_STOCK_LIST:
                if stock['name'] == query:
                    found_stock = stock
                    break
        
        if not found_stock:
            messagebox.showwarning("找不到", f"找不到符合 '{query}' 的股票代號或名稱。" )
            return

        try:
            self.log(f"正在驗證股票資訊: {found_stock['symbol']}...")
            ticker = yf.Ticker(found_stock['symbol'])
            info = ticker.info
            long_name = info.get('longName', found_stock['name'])
        except Exception as e:
            self.log(f"驗證 {found_stock['symbol']} 失敗: {e}。將使用本地資料。" )
            long_name = found_stock['name']

        stocks = core.load_stocks()
        if any(s['symbol'] == found_stock['symbol'] for s in stocks):
            messagebox.showwarning("已存在", f"{long_name} ({found_stock['symbol']}) 已經在您的監控清單中。" )
            return

        new_stock = {'symbol': found_stock['symbol'], 'name': long_name, 'target_price': target_price, 'condition': condition, 'category': category}
        stocks.append(new_stock)
        core.save_stocks(stocks)
        
        messagebox.showinfo("成功", f"已成功新增 {long_name} 到監控清單。" )
        self.refresh_stock_list()

    def edit_stock(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "請先在列表中選擇一支持股。")
            return
        if len(selected_items) > 1:
            messagebox.showwarning("提示", "請一次只選擇一支持股進行編輯。")
            return

        selected_item = selected_items[0]
        
        if not self.tree.parent(selected_item):
            messagebox.showwarning("提示", "不能編輯分類本身，請選擇一支持股。")
            return

        original_symbol = self.tree.item(selected_item, "values")[0]
        stocks = core.load_stocks()
        
        stock_to_edit = None
        for s in stocks:
            if s['symbol'] == original_symbol:
                stock_to_edit = s
                break
        
        if not stock_to_edit:
            messagebox.showerror("錯誤", "在資料庫中找不到所選的股票。")
            return

        dialog = EditStockDialog(self.root, "編輯股票/分類", initial_data=stock_to_edit)

        if dialog.result:
            new_query, new_target_price_str, new_condition, new_category = dialog.result
            
            try:
                new_target_price = float(new_target_price_str)
            except ValueError:
                messagebox.showerror("錯誤", "目標價必須是有效的數字。")
                return

            if not new_category.strip():
                new_category = "未分類"
            else:
                new_category = new_category.strip()

            # 檢查股票代號/名稱是否有變更
            if new_query.strip().upper() == original_symbol.upper() or new_query.strip() == stock_to_edit.get('name'):
                # 股票本身沒變，只更新其他資訊
                stock_to_edit['target_price'] = new_target_price
                stock_to_edit['condition'] = new_condition
                stock_to_edit['category'] = new_category
                core.save_stocks(stocks)
                self.log(f"已更新 {original_symbol} 的資訊。")
                self.refresh_stock_list()
            else:
                # 股票代號/名稱變了，需要重新查找和驗證
                self.log(f"正在查找新的股票資訊: {new_query}...")
                
                found_stock_info = None
                _query = new_query.strip()
                if '.' in _query:
                    for stock in TW_STOCK_LIST:
                        if stock['symbol'].upper() == _query.upper():
                            found_stock_info = stock
                            break
                else:
                    for stock in TW_STOCK_LIST:
                        if stock['name'] == _query:
                            found_stock_info = stock
                            break
                
                if not found_stock_info:
                    messagebox.showwarning("找不到", f"找不到符合 '{new_query}' 的股票代號或名稱。")
                    return

                new_symbol = found_stock_info['symbol']
                
                # 檢查新股號是否已存在於列表中 (排除自己)
                if any(s['symbol'] == new_symbol and s['symbol'] != original_symbol for s in stocks):
                    messagebox.showwarning("已存在", f"{found_stock_info['name']} ({new_symbol}) 已經在您的監控清單中。")
                    return
                
                # 更新股票資訊
                stock_to_edit['symbol'] = new_symbol
                stock_to_edit['name'] = found_stock_info['name']
                stock_to_edit['target_price'] = new_target_price
                stock_to_edit['condition'] = new_condition
                stock_to_edit['category'] = new_category
                
                core.save_stocks(stocks)
                self.log(f"已將 {original_symbol} 更改為 {new_symbol}。")
                self.refresh_stock_list()

    def remove_selected_stock(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "請先在列表中選擇項目。" )
            return

        if not messagebox.askyesno("確認", "您確定要刪除選取的項目嗎？\n(如果選取的是分類，將會刪除該分類下的所有股票)"):
            return

        stocks = core.load_stocks()
        symbols_to_delete = set()

        for item_id in selected_items:
            if not self.tree.parent(item_id):
                category_name = self.tree.item(item_id, "text")
                for stock in stocks:
                    if stock.get('category', '未分類') == category_name:
                        symbols_to_delete.add(stock['symbol'])
            else:
                symbols_to_delete.add(self.tree.item(item_id, "values")[0])
        
        new_stocks = [s for s in stocks if s['symbol'] not in symbols_to_delete]
        
        core.save_stocks(new_stocks)
        self.log(f"已刪除 {len(stocks) - len(new_stocks)} 筆資料。" )
        self.refresh_stock_list()

    def move_stock(self, direction):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "請先在列表中選擇一支持股。" )
            return
        if len(selected_items) > 1:
            messagebox.showwarning("提示", "請一次只選擇一支持股進行移動。" )
            return

        selected_item = selected_items[0]
        
        if not self.tree.parent(selected_item):
            messagebox.showwarning("提示", "只能對股票進行排序，不能移動分類。" )
            return

        current_symbol = self.tree.item(selected_item, "values")[0]
        stocks = core.load_stocks()
        
        current_index = -1
        for i, stock in enumerate(stocks):
            if stock['symbol'] == current_symbol:
                current_index = i
                break
        
        if current_index == -1:
            self.log("錯誤：在資料中找不到選取的股票。" )
            return

        new_index = current_index + direction

        if not (0 <= new_index < len(stocks)):
            return 

        stocks[current_index], stocks[new_index] = stocks[new_index], stocks[current_index]
        
        core.save_stocks(stocks)
        self.refresh_stock_list()
        
        for category_id in self.tree.get_children():
            for item_id in self.tree.get_children(category_id):
                if self.tree.item(item_id, "values")[0] == current_symbol:
                    self.tree.selection_set(item_id)
                    self.tree.focus(item_id)
                    self.tree.see(item_id)
                    return

    def move_stock_up(self):
        self.move_stock(-1)

    def move_stock_down(self):
        self.move_stock(1)

    def run_price_check_threaded(self):
        self.log("開始執行價格檢查 (背景執行)...")
        thread = threading.Thread(target=self.run_price_check)
        thread.daemon = True
        thread.start()

    def run_price_check(self):
        stocks = core.load_stocks()
        if not stocks:
            self.log("您的追蹤清單是空的。" )
            return

        for stock in stocks:
            price = core.get_stock_price(stock['symbol'])
            if price is not None:
                target_price = stock['target_price']
                condition = stock.get('condition', '>=' )
                self.log(f"  -> {stock['symbol']} 目前:{price}, 條件: {condition} {target_price}")
                
                is_target_met = False
                if condition == '>=' and price >= target_price:
                    is_target_met = True
                elif condition == '<=' and price <= target_price:
                    is_target_met = True
                
                if is_target_met:
                    notification_message = f"🎉 **達標通知** 🎉\n股票 {stock['symbol']} ({stock.get('name', '')})\n已達到目標! (目前: {price} {condition} 目標: {target_price})"
                    self.log("="*40)
                    self.log(notification_message, tag="target_met")
                    self.log("="*40)
        self.log("檢查完畢。" )

class EditStockDialog(simpledialog.Dialog):
    """編輯股票的對話視窗"""
    def __init__(self, parent, title, initial_data):
        self.initial_data = initial_data
        super().__init__(parent, title)

    def body(self, master):
        ttk.Label(master, text="股號 (可改) 或公司名稱:").grid(row=0, columnspan=2, sticky=tk.W)
        self.entry_query = ttk.Entry(master, width=40)
        self.entry_query.grid(row=1, columnspan=2, sticky=tk.W+tk.E, pady=5)
        self.entry_query.insert(0, self.initial_data.get('symbol', ''))

        ttk.Label(master, text="分類:").grid(row=2, columnspan=2, sticky=tk.W)
        self.entry_category = ttk.Entry(master, width=40)
        self.entry_category.grid(row=3, columnspan=2, sticky=tk.W+tk.E, pady=5)
        self.entry_category.insert(0, self.initial_data.get('category', '未分類'))

        ttk.Label(master, text="條件:").grid(row=4, column=0, sticky=tk.W)
        self.condition_var = tk.StringVar()
        current_condition_map = {
            '>=': '>= (目標賣價)',
            '<=': '<= (目標買價)'
        }
        self.condition_var.set(current_condition_map.get(self.initial_data.get('condition'), '>= (目標賣價)'))
        self.combo_condition = ttk.Combobox(master, textvariable=self.condition_var, values=['>= (目標賣價)', '<= (目標買價)'], state='readonly')
        self.combo_condition.grid(row=5, column=0, sticky=tk.W, padx=(0, 5))

        ttk.Label(master, text="目標價:").grid(row=4, column=1, sticky=tk.W)
        self.entry_price = ttk.Entry(master, width=15)
        self.entry_price.grid(row=5, column=1, sticky=tk.W)
        self.entry_price.insert(0, self.initial_data.get('target_price', ''))
        
        return self.entry_query

    def apply(self):
        query = self.entry_query.get()
        price = self.entry_price.get()
        condition = self.condition_var.get().split(' ')[0]
        category = self.entry_category.get()
        
        if query and price and condition:
            self.result = (query, price, condition, category)
        else:
            self.result = None


class AddStockDialog(simpledialog.Dialog):
    """新增股票的對話視窗"""
    def body(self, master):
        ttk.Label(master, text="輸入股號 (如 2330.TW) 或公司名稱 (如 台積電):" ).grid(row=0, columnspan=2, sticky=tk.W)
        self.entry_query = ttk.Entry(master, width=40)
        self.entry_query.grid(row=1, columnspan=2, sticky=tk.W+tk.E, pady=5)

        ttk.Label(master, text="分類 (可選):" ).grid(row=2, columnspan=2, sticky=tk.W)
        self.entry_category = ttk.Entry(master, width=40)
        self.entry_category.grid(row=3, columnspan=2, sticky=tk.W+tk.E, pady=5)

        ttk.Label(master, text="條件:" ).grid(row=4, column=0, sticky=tk.W)
        self.condition_var = tk.StringVar(value='>= (目標賣價)')
        self.combo_condition = ttk.Combobox(master, textvariable=self.condition_var, values=['>= (目標賣價)', '<= (目標買價)'], state='readonly')
        self.combo_condition.grid(row=5, column=0, sticky=tk.W, padx=(0, 5))

        ttk.Label(master, text="目標價:" ).grid(row=4, column=1, sticky=tk.W)
        self.entry_price = ttk.Entry(master, width=15)
        self.entry_price.grid(row=5, column=1, sticky=tk.W)
        
        return self.entry_query

    def apply(self):
        query = self.entry_query.get()
        price = self.entry_price.get()
        condition = self.condition_var.get().split(' ')[0]
        category = self.entry_category.get()
        
        if query and price and condition:
            self.result = (query, price, condition, category)
        else:
            self.result = None

if __name__ == '__main__':
    root = tk.Tk()
    app = StockWatcherApp(root)
    root.mainloop()