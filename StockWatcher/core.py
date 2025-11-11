import sys
import json
import requests
import yfinance as yf
# from plyer import notification # 我們之後會啟用這個

# --- 常數設定 ---
STOCKS_FILE = 'stocks.json'

# --- 資料處理函式 ---
def load_stocks():
    """從 stocks.json 載入股票清單"""
    try:
        with open(STOCKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果檔案不存在或格式錯誤，回傳空清單
        return []

def save_stocks(stocks):
    """將股票清單存回 stocks.json"""
    with open(STOCKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stocks, f, ensure_ascii=False, indent=4)

# --- 核心功能函式 ---
def get_stock_price(stock_symbol):
    """
    使用 yfinance API 抓取指定股號的最新股價
    - stock_symbol: 股票代號，例如 '2330.TW'
    """
    try:
        cleaned_symbol = stock_symbol.strip().strip('/')
        print(f"正在查詢 {cleaned_symbol} 的股價...")
        ticker = yf.Ticker(cleaned_symbol)
        
        # yfinance 提供多種獲取價格的方式，我們嘗試幾種以增加成功率
        
        # 方法一：獲取最近一天的歷史資料，取收盤價
        hist = ticker.history(period="1d")
        if not hist.empty:
            latest_price = hist['Close'].iloc[-1]
            return round(latest_price, 2)
            
        # 方法二：如果 history 為空，嘗試從 info 字典中獲取 'regularMarketPrice'
        info = ticker.info
        if 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
            return round(info['regularMarketPrice'], 2)

        # 方法三：作為最終備案，嘗試 'preMarket' 或 'postMarket' 價格
        if 'preMarket' in info and info['preMarket'] is not None:
             return round(info['preMarket'], 2)

        print(f"警告：無法為 {cleaned_symbol} 找到任何有效的價格資料。")
        return None

    except Exception as e:
        print(f"錯誤：使用 yfinance 抓取 {cleaned_symbol} 股價時發生錯誤: {e}")
        return None

def check_prices():
    """檢查所有追蹤股票的價格並在達標時發出通知"""
    print("開始檢查股價...")
    stocks = load_stocks()
    if not stocks:
        print("您的追蹤清單是空的，請先使用 'add' 指令新增股票。")
        return

    for stock in stocks:
        price = get_stock_price(stock['symbol'])
        
        if price is not None:
            target_price = stock['target_price']
            print(f"  -> {stock['symbol']} 目前價格: {price}, 目標價: {target_price}")
            if price >= target_price:
                print("\n" + "="*40)
                print(f"🎉 **達標通知** 🎉")
                print(f"  股票 {stock['symbol']} 已達到目標價!")
                print(f"  目前價格: {price} >= 目標價: {target_price}")
                print("="*40 + "\n")
                # 在未來，我們可以在這裡觸發桌面通知
                # notification.notify(...)
    
    print("檢查完畢。")

# --- 使用者介面函式 ---
def add_stock():
    """引導使用者新增一支持股到追蹤清單"""
    symbol = input("請輸入股票代號 (例如台積電請輸入 2330.TW): ")
    target_price_str = input(f"請為 {symbol} 設定目標價: ")
    
    try:
        target_price = float(target_price_str)
    except ValueError:
        print("錯誤：目標價必須是數字。")
        return

    stocks = load_stocks()
    # 檢查是否已存在
    if any(s['symbol'] == symbol for s in stocks):
        print(f"錯誤：{symbol} 已經在您的追蹤清單中了。")
        return
        
    new_stock = {'symbol': symbol, 'name': '', 'target_price': target_price} # name 暫時留空
    stocks.append(new_stock)
    save_stocks(stocks)
    print(f"成功新增 {symbol} 到追蹤清單，目標價為 {target_price}。")

def list_stocks():
    """列出所有在追蹤清單中的持股"""
    stocks = load_stocks()
    if not stocks:
        print("您的追蹤清單是空的。")
        return
    
    print("\n--- 您目前的追蹤清單 ---")
    for stock in stocks:
        print(f"  - 股票代號: {stock['symbol']}, 目標價: {stock['target_price']}")
    print("--------------------------\n")

def print_usage():
    """印出使用說明"""
    print("\n--- 股票價格監控小助理 ---")
    print("使用方法:")
    print("  python main.py add      - 新增一支持股到追蹤清單")
    print("  python main.py list     - 顯示目前追蹤的所有持股")
    print("  python main.py run      - 執行一次價格檢查")
    print("--------------------------\n")

# --- 主程式進入點 ---
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
    else:
        command = sys.argv[1].lower()
        if command == 'add':
            add_stock()
        elif command == 'list':
            list_stocks()
        elif command == 'run':
            check_prices()
        else:
            print(f"錯誤：未知的指令 '{command}'")
            print_usage()
