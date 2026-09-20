import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
import requests
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

threading.Thread(target=run_web_server, daemon=True).start()
# ---------------------------------------------------

bot = TelegramClient('terabox_bot', API_ID, API_HASH)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply(
        "👋 **Terabox Downloader Bot is Online!**\n\n"
        "Send me any Terabox link, and I will process and download it for you."
    )

@bot.on(events.NewMessage(pattern=r'https?://[^\s]+'))
async def link_handler(event):
    raw_url = event.raw_text.strip()
    
    # Terabox aur uske saare alternative/redirect domains ko match karne ke liye
    domains = ["terabox", "1024tera", "freeterabox", "nephobox", "teraboxlink"]
    if any(d in raw_url.lower() for d in domains):
        status_msg = await event.reply("📥 **Link received!** Resolving and downloading via your Cookie...")
        
        cookie_value = TERABOX_COOKIE
        if not cookie_value:
            await status_msg.edit("⚠️ **Error:** `COOKIE` environment variable is missing in Render dashboard!")
            return

        # Netscape Cookie File creation for all potential Terabox domains
        cookie_file = "cookies.txt"
        try:
            with open(cookie_file, "w", encoding="utf-8") as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write(f".terabox.com\tTRUE\t/\tTRUE\t0\tndus\t{cookie_value}\n")
                f.write(f".1024tera.com\tTRUE\t/\tTRUE\t0\tndus\t{cookie_value}\n")
                f.write(f".teraboxlink.com\tTRUE\t/\tTRUE\t0\tndus\t{cookie_value}\n")
        except Exception as e:
            logger.error(f"Cookie file write error: {e}")

        # Step 1: Resolve short/redirect URLs (jaise dm.1024tera.com)
        resolved_url = raw_url
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(raw_url, headers=headers, allow_redirects=True, timeout=12)
            resolved_url = response.url
        except Exception as ex:
            logger.warning(f"Redirect resolution warning, falling back to raw URL: {ex}")

        downloaded_file = None
        try:
            ydl_opts = {
                'cookiefile': cookie_file,
                'outtmpl': 'downloaded_%(id)s.%(ext)s',
                'format': 'best',
                'socket_timeout': 30,
                'no_warnings': True,
                'ignoreerrors': False
            }

            # Step 2: Extract and Download file using yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(resolved_url, download=True)
                downloaded_file = ydl.prepare_filename(info)

            if downloaded_file and os.path.exists(downloaded_file):
                file_size = os.path.getsize(downloaded_file)
                # Telegram bot file size limit check (approx 50MB for standard bot API)
                if file_size > 50 * 1024 * 1024:
                    await status_msg.edit("⚠️ File size 50MB se badi hai, jo Telegram Bot API limits se exceed ho rahi hai.")
                else:
                    await status_msg.edit("📤 **Download complete!** Uploading video to Telegram...")
                    await event.client.send_file(
                        event.chat_id,
                        downloaded_file,
                        caption=f"✅ **Here is your video!**\n🔗 {raw_url}"
                    )
                    await status_msg.delete()
            else:
                await status_msg.edit("❌ File download nahi ho saki. Link expired ya protected ho sakta hai.")

        except yt_dlp.utils.DownloadError as de:
            logger.error(f"yt-dlp Download Error: {de}")
            await status_msg.edit("❌ **Download Failed:** Link unsupported hai ya Terabox ne access block kar diya hai.")
        except Exception as e:
            logger.error(f"Unexpected Error: {e}")
            await status_msg.edit("❌ **Error:** Link process karte waqt ek unexpected error aaya.")

        finally:
            # Cleanup temporary files to save server memory/storage
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
