import requests
import pandas as pd
import time
import os

APP_ID = os.getenv('ADZUNA_APP_ID')
APP_KEY = os.getenv('ADZUNA_APP_KEY')

def fetch_adzuna_data(pages=5):
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
                        "id": item.get('id'), # Dùng ID để lọc trùng
                        "job_title": item.get('title'),
                        "salary_min": item.get('salary_min'),
                        "location": item.get('location', {}).get('display_name', 'International'),
                        "date_scraped": time.strftime("%Y-%m-%d")
                    })
                print(f"   ✅ Đã lấy xong trang {page}")
            time.sleep(1) 
        except:
            continue
    return pd.DataFrame(all_jobs)

def accumulate_data():
    # 1. Lấy dữ liệu mới
    df_new = fetch_adzuna_data(pages=5)
    
    # 2. Kiểm tra và đọc dữ liệu cũ từ daily_jobs.csv
    file_path = "daily_jobs.csv"
    if os.path.exists(file_path):
        print("📁 Tìm thấy dữ liệu cũ, đang tiến hành tích lũy...")
        df_old = pd.read_csv(file_path)
        # Gộp mới và cũ
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        print("🆕 Chưa có dữ liệu cũ, tạo file mới...")
        df_final = df_new

    # 3. LOẠI BỎ TRÙNG LẶP (Cực kỳ quan trọng)
    # Tránh việc 1 công việc bị lưu nhiều lần nếu nó vẫn còn trên web vào hôm sau
    before_count = len(df_final)
    df_final = df_final.drop_duplicates(subset=['id'], keep='first')
    after_count = len(df_final)
    
    print(f"🧹 Đã loại bỏ {before_count - after_count} tin trùng lặp.")
    print(f"📊 Tổng số tin tích lũy được hiện tại: {after_count}")

    # 4. Lưu lại
    df_final.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"💾 Đã lưu thành phẩm vào {file_path}")

if __name__ == "__main__":
    accumulate_data()
