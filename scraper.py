import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# 1. Cấu hình chạy ngầm trên máy chủ GitHub
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

def scrape_data():
    print("🚀 Robot đang bắt đầu cào dữ liệu thực tế...")
    url = "https://itviec.com/it-jobs" 
    driver.get(url)
    time.sleep(7) # Đợi trang tải kỹ hơn để tránh bị trống dữ liệu

    jobs = []
    # ĐÃ SỬA LỖI: Dùng find_elements (chuẩn Selenium) thay vì find_all
    # Mình dùng CSS_SELECTOR để robot tìm chính xác khung của từng công việc
    elements = driver.find_elements(By.CSS_SELECTOR, ".job-card") 

    for item in elements:
        try:
            # Lấy tên công việc
            title = item.find_element(By.TAG_NAME, "h2").text
            # Lấy địa điểm
            location = item.find_element(By.CLASS_NAME, "city").text
            
            jobs.append({
                "job_title": title, 
                "location": location, 
                "date": time.strftime("%Y-%m-%d")
            })
        except:
            continue # Nếu 1 tin bị lỗi thì bỏ qua để lấy tin tiếp theo

    if jobs:
        df = pd.DataFrame(jobs)
        # Lưu file với định dạng utf-8-sig để không bị lỗi font tiếng Việt khi mở bằng Excel
        df.to_csv("daily_jobs.csv", index=False, encoding='utf-8-sig')
        print(f"✅ Thành công! Đã lấy được {len(jobs)} tin mới nhất.")
    else:
        print("⚠️ Cảnh báo: Không tìm thấy tin nào. Có thể trang web đã thay đổi cấu trúc.")

if __name__ == "__main__":
    try:
        scrape_data()
    finally:
        driver.quit()
