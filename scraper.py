import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import os

APP_ID = os.getenv('ADZUNA_APP_ID')
APP_KEY = os.getenv('ADZUNA_APP_KEY')

def fetch_adzuna_data(pages=5):
    # (Giữ nguyên phần này như code cũ)
    all_jobs = []
    print(f"📡 Đang bắt đầu thu thập dữ liệu từ {pages} trang Adzuna...")
    for page in range(1, pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/gb/search/{page}?app_id={APP_ID}&app_key={APP_KEY}&results_per_page=50&what=it%20developer"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                results = response.json().get('results', [])
                for item in results:
                    all_jobs.append({
                        "id": item.get('id'),
                        "job_title": item.get('title'),
                        "salary_min": item.get('salary_min'),
                        "location": item.get('location', {}).get('display_name', 'International'),
                        "date_scraped": time.strftime("%Y-%m-%d") # Lưu ngày dạng YYYY-MM-DD
                    })
                print(f"   ✅ Đã lấy xong trang {page}")
            time.sleep(1) 
        except:
            continue
    return pd.DataFrame(all_jobs)

def accumulate_data():
    df_new = fetch_adzuna_data(pages=5)
    file_path = "daily_jobs.csv"
    
    if os.path.exists(file_path):
        df_old = pd.read_csv(file_path)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new

    # Loại bỏ trùng lặp
    df_final = df_final.drop_duplicates(subset=['id'], keep='last')
    
    # 🧹 CHIẾN THUẬT CỬA SỔ TRƯỢT: Giới hạn dữ liệu
    # 1. Chuyển cột date_scraped sang dạng thời gian
    df_final['date_scraped'] = pd.to_datetime(df_final['date_scraped'])
    
    # 2. Tính mốc thời gian (Ví dụ: 30 ngày trước)
    cutoff_date = datetime.now() - timedelta(days=30)
    
    # 3. Chỉ giữ lại những tin cào được sau mốc thời gian đó
    before_purge = len(df_final)
    df_final = df_final[df_final['date_scraped'] >= cutoff_date]
    after_purge = len(df_final)
    
    # Chuyển ngược lại về dạng text để lưu CSV cho đẹp
    df_final['date_scraped'] = df_final['date_scraped'].dt.strftime('%Y-%m-%d')
    
    print(f"♻️ Đã dọn dẹp {before_purge - after_purge} tin quá hạn (cũ hơn 30 ngày).")
    print(f"📊 Dữ liệu sạch hiện tại: {len(df_final)} dòng.")

    # Lưu lại
    df_final.to_csv(file_path, index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    accumulate_data()
