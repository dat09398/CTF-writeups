import os
import re
import requests
import subprocess

# Lấy Token từ thiết lập bảo mật của GitHub
HACKMD_TOKEN = os.environ.get("HACKMD_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HACKMD_TOKEN}"
}

def clean_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title).strip()

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
        print("Lỗi: Không tìm thấy HACKMD_TOKEN.")
        return

    print("Đang lấy danh sách bài viết từ HackMD...")
    notes = get_notes()

    for note in notes:
        title = note.get('title', 'Untitled')
        safe_title = clean_filename(title)
        note_id = note.get('id')
        
        print(f"Đang tải: {safe_title}.md ...")
        content = get_note_content(note_id)

        filename = f"{safe_title}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
            
if __name__ == "__main__":
    main()