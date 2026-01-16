from fastapi import FastAPI, Header, HTTPException
import httpx

app = FastAPI(title="CSINT Eyecon API")

# 🔑 HARD-CODED API KEY
API_KEY = "@CSINT"

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "E-Auth-V": "e1",
    "E-Auth": "dd2bc3e8-0f11-40c2-9bc2-81bcd862baf5",
    "E-Auth-C": "34",
    "E-Auth-K": "PgdtSBeR0MumR7fO",
    "Accept-Encoding": "gzip, deflate, br"
}

def check_key(key: str):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.get("/getnames")
async def get_names(cli: str, x_api_key: str = Header(...)):
    check_key(x_api_key)

    params = {
        "cli": cli,
        "lang": "en",
        "is_callerid": "true",
        "is_ic": "true",
        "source": "HISTORY"
    }

    async with httpx.AsyncClient(http2=True) as client:
        r = await client.get(
            "https://api.eyecon-app.com/app/getnames.jsp",
            headers=BASE_HEADERS,
            params=params
        )

    return {
        "status": r.status_code,
        "data": r.text
    }


@app.get("/getpic")
async def get_pic(cli: str, x_api_key: str = Header(...)):
    check_key(x_api_key)

    params = {
        "cli": cli,
        "size": "small",
        "type": "0",
        "src": "HISTORY"
    }

    async with httpx.AsyncClient(http2=True, follow_redirects=False) as client:
        r = await client.get(
            "https://api.eyecon-app.com/app/pic",
            headers=BASE_HEADERS,
            params=params
        )

    return {
        "status": r.status_code,
        "image_url": r.headers.get("Location")
    }
