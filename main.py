import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from config import API_ID, API_HASH, BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TeraboxBot")

if not API_ID or not API_HASH or not BOT_TOKEN:
    logger.error("Critical Error: API_ID, API_HASH, or BOT_TOKEN is missing in Environment Variables!")
    exit(1)

# --- Render Port Check ke liye Dummy HTTP Server ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_web_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Dummy web server started on port {port}")
    server.serve_forever()

# Server ko background thread mein chala rahe hain taaki Render ka port timeout fix ho jaye
threading.Thread(target=run_web_server, daemon=True).start()
# ---------------------------------------------------

# Telethon Bot Client initialize kar rahe hain
bot = TelegramClient('terabox_bot', API_ID, API_HASH)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply(
        "👋 **Welcome to Terabox Downloader Bot!**\n\n"
        "Send me any public or private Terabox link, and I will process it for you."
    )

@bot.on(events.NewMessage(pattern=r'https?://[^\s]+'))
async def link_handler(event):
    url = event.raw_text.strip()
    if "terabox" in url.lower():
        await event.reply("📥 **Terabox link received!** Processing your download request...")
        
        # Yahan aap apna Terabox API download logic ya script jodh sakte hain
        
    else:
        await event.reply("⚠️ Please send a valid Terabox link.")

def main():
    logger.info("Starting Telegram Bot...")
    bot.start(bot_token=BOT_TOKEN)
    logger.info("Bot is running successfully!")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
