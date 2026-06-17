import os
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "8935637388:AAFrm5jfRNISj4oyaW0gktQh3a0KiYblEmg"
ALLOWED_USER = 8837854952
PAGES_TOKEN = "m5FsF4KK110J/5y6aZuTdkXmFleB+QM7OZcBLNokX4M="

DOMAINS_FILE = "domains.json"
FOLDERS_FILE = "folders.json"

def load_data(file, default):
    if os.path.exists(file):
        with open(file) as f:
            return json.load(f)
    return default

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

user_state = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ALLOWED_USER:
        await update.message.reply_text("Access Denied!")
        return
    uid = update.message.from_user.id
    text = update.message.text
    if user_state.get(uid) == "adding_domain":
        domains = load_data(DOMAINS_FILE, [])
        domains.append(text)
        save_data(DOMAINS_FILE, domains)
        user_state[uid] = None
        await update.message.reply_text("Domain add ho gaya!")
        return
    if user_state.get(uid) == "adding_folder":
        folders = load_data(FOLDERS_FILE, [])
        folders.append(text)
        save_data(FOLDERS_FILE, folders)
        user_state[uid] = None
        await update.message.reply_text("Folder add ho gaya!")
        return
    user_state[uid] = {"url": text}
    domains = load_data(DOMAINS_FILE, ["gaganpratapvod2", "pundit-mocks", "tgdoraemonmocks", "sscpratham02", "10juneca"])
    keyboard = [[InlineKeyboardButton(d, callback_data="domain_" + d)] for d in domains]
    keyboard.append([InlineKeyboardButton("Add Domain", callback_data="add_domain")])
    await update.message.reply_text("Domain select karo:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    data = query.data
    if data == "add_domain":
        user_state[uid] = "adding_domain"
        await query.edit_message_text("Naya domain naam bhejo:")
        return
    if data == "add_folder":
        user_state[uid] = "adding_folder"
        await query.edit_message_text("Naya folder naam bhejo:")
        return
    if data.startswith("domain_"):
        domain = data[7:]
        if isinstance(user_state.get(uid), dict):
            user_state[uid]["domain"] = domain
        folders = load_data(FOLDERS_FILE, ["Movies", "Music", "Docs", "Videos"])
        keyboard = [[InlineKeyboardButton(f, callback_data="folder_" + f)] for f in folders]
        keyboard.append([InlineKeyboardButton("Add Folder", callback_data="add_folder")])
        await query.edit_message_text("Folder select karo:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("folder_"):
        folder = data[7:]
        state = user_state.get(uid, {})
        url = state.get("url", "")
        domain = state.get("domain", "")
        await query.edit_message_text("Upload ho raha hai...")
        try:
            auth = "Bearer " + PAGES_TOKEN
            head = {"Authorization": auth, "Content-Type": "application/json"}
            body = {"projectName": domain, "files": [{"path": "/" + folder + "/" + url.split("/")[-1], "url": url}]}
            resp = requests.post("https://api.edgeone.ai/pages/deployments", headers=head, json=body)
            final = "https://" + domain + ".edgeone.app/" + folder + "/" + url.split("/")[-1]
            await query.edit_message_text("Done!\nLink: " + final)
        except Exception as e:
            await query.edit_message_text("Error: " + str(e))

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(handle_callback))
app.run_polling(drop_pending_updates=True)
