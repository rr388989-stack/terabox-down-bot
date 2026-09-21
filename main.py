import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# --- 1. Render Port Health Check Server (Deployment fail nahi hogi) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active and running!")

def run_web_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Background mein web server start kar rahe hain
threading.Thread(target=run_web_server, daemon=True).start()
# ---------------------------------------------------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **Media Downloader Bot is Online!**\n\n"
        "Send me any link from:\n"
        "• **YouTube** (Videos / Shorts)\n"
        "• **Instagram** (Reels / Posts)\n"
        "• **Facebook, Twitter & 1000+ sites**\n\n"
        "Main turant download karke bhej dunga!"
    )

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not url.startswith("http"):
        return

    status_msg = await update.message.reply_text("📥 **Link received!** Downloading media...")

    output_template = "downloaded_%(id)s.%(ext)s"
    ydl_opts = {
        'outtmpl': output_template,
        'format': 'bestvideo+bestaudio/best/best',
        'merge_output_format': 'mp4',
        'no_warnings': True,
        'socket_timeout': 30,
    }

    downloaded_file = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)
            
            # Agar file merge hokar .mp4 bani hai
            if not os.path.exists(downloaded_file):
                base, _ = os.path.splitext(downloaded_file)
                if os.path.exists(base + '.mp4'):
                    downloaded_file = base + '.mp4'

        if downloaded_file and os.path.exists(downloaded_file):
            file_size = os.path.getsize(downloaded_file)
            if file_size > 50 * 1024 * 1024:
                await status_msg.edit_text("⚠️ File size 50MB se badi hai, Telegram bot limit cross ho rahi hai.")
            else:
                await status_msg.edit_text("📤 **Download complete!** Uploading to Telegram...")
                with open(downloaded_file, 'rb') as video_file:
                    await update.message.reply_video(video=video_file, caption=f"✅ **Downloaded Successfully!**\n🔗 {url}")
                await status_msg.delete()
        else:
            await status_msg.edit_text("❌ File download nahi ho saki.")

    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** Link unsupported, private, ya expired ho sakta hai.")
    
    finally:
        # Cleanup temporary file from server
        if downloaded_file and os.path.exists(downloaded_file):
            try:
                os.remove(downloaded_file)
            except:
                pass

def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is missing in environment variables!")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_media))
    
    print("Bot is running successfully...")
    app.run_polling()

if __name__ == '__main__':
    main()

