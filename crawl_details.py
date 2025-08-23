import json, time, random, datetime, re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from docx import Document

DETAIL_FIELDS = {
    "Ngày cấp": "Ngày cấp",
    "Ngày hoạt động": "Ngày hoạt động",
    "Tình trạng": "Tình trạng",
    "Địa chỉ": "Địa chỉ",
    "Người đại diện": "Người đại diện",
    "Điện thoại": "Điện thoại",
}

VALID_PREFIXES = ["096", "097", "098", "090", "093", "089", "086", "070", ]
VALID_PREFIX_RANGES = [(32, 39), (76, 79)]  # 032-039, 076-079


def is_valid_phone(phone: str) -> bool:
    if not phone:
        return False
    # lấy 3 số đầu
    digits = re.sub(r"\D", "", phone)  # bỏ ký tự không phải số
    if len(digits) < 3:
        return False
    prefix = digits[:3]

    # check trong list cố định
    if prefix in VALID_PREFIXES:
        return True

    # check trong khoảng (032-039, 070-079)
    try:
        prefix_int = int(prefix)
        for low, high in VALID_PREFIX_RANGES:
            if low <= prefix_int <= high:
                return True
    except:
        return False

    return False


def get_company_details(driver, url):
    driver.get(url)
    time.sleep(random.uniform(2, 4))

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(2, 4))

    # Nếu Cloudflare challenge xuất hiện thì chờ xử lý
    page_html = driver.page_source
    if "Checking your browser" in page_html or "cf-browser-verification" in page_html:
        print(f"⚠️ Cloudflare chặn, đợi xử lý...")
        time.sleep(random.uniform(8, 12))
        driver.refresh()
        time.sleep(random.uniform(3, 6))

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )
    except:
        print("❌ Không lấy được chi tiết")
        return {field: None for field in DETAIL_FIELDS}

    details = {field: None for field in DETAIL_FIELDS}
    rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) == 2:
            key = cols[0].text.strip()
            val = cols[1].text.strip()
            if key in details:
                details[key] = val

    return details


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

    with open("companies.json", "r", encoding="utf-8") as f:
        companies = json.load(f)

    results = []
    for company in companies:
        print(f"Đang lấy chi tiết: {company['name']}")
        try:
            details = get_company_details(driver, company["link"])

            # lọc theo số điện thoại
            phone = details.get("Điện thoại")
            if not is_valid_phone(phone):
                print(f"❌ Bỏ qua {company['name']} (số điện thoại không hợp lệ: {phone})")
                continue

            company.update(details)
            results.append(company)
        except Exception as e:
            print(f"❌ Lỗi khi lấy {company['name']}: {e}")
        time.sleep(random.uniform(3, 6))

    driver.quit()

    # Xuất ra Word
    doc = Document()
    for comp in results:
        doc.add_paragraph(comp["name"].upper(), style="Heading 2")

        for field, _ in DETAIL_FIELDS.items():
            value = comp.get(field, "")
            if value:
                doc.add_paragraph(f"{field}: {value}")

        doc.add_paragraph("")  # cách giữa các công ty

    doc.save("Vũ.23-8.docx")
    print("✅ Đã lưu kết quả vào Vũ.23-8.docx")
