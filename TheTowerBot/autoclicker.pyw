import pyautogui
import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import scrolledtext, font
import pygetwindow as gw
import ctypes
import sys
import json
import os

# --- 設定 ---
# 請將你要點擊的資源圖片放在與此腳本相同的資料夾中。
# 在下面的列表中新增或修改你的圖片檔名。
RESOURCE_IMAGE_PATHS = [
    'resource1.png',

]
# 圖像識別的信心度（0.0 到 1.0 之間，建議 0.8）
CONFIDENCE = 0.8
CONFIG_FILE = 'config.json'

# Windows API 常數，用於防止系統休眠
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

class AutoClickerGUI:
    def __init__(self, master):
        self.master = master
        master.title("自動點擊器 (視窗模式)")
        master.geometry("800x600")

        self.is_running = False
        self.loop_id = None

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=14)
        master.option_add("*Font", default_font)

        # 處理關閉視窗事件
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- GUI 元件 ---
        # 視窗標題設定
        self.window_title_label = tk.Label(master, text="目標視窗標題:")
        self.window_title_label.pack(pady=(10,0))
        self.window_title_entry = tk.Entry(master, width=40)
        self.window_title_entry.pack()

        # 延遲時間設定
        self.delay_label = tk.Label(master, text="搜尋間隔 (秒):")
        self.delay_label.pack(pady=(10,0))
        self.delay_entry = tk.Entry(master, width=20)
        self.delay_entry.pack()

        # 控制按鈕
        self.control_frame = tk.Frame(master)
        self.control_frame.pack(pady=15)
        self.start_button = tk.Button(self.control_frame, text="開始", command=self.start_clicking, width=12, height=2)
        self.start_button.pack(side=tk.LEFT, padx=10)
        self.stop_button = tk.Button(self.control_frame, text="停止", command=self.stop_clicking, state=tk.DISABLED, width=12, height=2)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # --- 進階選項 ---
        self.advanced_frame = tk.Frame(master)
        self.advanced_frame.pack(pady=10)

        self.prevent_sleep_var = tk.BooleanVar()
        self.prevent_sleep_check = tk.Checkbutton(self.advanced_frame, text="防止系統休眠", var=self.prevent_sleep_var)
        self.prevent_sleep_check.pack(side=tk.LEFT, padx=15)

        self.auto_stop_var = tk.BooleanVar()
        self.auto_stop_check = tk.Checkbutton(self.advanced_frame, text="啟用自動停止", var=self.auto_stop_var)
        self.auto_stop_check.pack(side=tk.LEFT, padx=5)

        self.max_fails_label = tk.Label(self.advanced_frame, text="連續失敗次數:")
        self.max_fails_label.pack(side=tk.LEFT)
        self.max_fails_entry = tk.Entry(self.advanced_frame, width=5)
        self.max_fails_entry.pack(side=tk.LEFT)

        # 狀態日誌
        self.log_label = tk.Label(master, text="狀態日誌:")
        self.log_label.pack(pady=(10,0))
        self.log_text = scrolledtext.ScrolledText(master, height=15, width=60)
        self.log_text.pack(expand=True, fill='both', padx=10, pady=10)

        self.failed_attempts = 0

        self.log("歡迎使用！")
        self.load_settings()
        self.log(f"已載入圖片: {', '.join(RESOURCE_IMAGE_PATHS)}")
        self.log("請確認視窗標題正確，然後按 '開始'。")

    def load_settings(self):
        """從 config.json 載入設定"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    settings = json.load(f)
                
                self.window_title_entry.insert(0, settings.get('window_title', 'MSI App Player'))
                self.delay_entry.insert(0, settings.get('delay', '300'))
                self.prevent_sleep_var.set(settings.get('prevent_sleep', True))
                self.auto_stop_var.set(settings.get('auto_stop', False))
                self.max_fails_entry.insert(0, settings.get('max_fails', '5'))
                self.log("已成功載入上次的設定。")
            else:
                self.log("未找到設定檔，將使用預設值。")
                self.window_title_entry.insert(0, "MSI App Player")
                self.delay_entry.insert(0, "300")
                self.prevent_sleep_var.set(True)
                self.auto_stop_var.set(False)
                self.max_fails_entry.insert(0, "5")
        except (json.JSONDecodeError, IOError) as e:
            self.log(f"讀取設定檔時發生錯誤: {e}")
            self.log("將使用預設值。")

    def save_settings(self):
        """將目前設定儲存到 config.json"""
        settings = {
            'window_title': self.window_title_entry.get(),
            'delay': self.delay_entry.get(),
            'prevent_sleep': self.prevent_sleep_var.get(),
            'auto_stop': self.auto_stop_var.get(),
            'max_fails': self.max_fails_entry.get()
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
            self.log("設定已儲存。")
        except IOError as e:
            self.log(f"儲存設定檔時發生錯誤: {e}")

    def on_closing(self):
        """當使用者關閉視窗時呼叫"""
        self.save_settings()
        if self.is_running:
            self.stop_clicking()
        self.master.destroy()

    def set_sleep_mode(self, prevent_sleep):
        """設定系統的休眠模式"""
        if 'win' not in sys.platform:
            self.log("防止休眠功能僅支援 Windows。")
            return

        if prevent_sleep:
            self.log("已啟用防止系統休眠功能。")
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
        else:
            self.log("已停用防止系統休眠功能，恢復正常。")
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

    def log(self, message):
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)

    def start_clicking(self):
        if self.is_running: return
        try:
            delay = float(self.delay_entry.get())
            if delay <= 0:
                self.log("錯誤：間隔時間必須大於 0。")
                return
        except ValueError:
            self.log("錯誤：請輸入有效的數字作為間隔時間。")
            return
        
        if self.auto_stop_var.get():
            try:
                max_fails = int(self.max_fails_entry.get())
                if max_fails <= 0:
                    self.log("錯誤：連續失敗次數必須大於 0。")
                    return
            except ValueError:
                self.log("錯誤：請輸入有效的數字作為連續失敗次數。")
                return

        if not self.window_title_entry.get():
            self.log("錯誤：視窗標題不能為空。")
            return

        self.is_running = True
        self.failed_attempts = 0
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        if self.prevent_sleep_var.get():
            self.set_sleep_mode(True)

        self.log("腳本已啟動...")
        self.automation_loop()

    def stop_clicking(self):
        if not self.is_running: return
        self.is_running = False
        if self.loop_id:
            self.master.after_cancel(self.loop_id)
            self.loop_id = None
        
        # 只有在腳本啟動時設定了防止休眠，才在停止時恢復它
        if self.prevent_sleep_var.get() and 'win' in sys.platform:
            self.set_sleep_mode(False)

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("腳本已停止。")

    def find_and_click_resources(self, screenshot_cv, offset_x, offset_y):
        found_something = False
        for image_path in RESOURCE_IMAGE_PATHS:
            try:
                template = cv2.imread(image_path, cv2.IMREAD_COLOR)
                if template is None:
                    self.log(f"警告：無法讀取圖片 '{image_path}'。")
                    continue

                result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val >= CONFIDENCE:
                    found_something = True
                    self.log(f"在視窗內找到 '{image_path}' (信心度: {max_val:.2f})")
                    
                    template_width, template_height = template.shape[1], template.shape[0]
                    
                    # 計算在視窗內的相對座標
                    click_x_relative = max_loc[0] + template_width // 2
                    click_y_relative = max_loc[1] + template_height // 2
                    
                    # 轉換為螢幕的絕對座標
                    click_x_absolute = offset_x + click_x_relative
                    click_y_absolute = offset_y + click_y_relative

                    pyautogui.moveTo(click_x_absolute, click_y_absolute, duration=0.2)
                    pyautogui.mouseDown()
                    time.sleep(0.05)
                    pyautogui.mouseUp()
                    self.log(f"在螢幕座標 ({click_x_absolute}, {click_y_absolute}) 點擊。")
                    time.sleep(0.3)
            
            except Exception as e:
                self.log(f"處理 '{image_path}' 時出錯: {e}")
        
        if not found_something:
            self.log("在視窗內未找到任何目標。")
            self.failed_attempts += 1
            self.log(f"連續失敗次數: {self.failed_attempts}")
        else:
            self.failed_attempts = 0 # 重置計數器

        return found_something

    def automation_loop(self):
        if not self.is_running: return

        self.log("開始新一輪搜尋...")
        # 模擬按下 Shift 鍵以喚醒螢幕，確保偵測準確
        pyautogui.press('shift')
        self.log("已模擬按下 Shift 鍵以喚醒螢幕。")
        time.sleep(1)

        try:
            window_title = self.window_title_entry.get()
            target_windows = gw.getWindowsWithTitle(window_title)

            if not target_windows:
                self.log(f"錯誤：找不到標題為 '{window_title}' 的視窗。")
                self.failed_attempts += 1
                self.log(f"連續失敗次數: {self.failed_attempts}")
            else:
                window = target_windows[0]
                if not window.isActive:
                    try:
                        window.activate()
                        self.log("Target window activated.")
                        time.sleep(0.2)
                    except Exception as e:
                        self.log(f"啟用視窗時出錯: {e}")

                x, y, width, height = window.left, window.top, window.width, window.height
                
                if width <= 0 or height <= 0:
                    self.log("警告：目標視窗被最小化或大小為零，跳過此輪。")
                    self.failed_attempts += 1
                    self.log(f"連續失敗次數: {self.failed_attempts}")
                else:
                    self.log(f"正在掃描視窗: '{window.title}' 區域: ({x}, {y}, {width}, {height})")
                    screenshot = pyautogui.screenshot(region=(x, y, width, height))
                    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    self.find_and_click_resources(screenshot_cv, x, y)

        except Exception as e:
            self.log(f"發生未預期的錯誤: {e}")
            self.failed_attempts += 1
            self.log(f"連續失敗次數: {self.failed_attempts}")

        if self.auto_stop_var.get():
            max_fails = int(self.max_fails_entry.get())
            if self.failed_attempts >= max_fails:
                self.log(f"已達到 {max_fails} 次連續失敗，自動停止腳本。")
                self.stop_clicking()
                return

        delay_ms = int(float(self.delay_entry.get()) * 1000)
        self.loop_id = self.master.after(delay_ms, self.automation_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerGUI(root)
    root.mainloop()