"""MP3 檔案處理模組"""
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TCON


def get_mp3_files(directory):
    """取得指定目錄中的所有 MP3 檔案及 metadata"""
    mp3_files = []
    path = Path(directory)
    
    for file in path.glob("**/*.mp3"):
        song_name = file.stem  # 不含副檔名的檔名
        
        # 讀取 MP3 metadata
        artist = ""
        album_name = ""
        has_genre = False
        existing_genre = None
        try:
            audio = MP3(str(file), ID3=ID3)
            if audio.tags:
                # 取得歌手標籤 (TPE1)
                if 'TPE1' in audio.tags:
                    artist = str(audio.tags['TPE1'])
                elif '\xa9ART' in audio.tags:  # iTunes format
                    artist = str(audio.tags['\xa9ART'])
                
                # 取得專輯名稱 (TALB)
                if 'TALB' in audio.tags:
                    album_name = str(audio.tags['TALB'])
                elif '\xa9alb' in audio.tags:  # iTunes format
                    album_name = str(audio.tags['\xa9alb'])
                
                # 檢查是否已有曲風標籤 (TCON)
                if 'TCON' in audio.tags:
                    has_genre = True
                    existing_genre = str(audio.tags['TCON'])
        except Exception as e:
            # 如果讀取失敗，使用預設值
            pass
        
        mp3_info = {
            "artist": artist,
            "album": album_name,
            "song": song_name,
            "file_path": str(file),  # 儲存完整檔案路徑
            "display_name": f"{artist} {album_name} {song_name}",
            "has_genre": has_genre,
            "existing_genre": existing_genre
        }
        mp3_files.append(mp3_info)
    
    return mp3_files


def update_mp3_genre(file_path, genre_id, genre_name):
    """更新 MP3 檔案的曲風 metadata"""
    try:
        audio = MP3(file_path, ID3=ID3)
        
        # 如果沒有 ID3 標籤，創建一個
        if audio.tags is None:
            audio.add_tags()
        
        # 更新曲風標籤 (TCON) - 使用括號格式: (編號)
        # 播放器會根據 ID3v1 標準自動對照顯示曲風名稱
        audio.tags['TCON'] = TCON(encoding=3, text=f"({genre_id})")
        
        # 儲存變更
        audio.save()
        return True
    except Exception as e:
        print(f"   ⚠️ 更新失敗: {e}")
        return False
