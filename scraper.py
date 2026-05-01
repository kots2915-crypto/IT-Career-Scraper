import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Cấu hình robot chạy ngầm
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# Giả lập như trình duyệt thật để tránh bị chặn
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)

def scrape_data():
    print("🚀 Đang tiến vào 'mỏ dữ liệu'...")
    url = "https://itviec.com/it-jobs"
    driver.get(url)
    time.sleep(10) # Đợi lâu hơn một chút cho trang tải hết

    jobs = []
    # Thử tìm kiếm bằng nhiều loại "mật mã" khác nhau
    selectors = [".job-card", ".job_content", ".job-item", ".c-job-card"]
    
    elements = []
    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            print(f"✅ Tìm thấy dữ liệu bằng mã: {selector}")
            break

    for item in elements:
        try:
            # Tìm tên công việc (thử các thẻ h2 hoặc h3)
            title = item.find_element(By.CSS_SELECTOR, "h2, h3").text
            # Tìm địa điểm
            location = item.find_element(By.CSS_SELECTOR, ".city, .location").text
            
            jobs.append({
                "job_title": title, 
                "location": location, 
                "date": time.strftime("%d-%m-%Y")
            })
        except:
            continue

    if jobs:
        df = pd.DataFrame(jobs)
        df.to_csv("daily_jobs.csv", index=False, encoding='utf-8-sig')
        print(f"🎉 Tuyệt vời! Đã thu hoạch được {len(jobs)} tin.")
    else:
        print("⚠️ Cảnh báo: Robot đi về tay không. Không tìm thấy tin nào.")

if __name__ == "__main__":
    try:
        scrape_data()
    finally:
        driver.quit()
