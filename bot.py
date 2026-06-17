import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ===== APNI DETAILS YAHAN BHARO =====
BOT_TOKEN = "8935637388:AAFrm5jfRNISj4oyaW0gktQh3a0KiYblEmg"
TENCENT_SECRET_ID = "IKIDMYS5RUDsHM7ZhUw4suc2AyScSxtWolOj"
TENCENT_SECRET_KEY = "4nDI3UzA0WhZ6JBwPXLoyoJUKr4xWprE"
ALLOWED_USER = 8837854952  # apna Telegram ID
# =====================================

user_data = {}

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ALLOWED_USER:
        await update.message.reply_text("❌ Access Denied!")
        return
    
    url = update.message.text
    user_data[update.message.from_user.id] = {"url": url}
    
    # Domain list fetch karo
    keyboard = [
        [InlineKeyboardButton("gaganpratapvod2", callback_data="domain_gaganpratapvod2")],
        [InlineKeyboardButton("pundit-mocks", callback_data="domain_pundit-mocks")],
        [InlineKeyboardButton("tgdoraemonmocks", callback_data="domain_tgdoraemonmocks")],
        [InlineKeyboardButton("sscpratham02", callback_data="domain_sscpratham02")],
        [InlineKeyboardButton("10juneca", callback_data="domain_10juneca")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📁 Domain select karo:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("domain_"):
        domain = data.replace("domain_", "")
        user_data[user_id]["domain"] = domain
        
        keyboard = [
            [InlineKeyboardButton("📁 Movies", callback_data="folder_movies")],
            [InlineKeyboardButton("📁 Music", callback_data="folder_music")],
            [InlineKeyboardButton("📁 Docs", callback_data="folder_docs")],
            [InlineKeyboardButton("📁 Videos", callback_data="folder_videos")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"✅ Domain: {domain}\n\n📂 Folder select karo:", reply_markup=reply_markup)

    elif data.startswith("folder_"):
        folder = data.replace("folder_", "")
        url = user_data[user_id]["url"]
        domain = user_data[user_id]["domain"]
        
        await query.edit_message_text(f"⏳ Upload ho raha hai...")
        
        # Yahan EdgeOne API call hogi
        final_url = f"https://{domain}.edgeone.app/{folder}/{url.split('/')[-1]}"
        await query.edit_message_text(f"✅ Done!\n🔗 Link: {final_url}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(handle_callback))
app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
