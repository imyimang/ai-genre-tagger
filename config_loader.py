"""配置載入模組"""
import json


def load_config():
    """載入設定檔"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ 找不到 config.json，使用預設值")
        return {
            "model": "gemini-2.5-flash",
            "mp3_directory": ".",
            "batch_size": 20,
            "genre_list_file": "genre_list.json"
        }
    except json.JSONDecodeError:
        print("❌ config.json 格式錯誤，使用預設值")
        return {
            "model": "gemini-2.5-flash",
            "mp3_directory": ".",
            "batch_size": 20,
            "genre_list_file": "genre_list.json"
        }


def load_genre_list(genre_list_file):
    """載入曲風列表"""
    try:
        with open(genre_list_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ 找不到曲風列表檔案: {genre_list_file}")
        return None
    except json.JSONDecodeError:
        print(f"❌ 曲風列表檔案格式錯誤")
        return None
