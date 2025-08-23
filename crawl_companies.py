import json, time, random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://doanhnghiep.biz/dia-diem/tp-ho-chi-minh-701/?p={page}"

START_PAGE = 350
END_PAGE = 360

# Danh sách từ khóa tên công ty cần bỏ qua
KEYWORDS_TO_SKIP = ["DOANH NGHIỆP", "CHI NHÁNH", "HỢP TÁC XÃ"]


def get_company_links(driver, page=1):
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
        name = a.get_attribute("textContent").strip()
        if not name:
            name = a.text.strip()

        # --- Bỏ qua các tên chứa từ khóa ---
        if any(keyword in name.upper() for keyword in KEYWORDS_TO_SKIP):
            continue

        link = a.get_attribute("href")
        if link and not link.startswith("http"):
            link = "https://doanhnghiep.biz" + link

        companies.append({"name": name, "link": link})

    print(f"Trang {page} -> Tìm thấy {len(companies)} công ty (sau khi lọc từ khóa)")
    return companies

if __name__ == "__main__":
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115 Safari/537.36"
    )

    driver = uc.Chrome(options=options)
    all_companies = []

    try:
        for page in range(START_PAGE, END_PAGE + 1):
            print(f"Đang lấy trang {page} ...")
            all_companies.extend(get_company_links(driver, page))
            time.sleep(random.uniform(5, 12))
    finally:
        driver.quit()

    with open("companies.json", "w", encoding="utf-8") as f:
        json.dump(all_companies, f, ensure_ascii=False, indent=2)

    print(f"✅ Đã lưu {len(all_companies)} công ty hợp lệ vào companies.json")
