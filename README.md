# Phone Companion Parental Control

Telegram menu for a companion agent running on Android with Termux + Termux:API. Owner-ID restricted; Android permissions and limitations apply.

## Menu categories (15)
Location, Battery, Device info, SMS, Microphone, Camera, Volume, Notifications, Wi-Fi, Clipboard, Contacts, Calendar, Torch, Vibration, Sensors.

Working API actions in this version: location, battery, device info, Wi-Fi connection info, torch, and vibration. Other buttons explain how to complete sensitive actions visibly on-device. Remote harvesting/capture of SMS, microphone, camera, clipboard, contacts, notifications, calendar, or sensor streams is not implemented.

## Install
1. Install Termux and Termux:API (both apps).
2. In Termux: `pkg update -y && pkg upgrade -y`
3. `pkg install python termux-api -y`
4. Clone repository: `git clone https://github.com/coodwithyogesh-blip/parental-control-.git`
5. `cd parental-control-`
6. `pip install -r requirements.txt`
7. `cp config.example.py config.py` and edit token + numeric Telegram owner ID.
8. `python bot.py`

Do not commit `config.py` or share the bot token. Keep the device user aware of the companion agent and review Android permission prompts. Background execution may be restricted by Android.
