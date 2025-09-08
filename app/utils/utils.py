import os
import json
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

print(ROOT_DIR) 
DATA_DIR = ROOT_DIR / "data"
DOC_ID_STORE_FILE = DATA_DIR / "doc_id_store.json"

# 确保目录和文件存在


def ensure_store_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not DOC_ID_STORE_FILE.exists():
        with open(DOC_ID_STORE_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2, ensure_ascii=False)


def load_doc_ids():
    ensure_store_file()
    with open(DOC_ID_STORE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_doc_id(file_name: str, doc_id: str):
    data = load_doc_ids()
    data[file_name] = doc_id
    with open(DOC_ID_STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_doc_id(file_name: str) -> str | None:
    data = load_doc_ids()
    return data.get(file_name)
