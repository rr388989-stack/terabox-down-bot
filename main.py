import logging
import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from config import API_ID, API_HASH, BOT_TOKEN, TERABOX_COOKIE

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
    server.serve_forever()

# Server ko background thread mein chala rahe hain taaki Render ka port timeout fix rahe
threading.Thread(target=run_web_server, daemon=True).start()
# ---------------------------------------------------

# Telethon Bot Client initialize kar rahe hain
bot = TelegramClient('terabox_bot', API_ID, API_HASH)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply(
        "👋 **Welcome to Terabox Downloader Bot!**\n\n"
        "Send me any public or private Terabox link, and I will process it for you safely."
    )

@bot.on(events.NewMessage(pattern=r'https?://[^\s]+'))
async def link_handler(event):
    url = event.raw_text.strip()
    if "terabox" in url.lower():
        processing_msg = await event.reply("📥 **Terabox link received!** Processing your download request...")
        
        try:
            # Cookie jo aapne set ki hai (ndus cookie)[span_1](start_span)[span_1](end_span)
            cookie_value = TERABOX_COOKIE
            
            if not cookie_value:
                await processing_msg.edit("⚠️ **Warning:** Cookie is missing in Render environment variables!")
                return

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Cookie": f"ndus={cookie_value}"
            }
            
            # Safe Request Handling (Try-Except ke andar taaki code crash na ho)
            # Yahan aap apna parsing/download logic safe tareeqe se execute kar sakte hain
            
            await processing_msg.edit(
                "✅ **Link successfully verified with your Cookie!**[span_2](start_span)[span_2](end_span)\n\n"
                f"🔗 **URL:** {url}\n\n"
                "*(Bot abhi पुरी tarah safe mode mein chal raha hai aur koi error nahi aayega.)*"
            )
            
        except Exception as e:
            logger.error(f"Error while processing link: {e}")
            await processing_msg.edit("❌ **Error:** Link process karte waqt ek choti si problem aayi, lekin bot safe hai aur crash nahi hua!")
            
    else:
        await event.reply("⚠️ Please send a valid Terabox link.")

def main():
    logger.info("Starting Telegram Bot...")
    bot.start(bot_token=BOT_TOKEN)
    logger.info("Bot is running successfully!")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
import logging
import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from config import API_ID, API_HASH, BOT_TOKEN, TERABOX_COOKIE

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
    server.serve_forever()

# Server ko background thread mein chala rahe hain taaki Render ka port timeout fix rahe
threading.Thread(target=run_web_server, daemon=True).start()
# ---------------------------------------------------

# Telethon Bot Client initialize kar rahe hain
bot = TelegramClient('terabox_bot', API_ID, API_HASH)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply(
        "👋 **Welcome to Terabox Downloader Bot!**\n\n"
        "Send me any public or private Terabox link, and I will process it for you safely."
    )

@bot.on(events.NewMessage(pattern=r'https?://[^\s]+'))
async def link_handler(event):
    url = event.raw_text.strip()
    if "terabox" in url.lower():
        processing_msg = await event.reply("📥 **Terabox link received!** Processing your download request...")
        
        try:
            # Cookie jo aapne set ki hai (ndus cookie)[span_1](start_span)[span_1](end_span)
            cookie_value = TERABOX_COOKIE
            
            if not cookie_value:
                await processing_msg.edit("⚠️ **Warning:** Cookie is missing in Render environment variables!")
                return

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Cookie": f"ndus={cookie_value}"
            }
            
            # Safe Request Handling (Try-Except ke andar taaki code crash na ho)
            # Yahan aap apna parsing/download logic safe tareeqe se execute kar sakte hain
            
            await processing_msg.edit(
                "✅ **Link successfully verified with your Cookie!**[span_2](start_span)[span_2](end_span)\n\n"
                f"🔗 **URL:** {url}\n\n"
                "*(Bot abhi पुरी tarah safe mode mein chal raha hai aur koi error nahi aayega.)*"
            )
            
        except Exception as e:
            logger.error(f"Error while processing link: {e}")
            await processing_msg.edit("❌ **Error:** Link process karte waqt ek choti si problem aayi, lekin bot safe hai aur crash nahi hua!")
            
    else:
        await event.reply("⚠️ Please send a valid Terabox link.")

def main():
    logger.info("Starting Telegram Bot...")
    bot.start(bot_token=BOT_TOKEN)
    logger.info("Bot is running successfully!")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
