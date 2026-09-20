import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
import yt_dlp
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

# Background server taaki Render ka timeout error na aaye
threading.Thread(target=run_web_server, daemon=True).start()
# ---------------------------------------------------

bot = TelegramClient('terabox_bot', API_ID, API_HASH)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply(
        "👋 **Welcome to Terabox Downloader Bot!**\n\n"
        "Send me any Terabox link, and I will download and send the video to you!"
    )

@bot.on(events.NewMessage(pattern=r'https?://[^\s]+'))
async def link_handler(event):
    url = event.raw_text.strip()
    # Terabox ya uske alternative domains check karne ke liye
    if any(domain in url.lower() for domain in ["terabox", "1024tera", "freeterabox", "nephobox"]):
        status_msg = await event.reply("📥 **Terabox link received!** Downloading video using your Cookie...")
        
        cookie_value = TERABOX_COOKIE
        if not cookie_value:
            await status_msg.edit("⚠️ **Error:** `COOKIE` environment variable is missing in Render dashboard!")
            return

        # Cookie file create kar rahe hain yt-dlp ke liye
        cookie_file = "cookies.txt"
        with open(cookie_file, "w") as f:
            f.write(f"# Netscape HTTP Cookie File\n.terabox.com\tTRUE\t/\tTRUE\t0\tndus\t{cookie_value}\n")
            f.write(f".1024tera.com\tTRUE\t/\tTRUE\t0\tndus\t{cookie_value}\n")

        downloaded_file = None
        try:
            ydl_opts = {
                'cookiefile': cookie_file,
                'outtmpl': '%(id)s.%(ext)s',
                'format': 'best',
            }

            # Video download process
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)

            if downloaded_file and os.path.exists(downloaded_file):
                await status_msg.edit("📤 **Download complete!** Uploading video to Telegram...")
                await event.client.send_file(
                    event.chat_id,
                    downloaded_file,
                    caption=f"✅ **Here is your video!**\n🔗 {url}"
                )
                await status_msg.delete()
            else:
                await status_msg.edit("❌ Failed to fetch the video file from this link.")

        except Exception as e:
            logger.error(f"Download Error: {e}")
            await status_msg.edit(f"❌ **Download Failed:** Link expired ya protected ho sakta hai.")

        finally:
            # Server space clean rakhne ke liye files delete kar rahe hain
            if downloaded_file and os.path.exists(downloaded_file):
                try:
                    os.remove(downloaded_file)
                except:
                    pass
            if os.path.exists(cookie_file):
                try:
                    os.remove(cookie_file)
                except:
                    pass
    else:
        pass

def main():
    logger.info("Starting Telegram Bot...")
    bot.start(bot_token=BOT_TOKEN)
    logger.info("Bot is running successfully!")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
