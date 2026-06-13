"""
STARS IT Career Scraper
"""

import requests
import pandas as pd
import os
import time
import logging
from datetime import datetime, timedelta

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger(__name__)

# Cấu hình 
APP_ID       = os.getenv('ADZUNA_APP_ID')
APP_KEY      = os.getenv('ADZUNA_APP_KEY')
HISTORY_FILE = "data/full_history.csv"
DAILY_FILE   = "data/daily_job.csv"
MAX_JOBS     = 500         
RESULTS_PER_PAGE = 50
RETRY_LIMIT  = 3            
RETRY_DELAY  = 2            

# Bảng skills
SKILL_MAP = {
    'data scientist':    'Python, SQL, Machine Learning, Statistics, Pandas',
    'data analyst':      'SQL, Python, Power BI, Excel, Tableau',
    'data engineer':     'Python, SQL, Spark, Airflow, ETL',
    'machine learning':  'Python, TensorFlow, Scikit-learn, Machine Learning',
    'ai engineer':       'Python, Deep Learning, TensorFlow, PyTorch',
    'business analyst':  'SQL, Excel, Power BI, Business Analysis, BPMN',
    'java':              'Java, Spring Boot, SQL, Git, REST API',
    'python':            'Python, Django hoặc Flask, SQL, Git',
    '.net':              'C#, .NET, SQL Server, Git',
    'backend':           'REST API, SQL, Git, Node.js hoặc Java hoặc Python',
    'node':              'Node.js, JavaScript, MongoDB, REST API, Git',
    'php':               'PHP, Laravel, MySQL, Git',
    'golang':            'Go, Docker, Kubernetes, REST API',
    'frontend':          'HTML, CSS, JavaScript, ReactJS, Git',
    'react':             'ReactJS, JavaScript, HTML, CSS, Git',
    'vue':               'VueJS, JavaScript, HTML, CSS, Git',
    'mobile':            'Flutter hoặc React Native, iOS hoặc Android, Git',
    'android':           'Kotlin, Java, Android SDK, Git',
    'ios':               'Swift, Xcode, iOS SDK, Git',
    'flutter':           'Flutter, Dart, Firebase, Git',
    'fullstack':         'HTML, CSS, JavaScript, ReactJS, Node.js, SQL, Git',
    'devops':            'Docker, Kubernetes, CI/CD, Linux, AWS hoặc GCP',
    'cloud':             'AWS, GCP hoặc Azure, Terraform, Docker, Linux',
    'sysadmin':          'Linux, Windows Server, Networking, Bash',
    'network':           'Cisco, Networking, CCNA, Firewall, VPN',
    'security':          'Penetration Testing, SIEM, Firewall, Linux, SOC',
    'tester':            'Manual Testing, Selenium, JIRA, Test Case',
    'qa':                'Automation Testing, Selenium, Python hoặc Java, JIRA',
    'helpdesk':          'Windows, Troubleshooting, Networking, Office 365',
    'support':           'Windows, Networking, Hardware, Troubleshooting',
    'scrum':             'Scrum, Agile, JIRA, Facilitation, Kanban',
    'project manager':   'Agile, Scrum, JIRA, MS Project, Risk Management',
    'product':           'Agile, Backlog, User Story, JIRA, Product Roadmap',
    'sap':               'SAP, ERP, ABAP hoặc SD hoặc MM, Business Process',
    'ui':                'Figma, Adobe XD, User Research, Prototyping',
    'ux':                'Figma, User Research, Wireframing, Prototyping',
    'sql':               'SQL, Database, Data Analysis, Excel',
    'aws':               'AWS, Cloud, Terraform, Linux, Docker',
    'azure':             'Azure, Cloud, DevOps, PowerShell, Terraform',
}

def guess_info(title: str):
    t = str(title).lower()

    # Experience
    if any(x in t for x in ['senior', 'sr.', 'lead', 'principal', 'head of', 'staff']):
        exp = "3-5 years"
    elif any(x in t for x in ['manager', 'director', 'architect', 'vp ', 'vice president']):
        exp = "5+ years"
    elif any(x in t for x in ['junior', 'jr.', 'fresher', 'graduate', 'entry']):
        exp = "0-1 year"
    elif any(x in t for x in ['intern', 'internship', 'thực tập']):
        exp = "0-1 year"
    else:
        exp = "1-3 years"

    # Skills 
    for keyword, skills in SKILL_MAP.items():
        if keyword in t:
            return exp, skills

    # Fallback theo nhóm ngành
    if any(x in t for x in ['developer', 'engineer', 'programmer']):
        return exp, 'Git, Programming, Problem Solving, SQL'
    if any(x in t for x in ['analyst', 'analysis']):
        return exp, 'SQL, Excel, Data Analysis, Reporting'
    if any(x in t for x in ['manager', 'lead', 'director']):
        return exp, 'Leadership, Project Management, Communication'
    if any(x in t for x in ['design', 'designer']):
        return exp, 'Figma, Adobe XD, Creative Design'

    return exp, "IT General Skills"


