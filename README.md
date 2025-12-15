# AIGenreTagger
這是一個利用 Gemini AI 自動判定 MP3 歌曲曲風並修改檔案 Metadata 以實現分類的專案

可搭配 [SpotiDownloader](https://spotidownloader.com/) 等工具，以實現在 Auxio 等離線播放器能識別出曲風的效果

## 主要功能
- 透過 Gemini AI 根據歌名和歌手自動判定屬於 `genre_list.json` 的哪種曲風
- 根據結果修改 MP3 檔案的 Metadata TCON 標籤
- 自動處理所有子資料夾的 MP3 檔案
- 自動跳過 Metadata 已存在 TCON 標籤的 MP3 檔案

## 環境部署
安裝環境依賴：
```bash
pip install -r requirements.txt
```

將 `.env.example` 更名為 `.env` 並填入 Gemini API Key

將歌曲資料夾路徑填入 `config.json`

執行 `main.py`：
```bash
python main.py
```