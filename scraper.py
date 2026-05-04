import requests
import pandas as pd
import os
from datetime import datetime, timedelta

# Cấu hình API
APP_ID = os.getenv('ADZUNA_APP_ID')
APP_KEY = os.getenv('ADZUNA_APP_KEY')
HISTORY_FILE = "data/full_history.csv"
DAILY_FILE = "data/daily_job.csv"

def fetch_adzuna(country, pages=10):
    jobs = []
    print(f"📡 Đang cào Adzuna {country.upper()}...")
    for page in range(1, pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}?app_id={APP_ID}&app_key={APP_KEY}&results_per_page=50&what=it%20data%20science"
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                for item in res.json().get('results', []):
                    jobs.append({
                        "id": str(item.get('id')),
                        "job_title": item.get('title'),
                        "company": item.get('company', {}).get('display_name'),
                        "salary": item.get('salary_min'),
                        "location": f"{item.get('location', {}).get('display_name')} ({country.upper()})",
                        "raw_date": datetime.now().strftime("%Y-%m-%d")
                    })
            if len(jobs) >= 500: break # Đủ số lượng thì dừng
        except: continue
    return jobs

def main():
    # 1. Cào dữ liệu (Target 1000 dòng từ UK và US)
    raw_data = fetch_adzuna('gb') + fetch_adzuna('us')
    df_new = pd.DataFrame(raw_data)
    
    if df_new.empty: return

    # 2. Lọc trùng bằng ID với bộ nhớ 30 ngày
    os.makedirs('data', exist_ok=True)
    if os.path.exists(HISTORY_FILE):
        df_hist = pd.read_csv(HISTORY_FILE)
        df_hist['id'] = df_hist['id'].astype(str)
        # Chỉ lấy job có ID chưa từng xuất hiện
        df_unique = df_new[~df_new['id'].isin(df_hist['id'])].copy()
    else:
        df_unique = df_new.copy()
        df_hist = pd.DataFrame(columns=['id', 'raw_date'])

    # 3. Cập nhật kho lịch sử (chỉ lưu ID để nhẹ máy)
    df_hist_new = pd.concat([df_hist, df_unique[['id', 'raw_date']]], ignore_index=True)
    cutoff = datetime.now() - timedelta(days=30)
    df_hist_new['raw_date'] = pd.to_datetime(df_hist_new['raw_date'])
    df_hist_new = df_hist_new[df_hist_new['raw_date'] >= cutoff]
    df_hist_new.to_csv(HISTORY_FILE, index=False)

    # 4. Xuất file Daily (Xóa ID để đồng bộ hóa với Colab)
    # File này chỉ chứa hàng mới tinh, cột khớp 100% với cấu trúc VN
    df_unique = df_unique.drop(columns=['id'])
    df_unique.to_csv(DAILY_FILE, index=False, encoding='utf-8-sig')
    print(f"✅ Đã lọc! Lưu {len(df_unique)} job mới vào {DAILY_FILE}")

if __name__ == "__main__":
    main()
