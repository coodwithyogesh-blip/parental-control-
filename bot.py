import json, subprocess
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from config import BOT_TOKEN, OWNER_ID

MENU = ReplyKeyboardMarkup([
 ["📍 Location", "🔋 Battery", "📱 Device"],
 ["📩 SMS", "🎙 Microphone", "📷 Camera"],
 ["🔉 Volume", "🔔 Notifications", "📶 Wi-Fi"],
 ["📋 Clipboard", "👥 Contacts", "📅 Calendar"],
 ["🔦 Torch ON", "🔦 Torch OFF", "📳 Vibrate"],
 ["🧭 Sensors", "ℹ️ Help"]
], resize_keyboard=True)

def run_api(cmd, timeout=20):
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
        if p.returncode: return p.stderr.strip() or "Command failed."
        return p.stdout.strip() or "Done."
    except Exception as e: return str(e)

def get_json(cmd):
    out=run_api(cmd)
    try: return json.loads(out)
    except Exception: return out

def owner(update):
    return update.effective_user and update.effective_user.id==OWNER_ID

async def deny(update):
    if update.message: await update.message.reply_text("⛔ Access denied.")

async def start(update,context):
    if not owner(update): return await deny(update)
    await update.message.reply_text("Phone Companion parental-control menu. Device permissions and visible Android controls apply.",reply_markup=MENU)

async def battery(update,context):
    if not owner(update): return await deny(update)
    b=get_json(["termux-battery-status"])
    if isinstance(b,dict):
        await update.message.reply_text(f"🔋 Battery: {b.get('percentage','?')}%\nStatus: {b.get('status','?')}\nPlugged: {b.get('plugged','?')}\nTemp: {b.get('temperature','?')}°C")
    else: await update.message.reply_text(str(b))

async def device(update,context):
    if not owner(update): return await deny(update)
    await update.message.reply_text(run_api(["termux-info"])[:3500])

async def wifi(update,context):
    if not owner(update): return await deny(update)
    d=get_json(["termux-wifi-connectioninfo"])
    if isinstance(d,dict):
        await update.message.reply_text(f"📶 Wi-Fi\nSSID: {d.get('ssid','?')}\nIP: {d.get('ip','?')}\nSpeed: {d.get('link_speed','?')} Mbps")
    else: await update.message.reply_text(str(d))

async def location(update,context):
    if not owner(update): return await deny(update)
    await update.message.reply_text("Requesting device location. Android location permission/services must be enabled.")
    d=get_json(["termux-location","-p","gps"])
    if isinstance(d,dict):
        await update.message.reply_text(f"📍 Location\nLatitude: {d.get('latitude','?')}\nLongitude: {d.get('longitude','?')}\nAccuracy: {d.get('accuracy','?')} m")
    else: await update.message.reply_text(str(d))

async def torch(update,context,on):
    if not owner(update): return await deny(update)
    result=run_api(["termux-torch","on" if on else "off"])
    await update.message.reply_text(("🔦 Torch ON" if on else "🔦 Torch OFF")+ ("\n"+result if result not in ("Done.","") else ""))

async def volume(update,context):
    if not owner(update): return await deny(update)
    await update.message.reply_text(run_api(["termux-volume"]))

async def vibrate(update,context):
    if not owner(update): return await deny(update)
    await update.message.reply_text(run_api(["termux-vibrate","-d","500"]))

async def sensors(update,context):
    if not owner(update): return await deny(update)
    await update.message.reply_text("🧭 Sensor request. Sensor access may expose device context. Run on the device and review permissions; remote sensor streaming is not enabled.")

async def calendar(update,context):
    if not owner(update): return await deny(update)
    await update.message.reply_text("📅 Calendar access isn't remotely read by this bot. Open the calendar on the phone or use an explicit on-device export.")

async def notifications(update,context):
    if not owner(update): return await deny(update)
    await update.message.reply_text("🔔 Notification access can expose private messages. This bot does not remotely harvest notification contents. Review Android Notification Access on-device.")

async def privacy_info(update,context,label):
    if not owner(update): return await deny(update)
    await update.message.reply_text(label+"\n\nThis sensitive action is not remotely collected by the bot. Use the phone's visible, user-initiated app/Android workflow and review permissions on-device.")

async def help_cmd(update,context):
    if not owner(update): return await deny(update)
    await update.message.reply_text("15 categories: Location, Battery, Device, SMS, Microphone, Camera, Volume, Notifications, Wi-Fi, Clipboard, Contacts, Calendar, Torch, Vibration and Sensors. Access is owner-ID restricted. Sensitive content capture/export is not implemented.",reply_markup=MENU)

async def handle_text(update,context):
    if not owner(update): return await deny(update)
    t=update.message.text
    if t=="📍 Location": await location(update,context)
    elif t=="🔋 Battery": await battery(update,context)
    elif t=="📱 Device": await device(update,context)
    elif t=="📶 Wi-Fi": await wifi(update,context)
    elif t=="🔦 Torch ON": await torch(update,context,True)
    elif t=="🔦 Torch OFF": await torch(update,context,False)
    elif t=="🔉 Volume": await volume(update,context)
    elif t=="📳 Vibrate": await vibrate(update,context)
    elif t=="🧭 Sensors": await sensors(update,context)
    elif t=="📅 Calendar": await calendar(update,context)
    elif t=="🔔 Notifications": await notifications(update,context)
    elif t=="📩 SMS": await privacy_info(update,context,"📩 SMS: Remote reading/sending is disabled. Use the phone's visible SMS app.")
    elif t=="🎙 Microphone": await privacy_info(update,context,"🎙 Microphone: Remote recording is disabled. Start recording visibly on the device.")
    elif t=="📷 Camera": await privacy_info(update,context,"📷 Camera: Remote capture is disabled. Use the camera app visibly on the device.")
    elif t=="📋 Clipboard": await privacy_info(update,context,"📋 Clipboard: Clipboard scraping is disabled. Share text intentionally from the device.")
    elif t=="👥 Contacts": await privacy_info(update,context,"👥 Contacts: Remote extraction is disabled. Export/share contacts locally after reviewing.")
    elif t=="ℹ️ Help": await help_cmd(update,context)
    else: await update.message.reply_text("Use the menu.",reply_markup=MENU)

def main():
    if not BOT_TOKEN or BOT_TOKEN=="PASTE_BOT_TOKEN_HERE": raise SystemExit("Set BOT_TOKEN in config.py")
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("help",help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle_text))
    app.run_polling()

if __name__=="__main__": main()
