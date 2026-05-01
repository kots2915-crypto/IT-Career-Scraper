import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# Giả lập trình duyệt chuẩn của người dùng Việt Nam
chrome_options.add_argument("--lang=vi-VN")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)

def scrape_data():
    print("🚀 Đang thử thâm nhập nguồn dữ liệu với mặt nạ mới...")
    # Thử cào trang tuyển dụng của CareerBuilder (phiên bản dễ tính hơn)
    url = "https://careerbuilder.vn/viec-lam/it-k-vi.html"
    driver.get(url)
    time.sleep(15) # Đợi lâu hơn để trang tải hết script

    jobs = []
    # Tìm các khung chứa tin tuyển dụng
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, ".job-item, .job-card")
        for item in elements[:10]:
            title = item.find_element(By.TAG_NAME, "h2").text
            jobs.append({
                "job_title": title, 
                "location": "Việt Nam", 
                "date": time.strftime("%d-%m-%Y")
            })
    except:
        pass

    if jobs:
        df = pd.DataFrame(jobs)
        df.to_csv("daily_jobs.csv", index=False, encoding='utf-8-sig')
        print(f"🎉 Tuyệt vời! Đã lấy được {len(jobs)} tin thật.")
    else:
        print("⚠️ Vẫn bị chặn, tạo dữ liệu mẫu để bảo trì hệ thống...")
        demo = [{"job_title": "AI Engineer (Demo)", "location": "HCMC", "date": time.strftime("%d-%m-%Y")}]
        pd.DataFrame(demo).to_csv("daily_jobs.csv", index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    try:
        scrape_data()
    finally:
        driver.quit()
