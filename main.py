import os
import json
from dotenv import load_dotenv

from config_loader import load_config, load_genre_list
from mp3_handler import get_mp3_files, update_mp3_genre
from ai_classifier import classify_music_genre

load_dotenv()

# === 設定區域 ===
config = load_config()
API_KEY = os.getenv("API_KEY")
MODEL = config["model"]
MP3_DIRECTORY = config["mp3_directory"]
BATCH_SIZE = config["batch_size"]
GENRE_LIST_FILE = config["genre_list_file"]


def main():
    """主程式"""
    print("=== MP3 音樂曲風分類器 ===\n")
    
    # 檢查 API Key
    if not API_KEY:
        print("❌ 請先在 .env 檔案中設定 API_KEY！")
        print("範例：API_KEY=你的_API_Key")
        return
    # 載入曲風列表
    print("正在載入曲風列表...")
    genre_dict = load_genre_list(GENRE_LIST_FILE)
    if not genre_dict:
        return
    print(f"✓ 載入 {len(genre_dict)} 種曲風\n")
        # 取得 MP3 檔案
    print(f"正在掃描目錄: {MP3_DIRECTORY}")
    mp3_files = get_mp3_files(MP3_DIRECTORY)
    
    if not mp3_files:
        print(f"❌ 在 {MP3_DIRECTORY} 中找不到任何 MP3 檔案")
        return
    
    print(f"✓ 找到 {len(mp3_files)} 個 MP3 檔案\n")
    
    # 篩選掉已有曲風的歌曲
    files_with_genre = [f for f in mp3_files if f.get('has_genre', False)]
    files_without_genre = [f for f in mp3_files if not f.get('has_genre', False)]
    
    if files_with_genre:
        print(f"ℹ️  {len(files_with_genre)} 首歌已有曲風標籤，將跳過")
        for f in files_with_genre[:5]:  # 只顯示前 5 首
            print(f"   - {f['song']} [曲風: {f.get('existing_genre', 'N/A')}]")
        if len(files_with_genre) > 5:
            print(f"   ... 及其他 {len(files_with_genre) - 5} 首\n")
        else:
            print()
    
    if not files_without_genre:
        print("✓ 所有歌曲都已有曲風標籤，無需處理")
        return
    
    print(f"✅ 將處理 {len(files_without_genre)} 首缺少曲風的歌曲\n")
    mp3_files = files_without_genre
    
    # 分批處理
    total_batches = (len(mp3_files) + BATCH_SIZE - 1) // BATCH_SIZE
    all_results = []
    
    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(mp3_files))
        batch = mp3_files[start_idx:end_idx]
        
        print(f"處理第 {batch_num + 1}/{total_batches} 批 ({len(batch)} 首歌曲)...")
        
        # 呼叫 AI 分類
        results = classify_music_genre(batch, genre_dict, API_KEY, MODEL)
        
        if results:
            all_results.extend(results)
            print(f"✓ 完成第 {batch_num + 1} 批分類\n")
        else:
            print(f"❌ 第 {batch_num + 1} 批分類失敗\n")
    
    # 顯示結果並對照曲風名稱
    print("\n=== 分類結果 ===\n")
    final_results = []
    
    # 建立歌名到完整資訊的映射
    song_info_map = {info['song']: info for info in mp3_files}
    
    for i, result in enumerate(all_results, 1):
        song_name = result.get("song", "未知")
        genre_id = str(result.get("genre_id", "12"))  # 預設為 Other
        genre_name = genre_dict.get(genre_id, "Other")
        
        # 取得完整歌曲資訊
        song_info = song_info_map.get(song_name, {"artist": "Unknown", "album": "Unknown", "song": song_name})
        
        final_result = {
            "artist": song_info.get("artist", "Unknown"),
            "album": song_info.get("album", "Unknown"),
            "song": song_name,
            "genre_id": genre_id,
            "genre_name": genre_name
        }
        final_results.append(final_result)
        
        print(f"{i}. {song_info.get('artist', 'Unknown')} - {song_name}")
        print(f"   專輯: {song_info.get('album', 'Unknown')}")
        print(f"   曲風: [{genre_id}] {genre_name}\n")
    
    # 儲存結果到檔案
    output_file = "music_classification_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 結果已儲存至 {output_file}")
    
    # 更新 MP3 檔案的曲風 metadata
    print("\n=== 更新 MP3 曲風 Metadata ===\n")
    success_count = 0
    fail_count = 0
    
    for result in final_results:
        song_name = result['song']
        genre_id = result['genre_id']
        genre_name = result['genre_name']
        
        # 從 song_info_map 取得檔案路徑
        song_info = song_info_map.get(song_name)
        if song_info and 'file_path' in song_info:
            file_path = song_info['file_path']
            print(f"更新: {song_name} → [{genre_id}] {genre_name}")
            
            if update_mp3_genre(file_path, genre_id, genre_name):
                success_count += 1
            else:
                fail_count += 1
        else:
            print(f"⚠️  找不到檔案: {song_name}")
            fail_count += 1
    
    print(f"\n✓ 成功更新 {success_count} 個檔案")
    if fail_count > 0:
        print(f"⚠️  失敗 {fail_count} 個檔案")


if __name__ == "__main__":
    main()