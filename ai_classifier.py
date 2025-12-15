"""AI 曲風分類模組"""
import requests
import json


def classify_music_genre(song_infos, genre_dict, api_key, model):
    """使用 Gemini AI 判定音樂曲風"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    # 建立歌曲列表（包含歌手、專輯、歌名）
    songs_list = "\n".join([
        f"{i+1}. 歌手: {info['artist']} | 專輯: {info['album']} | 歌名: {info['song']}" 
        for i, info in enumerate(song_infos)
    ])
    
    # 建立曲風列表文字
    genre_list_text = "\n".join([f"{num}: {name}" for num, name in genre_dict.items()])
    
    # 設定 prompt
    prompt = f"""請根據以下歌曲資訊（包含歌手、專輯、歌名）判定每首歌的音樂曲風。

    可用的曲風列表及編號如下：
    {genre_list_text}

    請以 JSON 格式回傳結果，只需要回傳曲風編號（數字）和歌名，格式如下：
    [
        {{"song": "歌名", "genre_id": 編號}},
        ...
    ]

    請僅回傳 JSON，不要包含其他說明文字。

    歌曲列表：
    {songs_list}"""
    
    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.7
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        
        # 解析 AI 回應
        if "candidates" in result and len(result["candidates"]) > 0:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # 清理 JSON 標記（如果有的話）
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            # 解析 JSON
            classifications = json.loads(text)
            return classifications
        else:
            print(f"錯誤：無法取得 AI 回應")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"API 請求錯誤: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 解析錯誤: {e}")
        print(f"AI 回應內容: {text}")
        return None
    except Exception as e:
        print(f"發生錯誤: {e}")
        return None
