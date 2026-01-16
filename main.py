import httpx
import asyncio
from fastapi import FastAPI, Query

app = FastAPI()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "E-Auth-V": "e1",
    "E-Auth": "dd2bc3e8-0f11-40c2-9bc2-81bcd862baf5",
    "E-Auth-C": "34",
    "E-Auth-K": "PgdtSBeR0MumR7fO",
}

@app.get("/lookup")
async def lookup(cli: str = Query(..., description="Phone number")):
    async with httpx.AsyncClient(http2=True, timeout=15.0) as client:
        # Request 1: Name Fetch
        name_task = client.get(
            "https://api.eyecon-app.com/app/getnames.jsp",
            params={
                "cli": cli, "lang": "en", "is_callerid": "true", 
                "cv": "vc_729_vn_4.2026.01.13.0939_a", "source": "HISTORY"
            },
            headers=HEADERS
        )

        # Request 2: High Quality Picture Fetch (size=big)
        pic_task = client.get(
            "https://api.eyecon-app.com/app/pic",
            params={
                "cli": cli, 
                "is_callerid": "true", 
                "size": "big", # Yahan 'big' karne se quality clear aayegi
                "type": "0", 
                "cv": "vc_729_vn_4.2026.01.13.0939_a"
            },
            headers=HEADERS,
            follow_redirects=False
        )

        responses = await asyncio.gather(name_task, pic_task, return_exceptions=True)
        name_res, pic_res = responses

        # Processing Results
        name_final = name_res.text.strip() if hasattr(name_res, 'status_code') and name_res.status_code == 200 else "Not Found"
        
        # 302 Redirect se Direct Link nikalna
        photo_final = "No Photo"
        if hasattr(pic_res, 'status_code') and pic_res.status_code == 302:
            photo_final = pic_res.headers.get("Location")

        return {
            "status": "success",
            "number": cli,
            "name": name_final,
            "photo_url": photo_final
        }
        
