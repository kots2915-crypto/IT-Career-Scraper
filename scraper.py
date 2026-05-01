import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# 1. Cấu hình để Selenium chạy được trên máy chủ (Headless mode)
chrome_options = Options()
chrome_options.add_argument("--headless") # Chạy ngầm, không mở cửa sổ
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 2. Khởi tạo "Cánh tay robot"
driver = webdriver.Chrome(options=chrome_options)

def scrape_data():
    print("🚀 Đang khởi động robot cào dữ liệu...")
    # Thử nghiệm với một trang danh sách việc làm IT
    url = "https://itviec.com/it-jobs" 
    driver.get(url)
    time.sleep(5) # Đợi trang tải xong

    jobs = []
    # Tìm các tin tuyển dụng (Đây là lúc robot "soi" cấu trúc web)
    elements = driver.find_all(By.CLASS_NAME, "job_content")[:10] # Lấy 10 tin đầu để thử nghiệm

    for item in elements:
        try:
            title = item.find_element(By.TAG_NAME, "h2").text
            location = item.find_element(By.CLASS_NAME, "city").text
            jobs.append({"job_title": title, "location": location, "date": time.strftime("%Y-%m-%d")})
        except:
            continue

    # 3. Lưu thành file CSV
    df = pd.DataFrame(jobs)
    df.to_csv("daily_jobs.csv", index=False)
    print("✅ Đã lưu dữ liệu mới nhất!")

if __name__ == "__main__":
    try:
        scrape_data()
    finally:
        driver.quit()
