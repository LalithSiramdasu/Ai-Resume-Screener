from pathlib import Path

import requests

BASE_URL = "http://127.0.0.1:8000/api"
SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"


def test_flow():
    print("1. Uploading files...")

    resume_path = SAMPLES_DIR / "resume_fullstack.txt"
    jd_path = SAMPLES_DIR / "jd_fullstack.txt"

    if not resume_path.exists() or not jd_path.exists():
        print("Sample files are missing. Expected files in:", SAMPLES_DIR)
        return

    with open(resume_path, "rb") as r:
        with open(jd_path, "rb") as j:
            files = {
                "resume": ("resume.txt", r, "text/plain"),
                "job_description": ("jd.txt", j, "text/plain"),
            }
            res = requests.post(f"{BASE_URL}/upload", files=files, timeout=120)

    if res.status_code != 200:
        print(f"Upload failed: {res.status_code}")
        print(res.text)
        return

    data = res.json()
    session_id = data.get("session_id")
    print(f"Success! Session ID: {session_id}")

    print("\n2. Asking a question...")
    q = "Does this candidate meet the JD requirements?"
    payload = {"session_id": session_id, "question": q}

    chat_res = requests.post(f"{BASE_URL}/chat", json=payload, timeout=120)
    if chat_res.status_code != 200:
        print(f"Chat failed: {chat_res.status_code}")
        print(chat_res.text)
        return

    chat_data = chat_res.json()
    print("\nAI ANSWER:")
    print(chat_data.get("answer"))


if __name__ == "__main__":
    test_flow()
