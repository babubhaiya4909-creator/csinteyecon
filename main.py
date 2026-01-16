import httpx
import asyncio
from fastapi import FastAPI, HTTPException, Query

app = FastAPI()

# Constant Config
VALID_KEY = "@CSINT"
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "E-Auth-V": "e1",
    "E-Auth": "dd2bc3e8-0f11-40c2-9bc2-81bcd862baf5",
    "E-Auth-C": "34",
    "E-Auth-K": "PgdtSBeR0MumR7fO",
}

@app.get("/lookup")
async def lookup(
    cli: str = Query(..., description="Phone number"),
    key: str = Query(..., description="API Key") # Ab key URL parameter mein hai
):
    # API Key Validation
    if key != VALID_KEY:
        raise HTTPException(status_code=403, detail="Galti mat kar bhai, sahi key daal!")

    async with httpx.AsyncClient(http2=True, follow_redirects=False, timeout=10.0) as client:
        # Dono request parallel mein chalengi fast processing ke liye
        name_url = "https://api.eyecon-app.com/app/getnames.jsp"
        pic_url = "https://api.eyecon-app.com/app/pic"

        params_name = {
            "cli": cli, "lang": "en", "is_callerid": "true", "is_ic": "true",
            "cv": "vc_729_vn_4.2026.01.13.0939_a", "requestApi": "URLconnection", "source": "HISTORY"
        }
        
        params_pic = {
            "cli": cli, "is_callerid": "true", "size": "small", "type": "0",
            "src": "HISTORY", "cancelfresh": "0", "cv": "vc_729_vn_4.2026.01.13.0939_a"
        }

        # Parallel Execution (Async)
        name_task = client.get(name_url, params=params_name, headers=BASE_HEADERS)
        pic_task = client.get(pic_url, params=params_pic, headers=BASE_HEADERS)
        
        name_res, pic_res = await asyncio.gather(name_task, pic_task)

        # Result Parsing
        final_data = {
            "status": "success",
            "phone": cli,
            "name": name_res.json() if name_res.status_code == 200 else "Not Found",
            "photo": pic_res.headers.get("Location") if pic_res.status_code == 302 else "No Photo"
        }

        return final_data
        
