import requests
import pandas as pd
import os
from datetime import datetime, timedelta

# Cấu hình
APP_ID = os.getenv('ADZUNA_APP_ID')
APP_KEY = os.getenv('ADZUNA_APP_KEY')
HISTORY_FILE = "data/full_history.csv"
DAILY_FILE = "data/daily_job.csv"

def fetch_data(country):
    all_jobs = []
    # Cào 10 trang để đảm bảo có khoảng 500 job/nước
    for page in range(1, 11):
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}?app_id={APP_ID}&app_key={APP_KEY}&results_per_page=50&what=it%20data"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                for item in res.json().get('results', []):
                    all_jobs.append({
                        "id": str(item.get('id')),
                        "job_title": item.get('title'),
                        "company": item.get('company', {}).get('display_name'), # Lấy tên công ty chuẩn
                        "salary": item.get('salary_min'),
                        "location": item.get('location', {}).get('display_name'),
                        "raw_date": datetime.now().strftime("%Y-%m-%d")
                    })
        except: continue
    return all_jobs

def run():
    # 1. Cào dữ liệu mới
    new_jobs = fetch_data('gb') + fetch_data('us')
    df_new = pd.DataFrame(new_jobs)
    
    # 2. Lọc trùng bằng ID với file Lịch sử
    if os.path.exists(HISTORY_FILE):
        df_history = pd.read_csv(HISTORY_FILE)
        df_history['id'] = df_history['id'].astype(str)
        # Chỉ lấy những cái ID chưa từng xuất hiện
        df_new_unique = df_new[~df_new['id'].isin(df_history['id'])]
    else:
        df_new_unique = df_new
        df_history = pd.DataFrame(columns=['id', 'raw_date'])

    # 3. Cập nhật kho lịch sử (Chỉ lưu ID và Ngày để siêu nhẹ)
    new_history_entries = df_new_unique[['id', 'raw_date']]
    df_history_updated = pd.concat([df_history, new_history_entries], ignore_index=True)
    
    # Dọn dẹp kho: Chỉ giữ ID của 30 ngày gần nhất cho nhẹ máy
    df_history_updated['raw_date'] = pd.to_datetime(df_history_updated['raw_date'])
    cutoff = datetime.now() - timedelta(days=30)
    df_history_updated = df_history_updated[df_history_updated['raw_date'] >= cutoff]
    
    # Lưu lại kho lịch sử
    os.makedirs('data', exist_ok=True)
    df_history_updated.to_csv(HISTORY_FILE, index=False)

    # 4. Lưu file Daily (Xóa cột ID đi để đồng bộ với VN)
    # File này chỉ chứa hàng mới tinh của ngày hôm nay
    df_daily = df_new_unique.drop(columns=['id']) 
    df_daily.to_csv(DAILY_FILE, index=False, encoding='utf-8-sig')
    
    print(f"✅ Đã lọc xong! Có {len(df_daily)} job mới tinh.")

if __name__ == "__main__":
    run()
