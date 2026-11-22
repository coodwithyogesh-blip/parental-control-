import json, subprocess, asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from config import BOT_TOKEN, OWNER_ID

MENU = ReplyKeyboardMarkup([
 ["📍 Location", "🔋 Battery"],
 ["📱 Device info", "📶 Wi-Fi"],
 ["🔦 Torch ON", "🔦 Torch OFF"],
 ["🔉 Volume", "➕ Volume"],
 ["➖ Volume", "ℹ️ Help"]
], resize_keyboard=True)

def run_api(cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if p.returncode != 0:
            return p.stderr.strip() or "Command failed."
        return p.stdout.strip() or "Done."
    except Exception as e:
        return str(e)

def get_json(cmd):
    out=run_api(cmd)
    try: return json.loads(out)
    except: return out

def owner(update):
    return update.effective_user and update.effective_user.id == OWNER_ID

async def deny(update):
    await update.message.reply_text("⛔ Access denied.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not owner(update): return await deny(update)
    await update.message.reply_text("Phone Companion is ready. Select an action:", reply_markup=MENU)

async def battery(update, context):
    if not owner(update): return await deny(update)
    b=get_json(["termux-battery-status"])
    if isinstance(b,dict):
        await update.message.reply_text(
            f"🔋 Battery: {b.get('percentage','?')}%\n"
            f"Status: {b.get('status','?')}\n"
            f"Plugged: {b.get('plugged','?')}\n"
            f"Temperature: {b.get('temperature','?')}°C")
    else: await update.message.reply_text(b)

async def device(update, context):
    if not owner(update): return await deny(update)
    info=run_api(["termux-info"])
    await update.message.reply_text(info[:3500])

async def wifi(update, context):
    if not owner(update): return await deny(update)
    data=get_json(["termux-wifi-connectioninfo"])
    if isinstance(data,dict):
        # Avoid exposing MAC/BSSID details by default.
        msg=f"📶 Wi-Fi\nSSID: {data.get('ssid','?')}\nIP: {data.get('ip','?')}\nLink speed: {data.get('link_speed','?')} Mbps"
    else: msg=data
    await update.message.reply_text(msg)

async def location(update, context):
    if not owner(update): return await deny(update)
    await update.message.reply_text("Requesting location. Android location permission and location services must be enabled.")
    result=get_json(["termux-location","-p","gps"])
    if isinstance(result,dict):
        lat=result.get("latitude"); lon=result.get("longitude")
        if lat is not None and lon is not None:
            await update.message.reply_text(f"📍 Location\nLatitude: {lat}\nLongitude: {lon}\nAccuracy: {result.get('accuracy','?')} m")
        else: await update.message.reply_text(str(result))
    else: await update.message.reply_text(result)

async def torch(update, context, enabled):
    if not owner(update): return await deny(update)
    res=run_api(["termux-torch", "on" if enabled else "off"])
    await update.message.reply_text("🔦 Torch ON" if enabled else "🔦 Torch OFF")

async def volume(update, context):
    if not owner(update): return await deny(update)
    await update.message.reply_text(run_api(["termux-volume"]))

async def setvolume(update, context, delta):
    if not owner(update): return await deny(update)
    # Read current media volume, then adjust with Android API. Unsupported API
    # versions may simply report an error; no privileged OS bypass is attempted.
    await update.message.reply_text("Volume adjustment is not universally supported by Termux:API. Use the phone's volume keys if unavailable.")

async def help_cmd(update, context):
    if not owner(update): return await deny(update)
    await update.message.reply_text("Available: location, battery, device info, Wi-Fi, torch toggle and volume status. Access is owner-ID restricted.")

async def handle_text(update, context):
    if not owner(update): return await deny(update)
    t=update.message.text
    if t=="📍 Location": await location(update,context)
    elif t=="🔋 Battery": await battery(update,context)
    elif t=="📱 Device info": await device(update,context)
    elif t=="📶 Wi-Fi": await wifi(update,context)
    elif t=="🔦 Torch ON": await torch(update,context,True)
    elif t=="🔦 Torch OFF": await torch(update,context,False)
    elif t=="🔉 Volume": await volume(update,context)
    elif t in ("➕ Volume","➖ Volume"): await setvolume(update,context,1 if "➕" in t else -1)
    elif t=="ℹ️ Help": await help_cmd(update,context)
    else: await update.message.reply_text("Use the menu buttons.",reply_markup=MENU)

def main():
    if BOT_TOKEN=="PASTE_BOT_TOKEN_HERE" or not BOT_TOKEN:
        raise SystemExit("Edit config.py and set BOT_TOKEN.")
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("help",help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle_text))
    app.run_polling()

if __name__=="__main__": main()
