from fastapi import FastAPI, Request
import re
import os
from datetime import datetime
from notion_client import Client

app = FastAPI()

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

        # ------------------------------------
        # 智慧解析：使用正則表達式提取金額與品項
        # ------------------------------------
        amount = None
        item_name = "一般消費"

        # 嘗試抓取「NT$1,280」或「1280元」這類的金額
        amount_match = re.search(r'(?:NT\$|\$|台幣)\s*([0-9,]+)', text)
        if amount_match:
            amount_str = amount_match.group(1).replace(',', '')
            amount = float(amount_str) if '.' in amount_str else int(amount_str)

        # 嘗試從訊息中抓取消費地點或品項（例如：台灣高鐵、連鎖商店等）
        # 這裡會抓取關鍵字後面的文字或簡化內容
        if "台灣高鐵" in text:
            item_name = "台灣高鐵"
        elif "全家" in text or "7-ELEVEN" in text or "超商" in text:
            item_name = "超商消費"
        else:
            # 如果沒有特定關鍵字，就把整行訊息的前 15 個字當作品項名稱
            item_name = text[:15].strip()

        # ------------------------------------
        # 寫入 Notion 資料庫（完整對應 4 個欄位）
        # ------------------------------------
        properties = {
            "品項": {
                "title": [{"text": {"content": item_name}}]
            },
            "原始訊息": {
                "rich_text": [{"text": {"content": text}}]
            },
            "日期": {
                "date": {"start": datetime.now().strftime("%Y-%m-%d")}
            }
        }

        # 如果有成功抓到金額，才把金額欄位加進去
        if amount is not None:
            properties["金額"] = {"number": amount}

        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties=properties
        )
        
        return {"status": "success", "message": "Logged to Notion successfully with parsed data!"}

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}
