import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
# Yahan tum apni self-hosted Terabox Gateway API ya public API endpoint ka URL daal sakte ho
TERABOX_API_URL = "http://localhost:5000/api"  # Jaise terabox-gateway local ya cloud URL

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! Main TeraBox Downloader Bot hoon.\n"
        "Ab yeh powerful **TeraBox Gateway API** ke sath kaam karta hai, jisse cookies expire hone ki problem khatam ho gayi hai! 🚀\n\n"
        "Bas mujhe TeraBox ki link bhejo."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Check if message contains a Terabox link
    if "terabox" in text.lower() or "1024terabox" in text.lower():
        msg = await update.message.reply_text("🔄 Processing link via TeraBox Gateway API...")
        
        try:
            # API request bhej rahe hain resolve=true ke sath taaki direct download link mil jaye
            params = {
                "url": text.strip(),
                "resolve": "true"
            }
            response = requests.get(TERABOX_API_URL, params=params, timeout=30)
            data = response.json()
            
            if response.status_code == 200 and "list" in data and len(data["list"]) > 0:
                file_info = data["list"][0]
                file_name = file_info.get("filename", "Unknown")
                file_size = file_info.get("size", "Unknown")
                download_link = file_info.get("dlink") or file_info.get("link")
                
                if download_link:
                    reply_text = (
                        f"✅ **File Found Successfully!**\n\n"
                        f"📂 **Name:** `{file_name}`\n"
                        f"📦 **Size:** `{file_size}`\n\n"
                        f"📥 [Direct Download Link]({download_link})"
                    )
                    await msg.edit_text(reply_text, parse_mode="Markdown")
                else:
                    await msg.edit_text("❌ Direct download link extract nahi ho paya. Dobara try karein.")
            else:
                error_msg = data.get("error", "Unknown error occurred.")
                await msg.edit_text(f"❌ API Error: {error_msg}")
                
        except Exception as e:
            await msg.edit_text(f"⚠️ Error connecting to Terabox API: {str(e)}")
    else:
        await msg.reply_text("⚠️ Kripya ek valid TeraBox link bhejiye.")

def main():
    app = Application.Builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot is running with TeraBox API integration...")
    app.run_polling()

if __name__ == "__main__":
    main()

