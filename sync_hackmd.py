import os
import re
import requests
import time

# Lấy Token từ thiết lập bảo mật của GitHub
HACKMD_TOKEN = os.environ.get("HACKMD_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HACKMD_TOKEN}"
}

def clean_filename(title):
    if not title:
        return "Untitled"
    return re.sub(r'[\\/*?:"<>|]', "", str(title)).strip()

def get_notes():
    url = "https://api.hackmd.io/v1/notes"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_note_content(note_id):
    url = f"https://api.hackmd.io/v1/notes/{note_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json().get('content', '')

def main():
    if not HACKMD_TOKEN:
        print("Lỗi: Không tìm thấy HACKMD_TOKEN. Vui lòng kiểm tra lại cấu hình Secrets trên GitHub.")
        return

    print("Đang lấy danh sách bài viết từ HackMD...")
    try:
        notes = get_notes()
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API lấy danh sách bài viết: {e}")
        if e.response is not None:
            print(f"Chi tiết lỗi: {e.response.text}")
        return

    for note in notes:
        title = note.get('title', 'Untitled')
        safe_title = clean_filename(title)
        note_id = note.get('id')
        
        print(f"Đang tải: {safe_title}.md ...")
        try:
            content = get_note_content(note_id)
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi tải bài viết '{safe_title}' (ID: {note_id}): {e}")
            if e.response is not None:
                print(f"Chi tiết lỗi: {e.response.text}")
            continue

        filename = f"{safe_title}.md"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Lỗi khi lưu file '{filename}': {e}")
            
        # Thêm khoảng trễ nhỏ để tránh bị giới hạn API (rate limit 60 requests/minute)
        time.sleep(1.5)

if __name__ == "__main__":
    main()