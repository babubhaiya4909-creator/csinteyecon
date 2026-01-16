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
    try:
        async with httpx.AsyncClient(http2=True, timeout=10.0) as client:
            # Parallel Tasks
            n_task = client.get("https://api.eyecon-app.com/app/getnames.jsp", 
                                params={"cli": cli, "lang": "en", "is_callerid": "true", "cv": "vc_729_vn_4.2026.01.13.0939_a", "source": "HISTORY"}, 
                                headers=HEADERS)
            
            p_task = client.get("https://api.eyecon-app.com/app/pic", 
                                params={"cli": cli, "is_callerid": "true", "size": "big", "type": "0", "cv": "vc_729_vn_4.2026.01.13.0939_a"}, 
                                headers=HEADERS, follow_redirects=False)

            n_res, p_res = await asyncio.gather(n_task, p_task)

            # Crash-proof parsing
            name = n_res.text.strip() if n_res.status_code == 200 else "Not Found"
            photo = p_res.headers.get("Location", "No Photo") if p_res.status_code == 302 else "No Photo"

            return {"status": "success", "name": name, "photo": photo}
            
    except Exception as e:
        return {"status": "error", "message": str(e)} # Ye line error bata degi ki kya dikkat hai