def fetch_adzuna(country: str, max_jobs: int = MAX_JOBS) -> list:
    jobs = []
    page = 1
    log.info(f" Bắt đầu khai thác Adzuna {country.upper()}...")

    while len(jobs) < max_jobs:
        url = (
            f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
            f"?app_id={APP_ID}&app_key={APP_KEY}"
            f"&results_per_page={RESULTS_PER_PAGE}"
            f"&what=it+developer+data+software"
            f"&sort_by=date"        
        )

        # Retry logic
        response = None
        for attempt in range(1, RETRY_LIMIT + 1):
            try:
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    break
                elif response.status_code == 429:
                    log.warning(f"  Rate limit! Chờ 10s... (attempt {attempt})")
                    time.sleep(10)
                else:
                    log.warning(f"  HTTP {response.status_code} trang {page}, attempt {attempt}")
                    time.sleep(RETRY_DELAY)
            except requests.exceptions.Timeout:
                log.warning(f"  Timeout trang {page}, attempt {attempt}")
                time.sleep(RETRY_DELAY)
            except requests.exceptions.RequestException as e:
                log.warning(f"  Request error trang {page}: {e}")
                time.sleep(RETRY_DELAY)

        if response is None or response.status_code != 200:
            log.error(f"   Bỏ qua trang {page} sau {RETRY_LIMIT} lần thử")
            page += 1
            if page > 20: 
                break
            continue

        results = response.json().get('results', [])
        if not results:
            log.info(f"  Không còn kết quả ở trang {page}, dừng.")
            break

        for item in results:
            title = item.get('title', '')
            exp, skills = guess_info(title)

            # Lấy cả salary_min và salary_max → tính trung bình
            sal_min = item.get('salary_min')
            sal_max = item.get('salary_max')
            if sal_min and sal_max:
                salary_val = (sal_min + sal_max) / 2
                salary_str = f"{int(sal_min)}-{int(sal_max)}"
            elif sal_min:
                salary_val = sal_min
                salary_str = str(int(sal_min))
            elif sal_max:
                salary_val = sal_max
                salary_str = str(int(sal_max))
            else:
                salary_val = None
                salary_str = "Negotiable"

            jobs.append({
                "id":          str(item.get('id', '')),
                "job_title":   title,
                "company":     item.get('company', {}).get('display_name', 'N/A'),
                "salary":      salary_str,
                "salary_raw":  salary_val,      
                "location":    f"{item.get('location', {}).get('display_name', 'N/A')} ({country.upper()})",
                "experience":  exp,
                "skills":      skills,
                "raw_date":    datetime.now().strftime("%Y-%m-%d"),
            })

        log.info(f"  Trang {page}: +{len(results)} jobs | Tổng: {len(jobs)}")
        page += 1
        time.sleep(0.5)     

    log.info(f" {country.upper()}: Thu được {len(jobs)} jobs")
    return jobs


def main():
    # Kiểm tra API key
    if not APP_ID or not APP_KEY:
        log.error(" Thiếu ADZUNA_APP_ID hoặc ADZUNA_APP_KEY trong environment!")
        raise SystemExit(1)

    os.makedirs('data', exist_ok=True)

    # 1. Thu thập dữ liệu
    all_raw = fetch_adzuna('gb') + fetch_adzuna('us') + fetch_adzuna('sg') + fetch_adzuna('in')
    df_new = pd.DataFrame(all_raw)

    if df_new.empty:
        log.warning(" Không lấy được job nào từ API. Thoát.")
        raise SystemExit(0)   # Exit 0 để workflow không báo fail

    log.info(f"Tổng thu thập: {len(df_new)} jobs (trước lọc trùng)")

    # 2. Lọc trùng 
    today_str = datetime.now().strftime("%Y-%m-%d")
    df_new['day_key'] = df_new['id'] + '_' + today_str  # Key duy nhất theo ngày

    if os.path.exists(HISTORY_FILE):
        df_hist = pd.read_csv(HISTORY_FILE, dtype={'id': str})
        # Tương thích ngược: file history cũ chưa có cột day_key → tự tạo
        if 'day_key' not in df_hist.columns:
            df_hist['day_key'] = df_hist['id'].astype(str) + '_' + df_hist['raw_date'].astype(str)
        df_hist['day_key'] = df_hist['day_key'].astype(str)
        seen_today = set(df_hist[df_hist['raw_date'] == today_str]['day_key'].tolist())
        df_unique = df_new[~df_new['day_key'].isin(seen_today)].copy()
        log.info(f" Đã thấy hôm nay: {len(seen_today)} | Mới thêm: {len(df_unique)}")
    else:
        df_unique = df_new.copy()
        df_hist = pd.DataFrame(columns=['id', 'day_key', 'raw_date'])
        log.info(" Không có lịch sử, lưu toàn bộ.")

    # 3. Cập nhật lịch sử 
    new_history = df_unique[['id', 'day_key', 'raw_date']].copy()
    df_hist_updated = pd.concat([df_hist, new_history], ignore_index=True)
    df_hist_updated['raw_date'] = pd.to_datetime(df_hist_updated['raw_date'], errors='coerce')
    cutoff = datetime.now() - timedelta(days=30)
    df_hist_updated = df_hist_updated[df_hist_updated['raw_date'] >= cutoff]
    df_hist_updated.to_csv(HISTORY_FILE, index=False)
    log.info(f" Lịch sử: {len(df_hist_updated)} entries (30 ngày gần nhất)")

    # 4. Xuất daily_job.csv
    if df_unique.empty:
        log.info("  Không có job mới hôm nay. Giữ nguyên file cũ.")
        raise SystemExit(0)

    df_daily = df_unique.drop(columns=['id', 'day_key', 'salary_raw'], errors='ignore')
    df_daily.to_csv(DAILY_FILE, index=False, encoding='utf-8-sig')
    log.info(f" Đã lưu {len(df_daily)} jobs mới vào {DAILY_FILE}")


if __name__ == "__main__":
    main()
