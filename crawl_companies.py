import json, time, random, threading, traceback
from queue import Queue, Empty

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ====== Cấu hình ======
START_PAGE = 1
END_PAGE = 10

MAX_WORKERS = 5   # số luồng chạy song song
HEADLESS = False  # True để ẩn chrome (CÓ THỂ LỖI)
OUTFILE = "companies.json"
# ======================

BASE_URL = "https://doanhnghiep.biz/dia-diem/long-an-801/?p={page}"

# Danh sách từ khóa tên công ty cần bỏ qua
KEYWORDS_TO_SKIP = ["DOANH NGHIỆP", "CHI NHÁNH", "HỢP TÁC XÃ", "VĂN PHÒNG"]

driver_lock = threading.Lock()

def build_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115 Safari/537.36"
    )
    if HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

    with driver_lock:
        driver = uc.Chrome(options=options, use_subprocess=True)
    return driver

def get_company_links(driver, page=1):
    """Lấy danh sách công ty từ 1 trang."""
    url = BASE_URL.format(page=page)
    driver.get(url)

    time.sleep(random.uniform(2, 5))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(2, 4))

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h6 a"))
        )
    except:
        print(f"⚠️ Trang {page} không load công ty nào")
        return []

    companies = []
    for a in driver.find_elements(By.CSS_SELECTOR, "h6 a"):
        name = a.get_attribute("textContent").strip() or a.text.strip()
        if not name:
            continue

        # --- Bỏ qua các tên chứa từ khóa ---
        if any(keyword in name.upper() for keyword in KEYWORDS_TO_SKIP):
            continue

        link = a.get_attribute("href")
        if link and not link.startswith("http"):
            link = "https://doanhnghiep.biz" + link

        companies.append({"name": name, "link": link})

    print(f"Trang {page} -> Tìm thấy {len(companies)} công ty (sau khi lọc từ khóa)")
    return companies

def worker(worker_id: int, q: Queue, results: list, results_lock: threading.Lock):
    """Luồng worker: lấy page từ queue, crawl công ty và lưu vào results."""
    driver = None
    try:
        driver = build_driver()
        while True:
            try:
                page = q.get(timeout=2)
            except Empty:
                break  # hết việc

            print(f"[W{worker_id}] ▶️ Đang lấy trang {page} ...")
            try:
                companies = get_company_links(driver, page)
                with results_lock:
                    results.extend(companies)
                print(f"[W{worker_id}] ✅ Hoàn tất trang {page}")
            except Exception as e:
                print(f"[W{worker_id}] ❌ Lỗi khi lấy trang {page}: {e}")
                traceback.print_exc(limit=1)

            q.task_done()
            time.sleep(random.uniform(2, 5))  # nghỉ ngẫu nhiên để tránh bị chặn

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
        print(f"[W{worker_id}] 🔚 Đã đóng driver.")

def main():
    # Tạo hàng đợi
    q = Queue()
    for page in range(START_PAGE, END_PAGE + 1):
        q.put(page)

    results = []
    results_lock = threading.Lock()

    # Tạo & chạy luồng
    workers = []
    n_workers = max(1, min(MAX_WORKERS, q.qsize()))
    print(f"🚀 Khởi động {n_workers} luồng ...")

    for wid in range(1, n_workers + 1):
        t = threading.Thread(target=worker, args=(wid, q, results, results_lock), daemon=True)
        t.start()
        workers.append(t)

    # Chờ các luồng xong
    for t in workers:
        t.join()

    # Xuất kết quả
    with open(OUTFILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✅ Đã lưu {len(results)} công ty hợp lệ vào {OUTFILE}")

if __name__ == "__main__":
    main()
