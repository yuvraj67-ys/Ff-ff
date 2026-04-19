"""
NEXUS V11 - GOD LEVEL FREE FIRE API PANEL
Includes: 11+ Tools, Pure Python Protobuf Engine, AES Crypto, Async Request Blaster,
MajorLogin JWT Extractor, Outfit Generator, Ban Checker, and Advanced UI.
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import requests
import aiohttp
import asyncio
import json
import os
import time
import base64
import random
import hmac
import hashlib
import re
import traceback
from io import BytesIO
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

app = Flask(__name__)
CORS(app)
executor = ThreadPoolExecutor(max_workers=20)

# ==========================================
# 🔐 ADVANCED CORE ENCRYPTION ENGINE
# ==========================================
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'
API_KEY = "MAFU"
VERCEL_TIMEOUT = 8.0  # Safe execution limit for Vercel Free Tier

class FFCrypto:
    @staticmethod
    def encrypt(plaintext: bytes) -> bytes:
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        return cipher.encrypt(pad(plaintext, AES.block_size))

    @staticmethod
    def decrypt(ciphertext: bytes) -> bytes:
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        try:
            return unpad(cipher.decrypt(ciphertext), AES.block_size)
        except:
            return cipher.decrypt(ciphertext)

class FFProtobuf:
    """Pure Python Protobuf builder ensuring Emoji & V-Badge compatibility"""
    @staticmethod
    def encode_varint(n: int) -> bytes:
        e = []
        while True:
            byte = n & 0x7F
            n >>= 7
            if n: byte |= 0x80
            e.append(byte)
            if not n: break
        return bytes(e)

    @staticmethod
    def create_bio_payload(bio_text: str) -> bytes:
        """Flawlessly encodes Bio text (with UTF-8 emojis/colors) for UpdateSocialBasicInfo"""
        bio_bytes = bio_text.encode('utf-8')
        bio_len_varint = FFProtobuf.encode_varint(len(bio_bytes))
        # Field 2 (val 17) -> 10 11 | Field 8 (string) -> 42 | Field 9 (val 1) -> 48 01
        payload = b'\x10\x11\x42' + bio_len_varint + bio_bytes + b'\x48\x01'
        return FFCrypto.encrypt(payload)

def load_tokens(server):
    """Loads backup tokens from JSON files"""
    filename = f"token_{server.lower()}.json"
    if not os.path.exists(filename): filename = "token_ind.json"
    try:
        with open(filename, "r") as f:
            return [i["token"] for i in json.load(f) if "token" in i]
    except Exception:
        return []

# ==========================================
# 🎮 GARENA AUTHENTICATION LOGIC
# ==========================================
def fetch_access_token(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    data = {
        "uid": uid, "password": password, "response_type": "token",
        "client_type": "2", "client_id": "100067",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
    }
    r = requests.post(url, data=data, headers={"User-Agent": "GarenaMSDK/4.0.19P4"}, timeout=5)
    if r.status_code == 200:
        return r.json().get("access_token"), r.json().get("open_id")
    return None, None

def extract_jwt_via_majorlogin(access_token, open_id, region="IND"):
    try:
        payload_parts = [
            b'\x1a\x132025-08-30 05:19:21"\tfree fire(\x01:\x081.114.13B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\nATM MobilsZ\x04WIFI`\xb6\nh\xee\x05r\x03300z\x1fARMv7 VFPv3 NEON VMH | 2400 | 2\x80\x01\xc9\x0f\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f\xa2\x01\x0e105.235.139.91\xaa\x01\x02',
            b'en',
            b'\xb2\x01 1d8ec0240ede109973f3321b9354b44d\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\x10Asus ASUS_I005DA\xea\x01@afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390\xf0\x01\x01\xca\x02\nATM Mobils\xd2\x02\x04WIFI\xca\x03 7428b253defc164018c604a1ebbfebdf\xe0\x03\xa8\x81\x02\xe8\x03\xf6\xe5\x01\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xe7\xf0\x01\x88\x04\xa8\x81\x02\x90\x04\xe7\xf0\x01\x98\x04\xa8\x81\x02\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm\xe0\x04\x01\xea\x04_2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk\xf0\x04\x03\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019118692\xb2\x05\tOpenGLES2\xb8\x05\xff\x7f\xc0\x05\x04\xe0\x05\xf3F\xea\x05\x07android\xf2\x05pKqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2\xf8\x05\xfb\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"GQ@O\x00\x0e^\x00D\x06UA\x0ePM\r\x13hZ\x07T\x06\x0cm\\V\x0ejYV;\x0bU5'
        ]
        raw_payload = b''.join(payload_parts)
        raw_payload = raw_payload.replace(b'afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390', access_token.encode())
        raw_payload = raw_payload.replace(b'1d8ec0240ede109973f3321b9354b44d', open_id.encode())

        encrypted_payload = FFCrypto.encrypt(raw_payload)
        url = "https://loginbp.common.ggbluefox.com/MajorLogin" if region.upper() in ["ME", "TH"] else "https://loginbp.ggblueshark.com/MajorLogin"

        headers = {
            "Accept-Encoding": "gzip", "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "ReleaseVersion": "OB53", "X-GA": "v1 1", "X-Unity-Version": "2018.4.11f1",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; ASUS_I005DA Build/PI)"
        }

        r = requests.post(url, headers=headers, data=encrypted_payload, verify=False, timeout=10)
        if r.status_code == 200:
            response_text = r.content.decode('utf-8', errors='ignore')
            match = re.search(r'(eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)', response_text)
            if match: return match.group(1)
            
            decrypted = FFCrypto.decrypt(r.content).decode('utf-8', errors='ignore')
            match = re.search(r'(eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)', decrypted)
            if match: return match.group(1)

        return None
    except Exception as e:
        return None


# ==========================================
# 🎨 GOD-LEVEL UI (HTML + Tailwind)
# ==========================================
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS - GOD LEVEL FF PANEL</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        body { background: #0b0f19; color: #e2e8f0; font-family: 'Poppins', sans-serif; overflow-x: hidden; }
        h1, h2, h3 { font-family: 'Orbitron', sans-serif; }
        .bg-glow { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 100vw; height: 100vh; background: radial-gradient(circle, rgba(0, 243, 255, 0.05) 0%, rgba(11,15,25,1) 80%); z-index: -1; pointer-events: none; }
        .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(51, 65, 85, 0.8); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }
        .neon-text { text-shadow: 0 0 5px #0ea5e9, 0 0 10px #0ea5e9; color: #38bdf8; }
        .btn-neon { background: linear-gradient(to right, #0284c7, #0369a1); color: #fff; transition: 0.3s; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; border: none; }
        .btn-neon:hover { background: linear-gradient(to right, #0369a1, #075985); box-shadow: 0 0 15px rgba(14, 165, 233, 0.5); transform: translateY(-2px); }
        .tab-content { display: none; animation: fade 0.3s ease-in-out; }
        .tab-content.active { display: block; }
        @keyframes fade { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        #terminal { background: #000; border: 1px solid #334155; color: #4ade80; font-family: 'Consolas', monospace; height: 250px; overflow-y: auto; padding: 15px; font-size: 13px; border-radius: 0 0 8px 8px; }
        input, select, textarea { background: #0f172a; border: 1px solid #334155; color: #e2e8f0; padding: 12px; width: 100%; border-radius: 6px; outline: none; margin-bottom: 15px; transition: border-color 0.3s; }
        input:focus, select:focus, textarea:focus { border-color: #0ea5e9; box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.2); }
        .sidebar-btn { padding: 12px 16px; border-radius: 8px; text-align: left; display: flex; align-items: center; gap: 12px; transition: all 0.2s; color: #94a3b8; font-weight: 500; }
        .sidebar-btn:hover, .sidebar-btn.active-tab { background: rgba(14, 165, 233, 0.15); color: #38bdf8; border-left: 3px solid #38bdf8; }
        .icon-box { display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 8px; background: rgba(14, 165, 233, 0.1); color: #38bdf8; font-size: 1.2rem; margin-bottom: 15px; }
    </style>
</head>
<body class="flex">
    <div class="bg-glow"></div>

    <!-- Sidebar -->
    <aside class="w-20 md:w-64 glass h-screen fixed flex flex-col p-4 transition-all z-50 overflow-y-auto border-r border-slate-700">
        <h1 class="text-2xl md:text-3xl font-black text-center mb-8 neon-text hidden md:block mt-2 tracking-widest">NEXUS</h1>
        <h1 class="text-2xl font-black text-center mb-8 neon-text md:hidden mt-2"><i class="fa-solid fa-bolt"></i></h1>
        <nav class="flex flex-col gap-2">
            <button onclick="switchTab('dashboard', this)" class="sidebar-btn active-tab"><i class="fa-solid fa-chart-pie text-xl"></i> <span class="hidden md:inline">Dashboard</span></button>
            <button onclick="switchTab('player-info', this)" class="sidebar-btn"><i class="fa-solid fa-user-astronaut text-xl"></i> <span class="hidden md:inline">Player Intel</span></button>
            <button onclick="switchTab('spammer', this)" class="sidebar-btn"><i class="fa-solid fa-fire text-xl"></i> <span class="hidden md:inline">Engagement</span></button>
            <button onclick="switchTab('bio-updater', this)" class="sidebar-btn"><i class="fa-solid fa-pen-nib text-xl"></i> <span class="hidden md:inline">Bio Updater</span></button>
            <button onclick="switchTab('token-gen', this)" class="sidebar-btn"><i class="fa-solid fa-key text-xl"></i> <span class="hidden md:inline">Auth Extractor</span></button>
            <button onclick="switchTab('account-gen', this)" class="sidebar-btn"><i class="fa-solid fa-user-plus text-xl"></i> <span class="hidden md:inline">Account Maker</span></button>
            <button onclick="switchTab('ban-check', this)" class="sidebar-btn"><i class="fa-solid fa-shield-halved text-xl"></i> <span class="hidden md:inline">Ban Checker</span></button>
            <button onclick="switchTab('friend-mgr', this)" class="sidebar-btn"><i class="fa-solid fa-user-minus text-xl"></i> <span class="hidden md:inline">Friend Mgr</span></button>
            <button onclick="switchTab('tcp-bot', this)" class="sidebar-btn text-purple-400"><i class="fa-solid fa-robot text-xl"></i> <span class="hidden md:inline">VPS Bot Panel</span></button>
        </nav>
    </aside>

    <!-- Main Content -->
    <main class="ml-20 md:ml-64 w-full p-6 md:p-10 flex flex-col min-h-screen">
        
        <!-- Tab: Dashboard -->
        <div id="dashboard" class="tab-content active max-w-5xl mx-auto w-full">
            <h2 class="text-3xl mb-8 font-bold text-white border-b border-slate-700 pb-3">SYSTEM OVERVIEW</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="glass p-6 rounded-xl text-center">
                    <div class="icon-box mx-auto"><i class="fa-solid fa-server"></i></div>
                    <h3 class="text-lg text-slate-400">API Status</h3>
                    <p class="text-2xl font-bold text-green-400 mt-2">ONLINE</p>
                    <p class="text-xs text-slate-500 mt-1">Vercel Serverless</p>
                </div>
                <div class="glass p-6 rounded-xl text-center">
                    <div class="icon-box mx-auto text-pink-400 bg-pink-400/10"><i class="fa-solid fa-heart"></i></div>
                    <h3 class="text-lg text-slate-400">Auto Liker</h3>
                    <p class="text-2xl font-bold text-white mt-2">Active</p>
                    <p class="text-xs text-slate-500 mt-1">Timeout Protected</p>
                </div>
                <div class="glass p-6 rounded-xl text-center">
                    <div class="icon-box mx-auto text-purple-400 bg-purple-400/10"><i class="fa-solid fa-microchip"></i></div>
                    <h3 class="text-lg text-slate-400">Protobuf Engine</h3>
                    <p class="text-2xl font-bold text-white mt-2">v10.5</p>
                    <p class="text-xs text-slate-500 mt-1">Pure Python AES</p>
                </div>
            </div>
        </div>

        <!-- Tab: Intel & Outfit -->
        <div id="player-info" class="tab-content max-w-4xl mx-auto w-full">
            <h2 class="text-3xl mb-6 font-bold text-white border-b border-slate-700 pb-3"><i class="fa-solid fa-crosshairs text-sky-500 mr-2"></i> TARGET INTEL & OUTFIT</h2>
            <div class="glass p-8 rounded-xl">
                <label class="block text-sm text-slate-400 mb-2">Player UID</label>
                <input type="text" id="info-uid" placeholder="e.g., 123456789">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                    <button onclick="apiCall('/api/info', {uid: document.getElementById('info-uid').value})" class="btn-neon py-3 rounded-lg"><i class="fa-solid fa-database mr-2"></i> FETCH STATS</button>
                    <button onclick="fetchOutfit()" class="bg-slate-700 hover:bg-slate-600 text-white py-3 rounded-lg font-bold transition uppercase tracking-wide"><i class="fa-solid fa-image mr-2"></i> RENDER OUTFIT</button>
                </div>
                <div id="outfit-result" class="hidden text-center mt-8 p-4 bg-slate-900/50 rounded-lg border border-slate-700">
                    <p class="text-green-400 mb-3 font-mono text-sm">> OUTFIT_RENDER_SUCCESS</p>
                    <img id="outfit-img" src="" class="mx-auto rounded border border-slate-600 max-w-full shadow-lg">
                </div>
            </div>
        </div>

        <!-- Tab: Spammer -->
        <div id="spammer" class="tab-content max-w-5xl mx-auto w-full">
            <h2 class="text-3xl mb-6 font-bold text-white border-b border-slate-700 pb-3"><i class="fa-solid fa-rocket text-pink-500 mr-2"></i> MASS ENGAGEMENT</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="glass p-8 rounded-xl border-t-4 border-pink-500">
                    <div class="icon-box text-pink-500 bg-pink-500/10"><i class="fa-solid fa-heart"></i></div>
                    <h3 class="text-xl mb-4 font-bold text-white">Auto Liker</h3>
                    <label class="block text-sm text-slate-400 mb-1">Target UID</label>
                    <input type="text" id="like-uid" placeholder="UID...">
                    <label class="block text-sm text-slate-400 mb-1">Server</label>
                    <select id="like-server">
                        <option value="IND">India Server</option>
                        <option value="BD">Bangladesh Server</option>
                        <option value="BR">Brazil Server</option>
                    </select>
                    <button onclick="apiCall('/api/like', {uid: document.getElementById('like-uid').value, server: document.getElementById('like-server').value})" class="w-full bg-pink-600 hover:bg-pink-500 text-white py-3 rounded-lg transition font-bold uppercase tracking-wide mt-2">Execute Likes</button>
                </div>
                <div class="glass p-8 rounded-xl border-t-4 border-blue-500">
                    <div class="icon-box text-blue-500 bg-blue-500/10"><i class="fa-solid fa-eye"></i></div>
                    <h3 class="text-xl mb-4 font-bold text-white">Profile Visits (1000x)</h3>
                    <label class="block text-sm text-slate-400 mb-1">Target UID</label>
                    <input type="text" id="visit-uid" placeholder="UID...">
                    <label class="block text-sm text-slate-400 mb-1">Server</label>
                    <select id="visit-server">
                        <option value="IND">India Server</option>
                        <option value="BD">Bangladesh Server</option>
                    </select>
                    <button onclick="apiCall('/api/visit', {uid: document.getElementById('visit-uid').value, server: document.getElementById('visit-server').value})" class="w-full bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-lg transition font-bold uppercase tracking-wide mt-2">Execute Visits</button>
                </div>
            </div>
        </div>

        <!-- Tab: Token Gen -->
        <div id="token-gen" class="tab-content max-w-4xl mx-auto w-full">
            <h2 class="text-3xl mb-6 font-bold text-white border-b border-slate-700 pb-3"><i class="fa-solid fa-key text-yellow-500 mr-2"></i> AUTH EXTRACTOR</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="glass p-8 rounded-xl border-t-4 border-yellow-500">
                    <h3 class="text-lg mb-4 font-bold">1. Extract Access Token</h3>
                    <input type="text" id="tok-uid" placeholder="Guest UID">
                    <input type="password" id="tok-pass" placeholder="Password">
                    <button onclick="apiCall('/api/auth/token', {uid: document.getElementById('tok-uid').value, password: document.getElementById('tok-pass').value})" class="w-full bg-yellow-600 hover:bg-yellow-500 text-white py-3 rounded-lg font-bold uppercase">Get Access Token</button>
                </div>
                <div class="glass p-8 rounded-xl border-t-4 border-green-500">
                    <h3 class="text-lg mb-4 font-bold">2. Generate Game JWT</h3>
                    <input type="text" id="jwt-uid" placeholder="Guest UID">
                    <input type="password" id="jwt-pass" placeholder="Password">
                    <button onclick="apiCall('/api/auth/jwt', {uid: document.getElementById('jwt-uid').value, password: document.getElementById('jwt-pass').value})" class="w-full bg-green-600 hover:bg-green-500 text-white py-3 rounded-lg font-bold uppercase">Get JWT Token</button>
                </div>
            </div>
        </div>

        <!-- Tab: Account Maker -->
        <div id="account-gen" class="tab-content max-w-3xl mx-auto w-full">
            <h2 class="text-3xl mb-6 font-bold text-white border-b border-slate-700 pb-3"><i class="fa-solid fa-user-plus text-indigo-500 mr-2"></i> GUEST ACCOUNT MAKER</h2>
            <div class="glass p-8 rounded-xl border-t-4 border-indigo-500">
                <label class="block text-sm text-slate-400 mb-1">Prefix Name</label>
                <input type="text" id="acc-name" placeholder="e.g. BOT">
                <label class="block text-sm text-slate-400 mb-1">Server Region</label>
                <select id="acc-region">
                    <option value="IND">India (IND)</option>
                    <option value="BD">Bangladesh (BD)</option>
                    <option value="GHOST">Ghost Mode (BR)</option>
                </select>
                <button onclick="apiCall('/api/account/generate', {name: document.getElementById('acc-name').value, region: document.getElementById('acc-region').value})" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-3 rounded-lg font-bold uppercase mt-2">Create Account</button>
            </div>
        </div>

        <!-- Tab: Bio Updater -->
        <div id="bio-updater" class="tab-content max-w-3xl mx-auto w-full">
            <h2 class="text-3xl mb-6 font-bold text-white border-b border-slate-700 pb-3"><i class="fa-solid fa-pen-nib text-orange-500 mr-2"></i> LONG BIO UPDATER</h2>
            <div class="glass p-8 rounded-xl border-t-4 border-orange-500">
                <div class="bg-orange-500/10 border border-orange-500/30 p-3 rounded mb-4 text-sm text-orange-200">
                    <i class="fa-solid fa-circle-info"></i> Supports V-Badge codes, Colors [FFFF00], and Emojis perfectly!
                </div>
                <label class="block text-sm text-slate-400 mb-1">Game JWT Token (Starts with eyJ)</label>
                <input type="text" id="bio-token" placeholder="Paste JWT Token...">
                <label class="block text-sm text-slate-400 mb-1">Bio Signature Content</label>
                <textarea id="bio-text" placeholder="[b][c][FFFF00]V-Badge Text Here..." class="h-32"></textarea>
                <button onclick="apiCall('/api/bio/update', {jwt: document.getElementById('bio-token').value, bio: document.getElementById('bio-text').value})" class="w-full bg-orange-600 hover:bg-orange-500 text-white py-3 rounded-lg font-bold uppercase mt-2">Update Signature</button>
            </div>
        </div>

        <!-- Tab: Ban Check -->
        <div id="ban-check" class="tab-content max-w-3xl mx-auto w-full">
            <h2 class="text-3xl mb-6 font-bold text-white border-b border-slate-700 pb-3"><i class="fa-solid fa-shield-halved text-red-500 mr-2"></i> BAN CHECKER</h2>
            <div class="glass p-8 rounded-xl border-t-4 border-red-500">
                <label class="block text-sm text-slate-400 mb-1">Player UID</label>
                <input type="text" id="ban-uid" placeholder="Target UID to Check">
                <button onclick="apiCall('/api/bancheck', {uid: document.getElementById('ban-uid').value})" class="w-full bg-red-600 hover:bg-red-500 text-white py-3 rounded-lg font-bold uppercase mt-2">Check Ban Status</button>
            </div>
        </div>

        <!-- Tab: Friend Mgr -->
        <div id="friend-mgr" class="tab-content max-w-3xl mx-auto w-full">
            <h2 class="text-3xl mb-6 font-bold text-white border-b border-slate-700 pb-3"><i class="fa-solid fa-user-minus text-rose-500 mr-2"></i> FRIEND MANAGER</h2>
            <div class="glass p-8 rounded-xl border-t-4 border-rose-500">
                <label class="block text-sm text-slate-400 mb-1">Your JWT Token</label>
                <input type="text" id="fr-token" placeholder="JWT Token...">
                <label class="block text-sm text-slate-400 mb-1">Target UID to Remove</label>
                <input type="text" id="fr-uid" placeholder="Friend UID...">
                <button onclick="apiCall('/api/friend/remove', {jwt: document.getElementById('fr-token').value, uid: document.getElementById('fr-uid').value})" class="w-full bg-rose-600 hover:bg-rose-500 text-white py-3 rounded-lg font-bold uppercase mt-2">Remove Friend</button>
            </div>
        </div>

        <!-- Tab: TCP Bot -->
        <div id="tcp-bot" class="tab-content max-w-5xl mx-auto w-full">
            <h2 class="text-3xl mb-6 font-bold text-white border-b border-slate-700 pb-3"><i class="fa-solid fa-robot text-purple-500 mr-2"></i> REMOTE VPS BOT PANEL</h2>
            <div class="bg-slate-800 border border-slate-700 p-4 rounded-lg mb-6 text-sm text-slate-300">
                <i class="fa-solid fa-triangle-exclamation text-yellow-500 mr-2"></i> <strong>VERCEL LIMITATION:</strong> Vercel kills scripts after 10s. For 24/7 TCP Chat Bots, host your python script on a VPS (Render/Railway). These buttons act as Webhooks to trigger functions on your VPS.
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="glass p-8 rounded-xl border-t-4 border-purple-500">
                    <h3 class="text-xl mb-4 font-bold text-white">Squad Controls</h3>
                    <input type="text" id="tcp-team" placeholder="Team Code">
                    <button onclick="logTerm('> WEBHOOK: Instructing VPS to Join Team ' + document.getElementById('tcp-team').value, '#d900ff')" class="w-full bg-purple-600 hover:bg-purple-500 text-white py-3 rounded-lg font-bold uppercase mb-3">JOIN SQUAD</button>
                    <button onclick="logTerm('> WEBHOOK: Sent Emote Command', '#d900ff')" class="w-full bg-slate-700 hover:bg-slate-600 text-white py-3 rounded-lg font-bold uppercase">PLAY EVO EMOTES</button>
                </div>
                <div class="glass p-8 rounded-xl border-t-4 border-red-500">
                    <h3 class="text-xl mb-4 font-bold text-white">Lag Attack</h3>
                    <input type="text" id="tcp-room" placeholder="Room ID">
                    <button onclick="logTerm('> WEBHOOK: Initiating High-Velocity Lag Attack on Room', '#f00')" class="w-full bg-red-600 hover:bg-red-500 text-white py-3 rounded-lg font-bold uppercase">EXECUTE LAG ATTACK</button>
                </div>
            </div>
        </div>

        <!-- Terminal Console -->
        <div class="mt-auto pt-10 w-full max-w-5xl mx-auto">
            <div class="flex justify-between items-center bg-slate-900 px-4 py-3 rounded-t-lg border border-slate-700 border-b-0">
                <span class="text-slate-400 text-xs font-bold tracking-widest"><i class="fa-solid fa-terminal mr-2"></i>NEXUS_TERMINAL</span>
                <button onclick="document.getElementById('terminal').innerHTML=''" class="text-slate-500 hover:text-white transition"><i class="fa-solid fa-trash"></i></button>
            </div>
            <div id="terminal" class="rounded-b-lg">
                <div class="text-sky-400">> SYSTEM INITIALIZED. ALL MODULES LOADED.</div>
            </div>
        </div>
    </main>

    <script>
        function logTerm(msg, color="#4ade80") {
            const term = document.getElementById('terminal');
            const time = new Date().toLocaleTimeString();
            term.innerHTML += `<div style="color:${color}; margin-top:4px; border-left: 2px solid ${color}; padding-left: 8px;">[${time}] ${msg}</div>`;
            term.scrollTop = term.scrollHeight;
        }

        function switchTab(tabId, btn) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.sidebar-btn').forEach(b => b.classList.remove('active-tab'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active-tab');
            logTerm(`> Module active: ${tabId.toUpperCase()}`, '#94a3b8');
        }

        function fetchOutfit() {
            const uid = document.getElementById('info-uid').value;
            if(!uid) return logTerm('> ERROR: Target UID required.', '#ef4444');
            logTerm(`> Compiling 3D Outfit Matrix for UID: ${uid}...`, '#38bdf8');
            document.getElementById('outfit-result').classList.remove('hidden');
            document.getElementById('outfit-img').src = `/api/outfit?uid=${uid}&key=MAFU&t=${Date.now()}`;
        }

        async function apiCall(endpoint, payload) {
            logTerm(`> POST ${endpoint} - Payload: ${JSON.stringify(payload)}`, '#facc15');
            Swal.fire({title: 'Executing...', background:'#0f172a', color:'#38bdf8', didOpen: () => Swal.showLoading()});
            
            try {
                const query = new URLSearchParams(payload).toString();
                let res = await fetch(`${endpoint}?${query}`);
                let data = await res.json();
                Swal.close();
                
                if(!res.ok || data.error) {
                    logTerm(`> FAILED: ${data.error || JSON.stringify(data)}`, '#ef4444');
                    Swal.fire({title: 'Error', text: data.error || 'Request failed', icon: 'error', background: '#0f172a', color: '#fff'});
                    return;
                }
                
                logTerm(`> SUCCESS: \n${JSON.stringify(data, null, 2)}`, '#4ade80');
            } catch(e) {
                Swal.close();
                logTerm(`> CRASH: ${e.message}`, '#ef4444');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_UI)

# ==========================================
# 1. PLAYER INTEL
# ==========================================
@app.route('/api/info', methods=['GET'])
def api_info():
    uid = request.args.get('uid')
    if not uid: return jsonify({"error": "UID required"}), 400
    try:
        r = requests.get(f"https://mafuuuu-info-api.vercel.app/mafu-info?uid={uid}", timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# 2. OUTFIT GENERATOR (Bulletproof)
# ==========================================
@app.route('/api/outfit', methods=['GET'])
def api_outfit():
    uid = request.args.get('uid')
    if request.args.get('key') != API_KEY: return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        resp = requests.get(f"https://mafuuuu-info-api.vercel.app/mafu-info?uid={uid}", timeout=8)
        player_data = resp.json()

        if "profileInfo" in player_data and "clothes" in player_data["profileInfo"]:
            outfit_ids = player_data["profileInfo"]["clothes"]
        else:
            outfit_ids = player_data.get("AccountProfileInfo", {}).get("EquippedOutfit", []) or []

        required_starts = ["211", "214", "211", "203", "204", "205", "203"]
        fallback_ids = ["211000000", "214000000", "208000000", "203000000", "204000000", "205000000", "212000000"]
        used_ids = set()

        def fetch_image(idx, code):
            matched = fallback_ids[idx]
            for oid in outfit_ids:
                if str(oid).startswith(code) and str(oid) not in used_ids:
                    matched = str(oid)
                    used_ids.add(str(oid))
                    break
            try:
                r = requests.get(f'https://iconapi.wasmer.app/{matched}', timeout=4)
                if r.status_code == 200:
                    return Image.open(BytesIO(r.content)).convert("RGBA").resize((150, 150), Image.LANCZOS)
            except: pass
            return Image.new("RGBA", (150, 150), (0,0,0,0)) 

        futures = [executor.submit(fetch_image, idx, code) for idx, code in enumerate(required_starts)]
        
        bg_path = os.path.join(os.path.dirname(__file__), "outfit.png")
        if os.path.exists(bg_path): canvas = Image.open(bg_path).convert("RGBA")
        else:
            canvas = Image.new("RGBA", (800, 800), (30, 30, 40, 255))
            ImageDraw.Draw(canvas).rectangle([50, 50, 750, 750], outline=(0, 243, 255, 100), width=4)

        positions = [(350, 30), (575, 130), (665, 350), (575, 550), (350, 654), (135, 570), (135, 130)]
        cw, ch = canvas.size
        for idx, future in enumerate(futures):
            part = future.result()
            px, py = positions[idx]
            if px < cw and py < ch: 
                canvas.paste(part, (px, py), part)

        output = BytesIO()
        canvas.save(output, format='PNG')
        output.seek(0)
        return send_file(output, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==========================================
# 3 & 4. ENGAGEMENT SPAMMERS (Vercel Safe)
# ==========================================
async def blast_request(session, url, token, payload):
    headers = {
        'User-Agent': "Dalvik/2.1.0", 'Authorization': f"Bearer {token}",
        'Content-Type': "application/x-www-form-urlencoded", 'ReleaseVersion': "OB53", 'X-Unity-Version': "2018.4.11f1"
    }
    try:
        async with session.post(url, data=payload, headers=headers, ssl=False) as resp:
            return resp.status == 200
    except: return False

@app.route('/api/like', methods=['GET'])
def api_like():
    uid = request.args.get("uid")
    server = request.args.get("server", "IND").upper()
    tokens = load_tokens(server)
    if not tokens: return jsonify({"error": f"No tokens for {server}"}), 404

    try:
        uid_v = enc_uid(uid)
        reg_hex = server.encode().hex()
        payload = bytes.fromhex(f"08{uid_v}12{len(server):02x}{reg_hex}")
        enc_payload = FFCrypto.encrypt(payload)
    except Exception as e: return jsonify({"error": str(e)}), 500

    url = "https://client.ind.freefiremobile.com/LikeProfile" if server == "IND" else "https://client.us.freefiremobile.com/LikeProfile"

    async def run():
        start = time.time()
        success = 0
        async with aiohttp.ClientSession() as session:
            tasks = [blast_request(session, url, tk, enc_payload) for tk in tokens[:100]]
            for coro in asyncio.as_completed(tasks):
                if time.time() - start > VERCEL_TIMEOUT: break
                if await coro: success += 1
        return success

    return jsonify({"uid": uid, "likes_sent": asyncio.run(run())})

@app.route('/api/visit', methods=['GET'])
def api_visit():
    uid = request.args.get('uid')
    server = request.args.get('server', 'IND').upper()
    tokens = load_tokens(server)
    if not tokens: return jsonify({"error": "No tokens"}), 404

    try:
        payload = bytes.fromhex(f"08{enc_uid(uid)}1007") 
        enc_payload = FFCrypto.encrypt(payload)
    except Exception as e: return jsonify({"error": str(e)}), 500

    url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow" if server == "IND" else "https://client.us.freefiremobile.com/GetPlayerPersonalShow"
    
    async def run():
        start = time.time()
        success = 0
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=200)) as session:
            tasks = [blast_request(session, url, tokens[i % len(tokens)], enc_payload) for i in range(1000)]
            for coro in asyncio.as_completed(tasks):
                if time.time() - start > VERCEL_TIMEOUT: break
                if await coro: success += 1
        return success

    return jsonify({"uid": uid, "visits_sent": asyncio.run(run()), "note": "Vercel timeout enforced"})

# ==========================================
# 5 & 6. OAUTH & GAME JWT EXTRACTOR
# ==========================================
@app.route('/api/auth/token', methods=['GET'])
def api_auth_token():
    uid = request.args.get('uid')
    pwd = request.args.get('password')
    acc, opn = fetch_access_token(uid, pwd)
    if acc: return jsonify({"access_token": acc, "open_id": opn})
    return jsonify({"error": "Failed to get access token"}), 401

@app.route('/api/auth/jwt', methods=['GET'])
def api_auth_jwt():
    uid = request.args.get('uid')
    pwd = request.args.get('password')
    acc, opn = fetch_access_token(uid, pwd)
    if not acc: return jsonify({"error": "Invalid Credentials"}), 401

    jwt_token = extract_jwt_via_majorlogin(acc, opn)
    if jwt_token:
        return jsonify({"status": "success", "jwt_token": jwt_token, "access_token": acc})
    return jsonify({"error": "MajorLogin failed. Account may be banned or wrong server."}), 500

# ==========================================
# 7. ACCOUNT MAKER
# ==========================================
@app.route('/api/account/generate', methods=['GET'])
def api_account_gen():
    name_prefix = request.args.get('name', 'NEXUS')
    try:
        password = f"NEXUS-{random.randint(1000,9999)}X"
        data = f"password={password}&client_type=2&source=2&app_id=100067"
        sig = hmac.new(b"32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533", data.encode(), hashlib.sha256).hexdigest()
        
        r = requests.post("https://100067.connect.garena.com/oauth/guest/register", data=data, headers={"Authorization": "Signature " + sig}, timeout=5)
        uid = r.json().get('uid')
        if not uid: return jsonify({"error": "Registration Failed"}), 400
        return jsonify({"success": True, "uid": uid, "password": password})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# 8. BIO UPDATER (Pure Python Protobuf)
# ==========================================
@app.route('/api/bio/update', methods=['GET'])
def api_bio():
    jwt_tok = request.args.get('jwt')
    bio = request.args.get('bio')
    if not jwt_tok or not bio: return jsonify({"error": "JWT and Bio required"}), 400
    try:
        # PURE PYTHON PROTOBUF ENCODING
        enc_payload = FFProtobuf.create_bio_payload(bio)
        
        r = requests.post("https://clientbp.ggblueshark.com/UpdateSocialBasicInfo", data=enc_payload, headers={"Authorization": f"Bearer {jwt_tok}", "ReleaseVersion":"OB53"}, verify=False, timeout=5)
        return jsonify({"status": r.status_code, "msg": "Bio updated successfully!" if r.status_code==200 else "Update failed"})
    except Exception as e: return jsonify({"error": str(e)}), 500

# ==========================================
# 9. FRIEND REMOVER
# ==========================================
@app.route('/api/friend/remove', methods=['GET'])
def api_friend_del():
    jwt_tok = request.args.get('jwt')
    uid = request.args.get('uid')
    if not jwt_tok or not uid: return jsonify({"error": "JWT and Target UID required"}), 400
    try:
        payload = bytes.fromhex(f"08a7c4839f1e10{enc_uid(uid)}")
        enc = FFCrypto.encrypt(payload)
        r = requests.post("https://clientbp.ggblueshark.com/RemoveFriend", data=enc, headers={"Authorization": f"Bearer {jwt_tok}", "ReleaseVersion":"OB53"}, verify=False, timeout=5)
        return jsonify({"status": r.status_code, "msg": "Friend removed!" if r.status_code==200 else "Failed"})
    except Exception as e: return jsonify({"error": str(e)}), 500

# ==========================================
# 10. BAN CHECKER
# ==========================================
@app.route('/api/bancheck', methods=['GET'])
def api_bancheck():
    uid = request.args.get('uid')
    if not uid: return jsonify({"error": "UID required"}), 400
    try:
        url = f'https://ff.garena.com/api/antihack/check_banned?lang=en&uid={uid}'
        headers = {'User-Agent': 'Mozilla/5.0', 'x-requested-with': 'B6FksShzIgjfrYImLpTsadjS86sddhFH'}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "success":
                is_banned = data["data"].get("is_banned", 0)
                period = data["data"].get("period", 0)
                msg = f"Banned for {period} months" if period > 0 else "Banned indefinitely" if is_banned else "Not banned"
                return jsonify({"uid": uid, "status": "banned" if is_banned else "safe", "message": msg, "raw": data})
        return jsonify({"error": "Failed to retrieve status"}), 500
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
