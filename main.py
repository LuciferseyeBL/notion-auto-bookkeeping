from fastapi import FastAPI, Request
import re
import os
from datetime import datetime
from notion_client import Client

app = FastAPI()

NOTION_TOKEN = "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"
DATABASE_ID = "3f7c65ac4ce78051b102f2167825b374"

notion = Client(auth=NOTION_TOKEN)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Bookkeeping API is running!"}

@app.post("/webhook")
async def receive_notification(request: Request):
    try:
        body_bytes = await request.body()
        text = body_bytes.decode("utf-8")
        
        if not text:
            return {"status": "error", "message": "Empty content"}
            
        print(f"Received notification: {text}")

        # 寫入 Notion 資料庫（對應正確的欄位名稱：品項、原始訊息、日期）
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "品項": {
                    "title": [{"text": {"content": text[:20] + "..."}}]
                },
                "原始訊息": {
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
