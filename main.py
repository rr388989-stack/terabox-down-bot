import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
import requests
import yt_dlp
from config import API_ID, API_HASH, BOT_TOKEN, TERABOX_COOKIE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UltimateBot")

if not API_ID or not API_HASH or not BOT_TOKEN:
    logger.error("Critical Error: API credentials are missing in Environment Variables!")
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

bot = TelegramClient('ultimate_bot', API_ID, API_HASH)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply(
        "🔥 **Ultimate Media Downloader Bot is Online!**\n\n"
        "Send me links from:\n"
        "• **Terabox** (Using your Cookie & Redirect Bypass)\n"
        "• **YouTube** (Videos & Shorts)\n"
        "• **Instagram** (Reels & Posts)\n\n"
        "I will automatically process and send them to you!"
    )

@bot.on(events.NewMessage(pattern=r'https?://[^\s]+'))
async def link_handler(event):
    raw_url = event.raw_text.strip()
    
    # Check platform type
    is_terabox = any(d in raw_url.lower() for d in ["terabox", "1024tera", "freeterabox", "nephobox", "teraboxlink"])
    is_social = any(d in raw_url.lower() for d in ["youtube.com", "youtu.be", "instagram.com", "fb.watch", "facebook.com"])

    if not is_terabox and not is_social:
        return  # Kisi aur faltu link ko ignore karega

    status_msg = await event.reply("📥 **Link detected!** Processing with security bypass...")

    # Cookie file setup (Terabox ke liye mukhya roop se zaroori hai)
    cookie_file = "cookies.txt"
    cookie_value = TERABOX_COOKIE
    
    if is_terabox:
        if not cookie_value:
            await status_msg.edit("⚠️ **Error:** Terabox download ke liye Render dashboard mein `COOKIE` missing hai!")
            return
        try:
            with open(cookie_file, "w", encoding="utf-8") as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write(f".terabox.com\tTRUE\t/\tTRUE\t0\tndus\t{cookie_value}\n")
                f.write(f".1024tera.com\tTRUE\t/\tTRUE\t0\tndus\t{cookie_value}\n")
                f.write(f".teraboxlink.com\tTRUE\t/\tTRUE\t0\tndus\t{cookie_value}\n")
        except Exception as e:
            logger.error(f"Cookie write error: {e}")

    # Agar Terabox link hai, toh pehle redirect resolve karo taaki Unsupported URL error na aaye
    target_url = raw_url
    if is_terabox:
        try:
            await status_msg.edit("🔄 **Bypassing Terabox security & resolving link...**")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            res = requests.get(raw_url, headers=headers, allow_redirects=True, timeout=15)
            target_url = res.url
        except Exception as ex:
            logger.warning(f"Redirect resolution warning: {ex}")

    downloaded_file = None
    try:
        ydl_opts = {
            'outtmpl': 'downloaded_%(id)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best/best',
            'merge_output_format': 'mp4',
            'socket_timeout': 30,
            'no_warnings': True,
        }

        # Agar cookie file bani hai aur Terabox link hai toh cookie attach karo
        if is_terabox and os.path.exists(cookie_file):
            ydl_opts['cookiefile'] = cookie_file

        await status_msg.edit("⏳ **Downloading media file...** Please wait.")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=True)
            downloaded_file = ydl.prepare_filename(info)
            
            # Agar file merge hokar .mp4 bani hai
            if not os.path.exists(downloaded_file):
                base, _ = os.path.splitext(downloaded_file)
                if os.path.exists(base + '.mp4'):
                    downloaded_file = base + '.mp4'

        if downloaded_file and os.path.exists(downloaded_file):
            file_size = os.path.getsize(downloaded_file)
            # Telegram Bot API standard limit (50MB)
            if file_size > 50 * 1024 * 1024:
                await status_msg.edit("⚠️ File size 50MB se badi hai, jo Telegram Bot ki limit se zyada hai.")
            else:
                await status_msg.edit("📤 **Download complete!** Uploading to Telegram...")
                await event.client.send_file(
                    event.chat_id,
                    downloaded_file,
                    caption=f"✅ **Successfully Downloaded!**\n🔗 {raw_url}"
                )
                await status_msg.delete()
        else:
            await status_msg.edit("❌ File download nahi ho saki.")

    except Exception as e:
        logger.error(f"Download Error: {e}")
        if is_terabox:
            await status_msg.edit("❌ **Terabox Error:** Link expired, protected, ya cookie invalid ho sakti hai.")
        else:
            await status_msg.edit("❌ **Download Failed:** Link private ya unsupported ho sakta hai.")

    finally:
        # Cleanup temporary files to save space
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

def main():
    logger.info("Starting Ultimate Bot...")
    bot.start(bot_token=BOT_TOKEN)
    logger.info("Bot is running successfully!")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
