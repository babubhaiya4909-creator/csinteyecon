import asyncio
from fastapi import FastAPI, Query
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import uvicorn
import os, re
import httpx

# ========= CONFIG =========
api_id = 31763063
api_hash = "e6ae5106b53940d0141fa76f4ed5ca20"
session_string = "1BVtsOLkBu77Q1lFVXNdBeUl13_nrKJ3ibNwh50nXuor_C3DLyvWp7dQK9ZbXjIKlSHA2ps50LcwAOs0IMNc-O7wLQw3lJm1YOj93GB80tTZSQPMhRhA8F3dIKCPtQMUlFUy-y8scDrgeBKoQnMXefKfg34xt5XU9ANI7PJXKHi0dlbM_PDlHxZ3A-KX-uBZaYbB_cPMY1AVTd67fHfYhrK7lc4fKd2rAvWt9-2BwehAyrnB8T9gOjTQVcUGMIVjaGMZtgGengnjz3898jCMVC5Lbe9rJ4EfB5wsJiniA_kJgb5kGlTgpR-fjV5F85jl7uF3OuaB6UdMbHRK_nh5P4T-dt6xno8g="
bot_username = "@doxxerTool404_bot"

PHONE_API = "https://located-surgeon-breed-schemes.trycloudflare.com/"

app = FastAPI()
client = TelegramClient(StringSession(session_string), api_id, api_hash)

# ========= PARSER =========
def parse_db_message(text):
    if not text:
        return None
    low = text.lower()
    if any(x in low for x in ["subjects made:", "number of results:", "buying a subscription"]):
        return "SKIP"
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if len(lines) < 2:
        return None
    return {
        "database": lines[0],
        "details": [l for l in lines if ":" in l]
    }

# ========= PHONE / CIRCLE API =========
async def fetch_phone_info(number):
    try:
        async with httpx.AsyncClient(timeout=10) as client_http:
            r = await client_http.get(PHONE_API, params={"num": number})
            data = r.json()
            if data.get("success"):
                return data.get("results", {})
    except:
        pass
    return {}

# ========= TELEGRAM ENGINE =========
async def scrape_all(query):
    results = []
    seen_titles = set()
    event_queue = asyncio.Queue()

    async def handler(event):
        await event_queue.put(event)

    client.add_event_handler(handler, events.NewMessage(from_users=bot_username))

    try:
        await client.send_message(bot_username, query)

        while True:
            try:
                event = await asyncio.wait_for(event_queue.get(), timeout=7.0)
                parsed = parse_db_message(event.text)

                if parsed == "SKIP":
                    continue

                if parsed:
                    if parsed["database"] in seen_titles:
                        break
                    seen_titles.add(parsed["database"])
                    results.append(parsed)

                if event.reply_markup:
                    for row in event.reply_markup.rows:
                        for btn in row.buttons:
                            if any(s in btn.text for s in ["➡", ">", "Next"]):
                                await asyncio.sleep(0.5)
                                await event.click(text=btn.text)
                                break
                        else:
                            continue
                        break
                    else:
                        break
                else:
                    break

            except asyncio.TimeoutError:
                break
    finally:
        client.remove_event_handler(handler)

    return results

@app.on_event("startup")
async def startup():
    await client.connect()

# ========= MAIN API =========
@app.get("/")
async def api_call(query: str = Query(None)):
    if not query:
        return {"error": "No query"}

    phone_info = await fetch_phone_info(query)
    final_results = await scrape_all(query)

    return {
        "status": "success",
        "phone_info": phone_info,
        "count": len(final_results),
        "results": final_results
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
