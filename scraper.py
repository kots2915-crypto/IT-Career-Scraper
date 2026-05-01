import requests
import pandas as pd
import time
import os

# Lấy ID và Key từ hệ thống bảo mật của GitHub
APP_ID = os.getenv('ADZUNA_APP_ID')
APP_KEY = os.getenv('ADZUNA_APP_KEY')

def fetch_adzuna_data():
    print("📡 Đang gọi API Adzuna để lấy dữ liệu...")
    # Lấy dữ liệu việc làm IT (ưu tiên từ khóa Data, AI, Dev)
    url = f"https://api.adzuna.com/v1/api/jobs/gb/search/1?app_id={APP_ID}&app_key={APP_KEY}&results_per_page=20&what=it%20developer"
    
    try:
        response = requests.get(url)
        results = response.json().get('results', [])
        
        jobs = []
        for item in results:
            jobs.append({
                "job_title": item.get('title'),
                "salary_min": item.get('salary_min'),
                "location": "International",
                "source": "Adzuna API"
            })
        return pd.DataFrame(jobs)
    except Exception as e:
        print(f"❌ Lỗi kết nối API: {e}")
        return pd.DataFrame()

def process_data():
    # 1. Lấy dữ liệu từ API
    df_api = fetch_adzuna_data()
    
    # 2. Đọc file dữ liệu nội địa (nếu bạn đã cào file vn_jobs.csv lên GitHub)
    try:
        df_vn = pd.read_csv("vn_jobs.csv")
    except:
        # Dữ liệu dự phòng nếu chưa có file VN
        df_vn = pd.DataFrame([{"job_title": "Data Scientist (VN)", "salary_min": 25000000, "location": "HCMC", "source": "Manual Scrape"}])

    # 3. Hợp nhất dữ liệu
    final_df = pd.concat([df_api, df_vn], ignore_index=True)
    
    # 4. Tính toán xu hướng (Trend Analysis)
    # Áp dụng logic phân loại đơn giản để chatbot dễ xử lý
    def analyze_trend(title):
        t = str(title).upper()
        if any(x in t for x in ["AI", "DATA", "MACHINE", "LEARNING"]): return "🔥 High Demand"
        if any(x in t for x in ["PYTHON", "JAVA", "FLUTTER"]): return "📈 Growing"
        return "⚖️ Stable"

    final_df['trend'] = final_df['job_title'].apply(analyze_trend)
    final_df['last_updated'] = time.strftime("%Y-%m-%d %H:%M")

    # Lưu thành phẩm cho nhóm Web và Chatbot
    final_df.to_csv("daily_jobs.csv", index=False, encoding='utf-8-sig')
    print(f"✅ Thành công! Đã xử lý {len(final_df)} dòng dữ liệu cho đồ án.")

if __name__ == "__main__":
    process_data()
