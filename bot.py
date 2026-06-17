import os
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "8935637388:AAFrm5jfRNISj4oyaW0gktQh3a0KiYblEmg"
ALLOWED_USER = 8837854952
PAGES_TOKEN = "yKmeZfNSpxyV3yg7eSMffB7BuzMNkgiZJB2a+0HvFVw="
PROJECT_NAME = "achiever8"

SITE_URL = "https://achiever8.edgeone.dev/"

FOLDERS = ["grammar", "cpb", "vocab"]
FOLDER_NAMES = {
    "grammar": "Grammar",
    "cpb": "Complete Practice Batch",
    "vocab": "Samundarmanthan of Vocabulary"
}

user_state = {}

def get_html():
    resp = requests.get(SITE_URL)
    return resp.text

def add_link_to_html(html, folder_id, link_name, link_url):
    marker = 'id="content-' + folder_id + '">'
    empty = '<p class="empty">No links yet.</p>'
    new_link = '<a class="link-item" href="' + link_url + '" target="_blank"><span>' + link_name + '</span><span class="arrow-link">▶</span></a>'
    if empty in html:
        html = html.replace(
            marker + '\n      <p class="empty">No links yet.</p>',
            marker + '\n      ' + new_link
        )
    else:
        html = html.replace(
            marker,
            marker + '\n      ' + new_link
        )
    return html

def deploy_html(html):
    head = {"Authorization": "Bearer " + PAGES_TOKEN, "Content-Type": "application/json"}
    body = {
        "projectName": PROJECT_NAME,
        "files": [{"path": "/index.html", "content": html}]
    }
    resp = requests.post("https://api.edgeone.ai/pages/deployments", headers=head, json=body)
    return resp.json()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ALLOWED_USER:
        await update.message.reply_text("Access Denied!")
        return
    uid = update.message.from_user.id
    text = update.message.text

    if isinstance(user_state.get(uid), dict) and user_state[uid].get("step") == "waiting_name":
        user_state[uid]["name"] = text
        user_state[uid]["step"] = "waiting_link"
        await update.message.reply_text("Ab link bhejo:")
        return

    if isinstance(user_state.get(uid), dict) and user_state[uid].get("step") == "waiting_link":
        user_state[uid]["link"] = text
        folder = user_state[uid]["folder"]
        name = user_state[uid]["name"]
        link = text
        await update.message.reply_text("Upload ho raha hai...")
        try:
            html = get_html()
            html = add_link_to_html(html, folder, name, link)
            result = deploy_html(html)
            await update.message.reply_text("Done! Site update ho gayi!\n" + SITE_URL)
        except Exception as e:
            await update.message.reply_text("Error: " + str(e))
        user_state[uid] = None
        return

    keyboard = []
    for f in FOLDERS:
        keyboard.append([InlineKeyboardButton("📁 " + FOLDER_NAMES[f], callback_data="folder_" + f)])
    await update.message.reply_text("Folder select karo:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    data = query.data

    if data.startswith("folder_"):
        folder = data[7:]
        user_state[uid] = {"folder": folder, "step": "waiting_name"}
        await query.edit_message_text("Link ka naam bhejo (jaise: Day 1 Grammar):")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(handle_callback))
app.run_polling(drop_pending_updates=True)
