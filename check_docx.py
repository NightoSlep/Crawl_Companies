from docx import Document
from collections import Counter

def find_duplicate_companies(docx_path):
    doc = Document(docx_path)

    # lấy tất cả đoạn có style Heading 2 (tên công ty bạn đã lưu)
    names = []
    for para in doc.paragraphs:
        if para.style.name == "Heading 2":
            name = para.text.strip().upper()
            if name:
                names.append(name)

    # đếm số lần xuất hiện
    counter = Counter(names)

    # lọc ra tên bị trùng
    duplicates = {name: count for name, count in counter.items() if count > 1}

    if not duplicates:
        print("✅ Không có công ty nào bị trùng")
    else:
        print("⚠️ Các công ty trùng tên:")
        for name, count in duplicates.items():
            print(f"- {name}: {count} lần")

    return duplicates


if __name__ == "__main__":
    docx_file = "Vu.28.08.docx"  # 👉 đổi thành file Word của bạn
    find_duplicate_companies(docx_file)
