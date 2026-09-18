import logging
from telethon import TelegramClient, events
from config import API_ID, API_HASH, BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TeraboxBot")

if not API_ID or not API_HASH or not BOT_TOKEN:
    logger.error("Critical Error: API_ID, API_HASH, or BOT_TOKEN is missing in Environment Variables!")
    exit(1)

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
    bot.run_until_complete()

if __name__ == '__main__':
    main()
