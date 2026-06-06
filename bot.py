# bot.py

import asyncio
import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import random

try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from pyrogram import Client
import config

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Download Movie</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {{
            background-color: #0f0f12;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            text-align: center;
            padding: 15px;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 90vh;
        }}
        .container {{
            width: 100%;
            max-width: 400px;
            background: rgba(30, 30, 38, 0.75);
            padding: 30px 20px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        }}
        h2 {{ 
            color: #ff0055; 
            margin-bottom: 5px; 
            font-size: 26px; 
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(255, 0, 85, 0.3);
        }}
        .movie-title {{ 
            font-size: 16px; 
            color: #00ff88; 
            margin-bottom: 25px; 
            font-weight: bold;
            background: rgba(0, 255, 136, 0.1);
            padding: 10px;
            border-radius: 8px;
            border: 1px solid rgba(0, 255, 136, 0.2);
        }}
        .step-card {{
            background: rgba(255, 255, 255, 0.04);
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 25px;
            font-size: 14px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.05);
            color: #d1d5db;
        }}
        .btn {{
            display: block;
            width: 100%;
            padding: 16px 0;
            margin: 15px 0;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.3s ease;
        }}
        .btn-ad {{
            background: linear-gradient(135deg, #ff0055, #b3003b);
            color: white;
            box-shadow: 0 4px 15px rgba(255, 0, 85, 0.4);
        }}
        .btn-ad:hover {{ 
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 0, 85, 0.6);
        }}
        .btn-download {{
            background-color: #1f2937;
            color: #4b5563;
            border: 1px solid #374151;
            pointer-events: none;
        }}
        .btn-download.active {{
            background: linear-gradient(135deg, #00ff88, #009951);
            color: #000000;
            font-weight: 800;
            pointer-events: auto;
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
            border: none;
        }}
        .success-badge {{
            display: none;
            background: rgba(0, 255, 136, 0.1);
            color: #00ff88;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 14px;
            border: 1px solid rgba(0, 255, 136, 0.2);
            margin-bottom: 15px;
        }}
    </style>
    <script>
        let tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();

        function unlockDownload() {{
            window.open("{ad_link}", "_blank");
            
            document.getElementById("btn-ad").style.display = "none";
            document.getElementById("success-badge").style.display = "block";
            
            var downloadBtn = document.getElementById("download-btn");
            downloadBtn.classList.add("active");
            downloadBtn.innerText = "⚡️ Get Movie File";
            document.getElementById("step-text").innerText = "লিংকটি সচল হয়েছে! নিচের বাটনে চাপ দিন।";
        }}

        function getMovie() {{
            tg.openTelegramLink("https://t.me/{bot_username}?start={file_db_id}");
            setTimeout(function() {{
                tg.close();
            }}, 500);
        }}
    </script>
</head>
<body>
    <div class="container">
        <h2>CTG PREMIUM SEARCH</h2>
        <div class="movie-title">🍿 Your Requested Movie is Ready!</div>
        
        <div id="step-text" class="step-card">
            নিচের লাল বাটনে ক্লিক করে ফাইল ডাউনলোডের লিংকটি আনলক করুন।
        </div>
        
        <div id="success-badge" class="success-badge">✅ Link Unlocked successfully!</div>
        
        <button id="btn-ad" class="btn btn-ad" onclick="unlockDownload()">🔓 Unlock Download Link</button>
        
        <button id="download-btn" class="btn btn-download" onclick="getMovie()">🔒 Locked</button>
    </div>
</body>
</html>
"""

class DummyWebServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/download":
            query_params = parse_qs(parsed_url.query)
            file_db_id = query_params.get("id", [""])[0]
            
            ad_link = random.choice(config.DIRECT_AD_LINKS)
            
            response_html = HTML_TEMPLATE.format(
                file_db_id=file_db_id,
                bot_username=config.BOT_USERNAME,
                ad_link=ad_link
            )
            
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(response_html.encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"CTG Movie Bot is running alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyWebServer)
    print(f"ওয়েব সার্ভার এবং মিনি অ্যাপ পোর্ট {port}-এ চালু হয়েছে।")
    server.forever = server.serve_forever() # For older compatibility

# Daemon Thread-এ সার্ভার সচল করা
t = threading.Thread(target=run_web_server, daemon=True)
t.start()

plugins = dict(root="plugins")

app = Client(
    "movie_search_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=plugins
)

if __name__ == "__main__":
    print("অভিনন্দন! আপনার মুভি বটটি সফলভাবে চালু হয়েছে।")
    app.run()
