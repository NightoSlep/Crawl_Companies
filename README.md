# 🏢 DoanhNghiep.biz Crawler

Script này giúp bạn **crawl danh sách công ty** từ trang [doanhnghiep.biz](https://doanhnghiep.biz), lọc các công ty không hợp lệ, và lưu ra file JSON. Ngoài ra, bạn có thể crawl chi tiết từng công ty và xuất ra Word.

---

## ⚡ 1. Yêu cầu

- **Python 3.9+**  
- **Chrome/Chromium** đã cài trên máy  

---

## 📦 2. Cài đặt thư viện

Chạy các lệnh sau trong terminal:

```
pip install undetected-chromedriver selenium beautifulsoup4 python-docx
```

## 📝 3. Cấu hình script

Mở crawl_companies.py và sửa các thông số nếu cần:

```bash
START_PAGE = 40       # Trang bắt đầu

END_PAGE   = 50       # Trang kết thúc

BASE_URL = "https://doanhnghiep.biz/dia-diem/binh-duong-717/?p={page}"

KEYWORDS_TO_SKIP = ["DOANH NGHIỆP", "CHI NHÁNH", "HỢP TÁC XÃ"]

KEYWORDS_TO_SKIP → các từ khóa tên công ty muốn bỏ qua.

START_PAGE / END_PAGE → giới hạn số trang cần crawl.
```

## 🚀 4. Chạy script

### 4.1 Crawl danh sách công ty ra JSON

Chạy các lệnh sau trong terminal:

```
python crawl_companies.py
```

- Kết quả: file companies.json chứa danh sách công ty hợp lệ.

- Console sẽ hiển thị số lượng công ty mỗi trang.

### 4.2 Crawl chi tiết công ty và xuất ra Word

```
python crawl_details.py
```

## 📁 5. Kết quả

- companies.json → danh sách tên + link công ty.

- companies_data.docx → thông tin chi tiết từng công ty, dễ mở và copy.
