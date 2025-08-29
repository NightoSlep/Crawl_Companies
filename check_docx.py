from docx import Document
from collections import Counter
import re

def normalize_phone(phone: str) -> str:
    """Chuẩn hóa số điện thoại: chỉ giữ chữ số."""
    if not phone:
        return ""
    return re.sub(r"\D", "", phone)

def find_duplicates(docx_path):
    doc = Document(docx_path)

    names = []
    phones = []

    current_company = None

    for para in doc.paragraphs:
        text = para.text.strip()

        # Công ty (Heading 2)
        if para.style.name == "Heading 2":
            current_company = text.upper()
            if current_company:
                names.append(current_company)

        # Số điện thoại (nằm trong đoạn có chữ "Điện thoại")
        elif "Điện thoại" in text:
            phone = text.split(":", 1)[-1].strip()
            phone_norm = normalize_phone(phone)
            if phone_norm:
                phones.append(phone_norm)

    # Kiểm tra trùng tên
    name_counter = Counter(names)
    duplicate_names = {n: c for n, c in name_counter.items() if c > 1}

    # Kiểm tra trùng số điện thoại
    phone_counter = Counter(phones)
    duplicate_phones = {p: c for p, c in phone_counter.items() if c > 1}

    # In kết quả
    if not duplicate_names:
        print("✅ Không có công ty nào trùng tên")
    else:
        print("⚠️ Công ty trùng tên:")
        for n, c in duplicate_names.items():
            print(f"- {n}: {c} lần")

    if not duplicate_phones:
        print("✅ Không có số điện thoại nào trùng")
    else:
        print("⚠️ Số điện thoại trùng:")
        for p, c in duplicate_phones.items():
            print(f"- {p}: {c} lần")

    return duplicate_names, duplicate_phones


if __name__ == "__main__":
    docx_file = "Vu.30.08.docx"  # 👉 đổi thành file Word của bạn
    find_duplicates(docx_file)
