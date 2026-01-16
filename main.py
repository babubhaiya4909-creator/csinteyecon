import httpx
import asyncio
from fastapi import FastAPI, Header, HTTPException, Query
from typing import Optional

app = FastAPI(title="Eyecon API Wrapper")

# Configuration
VALID_API_KEY = "@CSINT"
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "E-Auth-V": "e1",
    "E-Auth": "dd2bc3e8-0f11-40c2-9bc2-81bcd862baf5",
    "E-Auth-C": "34",
    "E-Auth-K": "PgdtSBeR0MumR7fO",
}

async def fetch_data(client, url, params, headers):
    try:
        response = await client.get(url, params=params, headers=headers, timeout=10.0)
        return response
    except Exception as e:
        return None

@app.get("/lookup")
async def lookup(cli: str = Query(..., description="Phone number to lookup"), 
                 api_key: str = Header(..., alias="X-API-KEY")):
    
    # Auth Check
    if api_key != VALID_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    async with httpx.AsyncClient(http2=True, follow_redirects=False) as client:
        # Names and Pic requests in parallel for speed
        names_params = {
            "cli": cli, "lang": "en", "is_callerid": "true", "is_ic": "true",
            "cv": "vc_729_vn_4.2026.01.13.0939_a", "requestApi": "URLconnection", "source": "HISTORY"
        }
        
        pic_params = {
            "cli": cli, "is_callerid": "true", "size": "small", "type": "0",
            "src": "HISTORY", "cancelfresh": "0", "cv": "vc_729_vn_4.2026.01.13.0939_a"
        }

        # Executing concurrently
        name_task = fetch_data(client, "https://api.eyecon-app.com/app/getnames.jsp", names_params, BASE_HEADERS)
        pic_task = fetch_data(client, "https://api.eyecon-app.com/app/pic", pic_params, BASE_HEADERS)
        
        name_res, pic_res = await asyncio.gather(name_task, pic_task)

        # Process Results
        result = {"phone": cli, "names": [], "photo_url": None}

        if name_res and name_res.status_code == 200:
            result["names"] = name_res.json() if "application/json" in name_res.headers.get("content-type", "") else name_res.text
            
        if pic_res and pic_res.status_code == 302:
            result["photo_url"] = pic_res.headers.get("Location")

        return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
