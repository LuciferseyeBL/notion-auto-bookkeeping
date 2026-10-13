from fastapi import FastAPI, Request
import os
from datetime import datetime
from notion_client import Client

app = FastAPI()

# 從 Render 環境變數動態讀取，不再寫死
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

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
