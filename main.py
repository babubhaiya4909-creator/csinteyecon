import httpx
import asyncio
from fastapi import FastAPI, Query
import re

app = FastAPI()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "E-Auth-V": "e1",
    "E-Auth": "dd2bc3e8-0f11-40c2-9bc2-81bcd862baf5",
    "E-Auth-C": "34",
    "E-Auth-K": "PgdtSBeR0MumR7fO",
}

def extract_details(url):
    """URL se Account aur ID nikalne ka logic"""
    account = "Unknown"
    uid = "Not Found"
    
    # Facebook Graph/Profile logic
    if "facebook.com" in url or "fbcdn.net" in url:
        account = "facebook.com"
        # Multiple regex patterns for FB IDs
        match = re.search(r'facebook\.com/(\d+)/|/(\d+)_|profile\.php\?id=(\d+)', url)
        if match:
            # Jo bhi group match kare, wo ID hai
            uid = next(g for g in match.groups() if g is not None)
            
    elif "whatsapp.net" in url:
        account = "whatsapp.net"
        match = re.search(r'/([\d-]+)@', url)
        if match:
            uid = match.group(1)
            
    return account, uid

@app.get("/lookup")
async def lookup(cli: str = Query(..., description="Phone number")):
    try:
        async with httpx.AsyncClient(http2=True, timeout=12.0) as client:
            n_task = client.get("https://api.eyecon-app.com/app/getnames.jsp", 
                                params={"cli": cli, "lang": "en", "is_callerid": "true", "cv": "vc_729_vn_4.2026.01.13.0939_a", "source": "HISTORY"}, 
                                headers=HEADERS)
            
            p_task = client.get("https://api.eyecon-app.com/app/pic", 
                                params={"cli": cli, "is_callerid": "true", "size": "big", "type": "0", "cv": "vc_729_vn_4.2026.01.13.0939_a"}, 
                                headers=HEADERS, follow_redirects=False)

            n_res, p_res = await asyncio.gather(n_task, p_task)

            name = n_res.text.strip() if n_res.status_code == 200 else "Not Found"
            photo = p_res.headers.get("Location", "No Photo")
            
            acc_type, account_id = extract_details(photo)

            # Response base structure
            response_data = {
                "status": "success",
                "name": name,
                "photo": photo,
                "Account": acc_type,
                "Id": account_id
            }

            # 🔥 Facebook ID Found Block
            if acc_type == "facebook.com" and account_id != "Not Found":
                response_data["facebook_info"] = {
                    "found": True,
                    "profile_url": f"https://www.facebook.com/profile.php?id={account_id}",
                    "direct_link": f"fb://profile/{account_id}" # Mobile app direct link
                }
            else:
                response_data["facebook_info"] = {"found": False}

            return response_data
            
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
