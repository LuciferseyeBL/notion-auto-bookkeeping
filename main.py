from fastapi import FastAPI, Request
import re
import os
from datetime import datetime
from notion_client import Client

app = FastAPI()

# 填入妳的 Notion API 金鑰與資料庫 ID（或從環境變數讀取）
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "YOUR_NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID", "YOUR_DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Bookkeeping API is running!"}

@app.post("/webhook")
async def receive_notification(request: Request):
    try:
        # 讀取 MacroDroid 傳過來的 raw body（文字內容）
        body_bytes = await request.body()
        text = body_bytes.decode("utf-8")
        
        if not text:
            return {"status": "error", "message": "Empty content"}
            
        print(f"Received notification: {text}")

        # ------------------------------------
        # 在這裡呼叫妳之前的 AI 解析 / 正則處理邏輯
        # 範例：提取金額與消費地點
        # ------------------------------------
        
        # 簡單示範寫入 Notion (請根據妳 Notion 資料庫的實際欄位調整)
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "名稱": {
                    "title": [{"text": {"content": text[:20] + "..."}}]
                },
                "明細": {
                    "rich_text": [{"text": {"content": text}}]
                },
                "日期": {
                    "date": {"start": datetime.now().strftime("%Y-%m-%d")}
                }
            }
        )
        return {"status": "success", "message": "Logged to Notion successfully"}

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}
