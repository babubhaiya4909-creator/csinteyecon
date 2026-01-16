import httpx
import asyncio
from fastapi import FastAPI, Query

app = FastAPI()

# Headers constant rakhe hain taaki block na ho
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "E-Auth-V": "e1",
    "E-Auth": "dd2bc3e8-0f11-40c2-9bc2-81bcd862baf5",
    "E-Auth-C": "34",
    "E-Auth-K": "PgdtSBeR0MumR7fO",
}

@app.get("/lookup")
async def lookup(cli: str = Query(..., description="Phone number")):
    async with httpx.AsyncClient(http2=True, follow_redirects=False, timeout=10.0) as client:
        # Dono request ek saath (Parallel) start hongi
        name_task = client.get(
            "https://api.eyecon-app.com/app/getnames.jsp", 
            params={"cli": cli, "lang": "en", "is_callerid": "true", "is_ic": "true", "cv": "vc_729_vn_4.2026.01.13.0939_a", "requestApi": "URLconnection", "source": "HISTORY"},
            headers=HEADERS
        )
        
        pic_task = client.get(
            "https://api.eyecon-app.com/app/pic",
            params={"cli": cli, "is_callerid": "true", "size": "small", "type": "0", "src": "HISTORY", "cancelfresh": "0", "cv": "vc_729_vn_4.2026.01.13.0939_a"},
            headers=HEADERS
        )

        # Yahan fast processing ho rahi hai (Parallel execution)
        name_res, pic_res = await asyncio.gather(name_task, pic_task)

        # Response parsing
        name_data = "Not Found"
        if name_res.status_code == 200:
            try:
                name_data = name_res.json()
            except:
                name_data = name_res.text

        photo_url = pic_res.headers.get("Location", "No Photo") if pic_res.status_code == 302 else "No Photo"

        return {
            "status": "success",
            "phone": cli,
            "name": name_data,
            "photo": photo_url
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
