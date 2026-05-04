import requests
import pandas as pd
import os
import re
from datetime import datetime, timedelta

# Cấu hình API
APP_ID = os.getenv('ADZUNA_APP_ID')
APP_KEY = os.getenv('ADZUNA_APP_KEY')
HISTORY_FILE = "data/full_history.csv"
DAILY_FILE = "data/daily_job.csv"

def guess_info(title):
    title = str(title).lower()
    # Suy luận kinh nghiệm
    exp = "1-3 years" # Mặc định
    if any(x in title for x in ['senior', 'lead', 'manager', 'principal']): exp = "3-5 years"
    elif any(x in title for x in ['junior', 'fresher', 'intern', 'graduate']): exp = "0-1 year"
    
    # Suy luận kỹ năng (Lấy các từ khóa phổ biến)
    skills_list = []
    keywords = ['python', 'sql', 'java', 'c++', 'aws', 'azure', 'react', 'data', 'analyst', 'machine learning', 'ai']
    for k in keywords:
        if k in title: skills_list.append(k.capitalize())
    
    skills = ", ".join(skills_list) if skills_list else "IT General"
    return exp, skills

def fetch_adzuna(country, pages=10):
    jobs = []
    print(f"📡 Đang khai thác Adzuna {country.upper()}...")
    for page in range(1, pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}?app_id={APP_ID}&app_key={APP_KEY}&results_per_page=50&what=it%20developer%20data"
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                results = res.json().get('results', [])
                for item in results:
                    title = item.get('title')
                    exp, sk = guess_info(title) # Tự động suy luận thông tin
                    jobs.append({
                        "id": str(item.get('id')),
                        "job_title": title,
                        "company": item.get('company', {}).get('display_name', 'N/A'),
                        "salary": item.get('salary_min'),
                        "location": f"{item.get('location', {}).get('display_name')} ({country.upper()})",
                        "experience": exp,
                        "skills": sk,
                        "raw_date": datetime.now().strftime("%Y-%m-%d")
                    })
            if len(jobs) >= 500: break
        except: continue
    return jobs

def main():
    # 1. Thu thập 1000 dòng
    all_raw = fetch_adzuna('gb') + fetch_adzuna('us')
    df_new = pd.DataFrame(all_raw)
    if df_new.empty: return

    # 2. Lọc trùng bằng ID (Bộ nhớ 30 ngày)
    os.makedirs('data', exist_ok=True)
    if os.path.exists(HISTORY_FILE):
        df_hist = pd.read_csv(HISTORY_FILE)
        df_hist['id'] = df_hist['id'].astype(str)
        df_unique = df_new[~df_new['id'].isin(df_hist['id'])].copy()
    else:
        df_unique = df_new.copy()
        df_hist = pd.DataFrame(columns=['id', 'raw_date'])

    # 3. Cập nhật lịch sử (Chỉ lưu ID và Ngày cho nhẹ)
    new_history = df_unique[['id', 'raw_date']]
    df_hist_updated = pd.concat([df_hist, new_history], ignore_index=True)
    df_hist_updated['raw_date'] = pd.to_datetime(df_hist_updated['raw_date'])
    df_hist_updated = df_hist_updated[df_hist_updated['raw_date'] >= (datetime.now() - timedelta(days=30))]
    df_hist_updated.to_csv(HISTORY_FILE, index=False)

    # 4. Xuất file Daily (Xóa ID, Cột khớp 100% dữ liệu VN)
    df_daily = df_unique.drop(columns=['id'])
    df_daily.to_csv(DAILY_FILE, index=False, encoding='utf-8-sig')
    print(f"✅ Hoàn tất! Đã lọc và lưu {len(df_daily)} job mới.")

if __name__ == "__main__":
    main()
