from fastapi import FastAPI, Request
import re
import os
from datetime import datetime
from notion_client import Client

app = FastAPI()

# 直接填入妳提供的金鑰與資料庫 ID，確保不會讀不到
NOTION_TOKEN = "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"
DATABASE_ID = "3f7c65ac4ce78051b102f2167825b374"

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

        # 寫入 Notion 資料庫
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
