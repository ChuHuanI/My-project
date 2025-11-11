import requests
import json

# 台灣證券交易所 (TWSE) 的官方 API 端點
API_URL = "https://www.twse.com.tw/exchangeReport/STOCK_DAY_ALL?response=json"
# 輸出檔案名稱
OUTPUT_FILE = "tw_stock_list.json"

def fetch_and_save_stock_list():
    """
    從台灣證券交易所 (TWSE) 獲取台股清單，處理後儲存為 JSON 檔案。
    """
    print(f"正在從台灣證券交易所官方 API 下載最新的台股清單...\n{API_URL}")
    
    try:
        # 偽裝成瀏覽器發送請求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        twse_data = response.json()
        
        if twse_data['stat'] != 'OK':
            print(f"錯誤：證交所 API 回應狀態不為 OK: {twse_data.get('stat')}")
            return

        # 'data' 欄位是一個包含 [["代號", "名稱", ...], ...] 的列表
        all_stocks_raw = twse_data.get('data', [])
        print(f"成功下載 {len(all_stocks_raw)} 筆原始資料。")
        
        processed_stocks = []
        print("正在處理資料，轉換為我們需要的格式...")
        
        for stock_info in all_stocks_raw:
            # 確保資料格式正確 (至少有代號和名稱)
            if len(stock_info) >= 2:
                symbol_code = stock_info[0].strip()
                name = stock_info[1].strip()
                
                # yfinance 需要在台股代號後加上 '.TW'
                symbol_for_yfinance = f"{symbol_code}.TW"
                
                processed_stocks.append({
                    "symbol": symbol_for_yfinance,
                    "name": name
                })
        
        print(f"處理完成，總共 {len(processed_stocks)} 筆有效股票資料。")
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(processed_stocks, f, ensure_ascii=False, indent=2)
            
        print(f"成功！包含中文名稱的股票清單已儲存至 -> {OUTPUT_FILE}")
        
    except requests.exceptions.RequestException as e:
        print(f"錯誤：下載股票清單時發生網路錯誤: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"錯誤：無法解析從 API 收到的回應，格式可能已變更。錯誤: {e}")
    except Exception as e:
        print(f"處理過程中發生未知錯誤: {e}")

if __name__ == '__main__':
    fetch_and_save_stock_list()