from fastapi import FastAPI, Header, HTTPException
import httpx

app = FastAPI(title="CSINT Eyecon API")

# 🔑 HARD-CODED API KEY
API_KEY = "@CSINT"

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "E-Auth-V": "e1",
    "E-Auth": "dd2bc3e8-0f11-40c2-9bc2-81bcd862baf5",
    "E-Auth-C": "34",
    "E-Auth-K": "PgdtSBeR0MumR7fO",
    "Accept-Encoding": "gzip, deflate, br"
}

def verify_key(key: str):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


@app.get("/")
def home():
    return {"status": "CSINT API running"}


@app.get("/lookup")
async def lookup(cli: str, x_api_key: str = Header(...)):
    verify_key(x_api_key)

    async with httpx.AsyncClient(http2=True, follow_redirects=False) as client:

        # 🔹 1️⃣ Try getting picture first
        pic_params = {
            "cli": cli,
            "size": "small",
            "type": "0",
            "src": "HISTORY"
        }

        pic_resp = await client.get(
            "https://api.eyecon-app.com/app/pic",
            headers=BASE_HEADERS,
            params=pic_params
        )

        if pic_resp.status_code == 302 and "Location" in pic_resp.headers:
            return {
                "cli": cli,
                "type": "picture",
                "image_url": pic_resp.headers["Location"]
            }

        # 🔹 2️⃣ If pic not found → get name
        name_params = {
            "cli": cli,
            "lang": "en",
            "is_callerid": "true",
            "is_ic": "true",
            "source": "HISTORY"
        }

        name_resp = await client.get(
            "https://api.eyecon-app.com/app/getnames.jsp",
            headers=BASE_HEADERS,
            params=name_params
        )

        return {
            "cli": cli,
            "type": "name",
            "response": name_resp.text
        }
