# Phone Companion Parental Control

A Telegram control/status companion running on the Android phone itself through Termux + Termux:API.

## Included
- Battery status
- Device/Android information
- Wi-Fi connection details
- Location request (only when the Android permission and location services allow it)
- Torch toggle
- Volume status / safe volume adjustment
- Menu and owner-only Telegram access

Sensitive actions such as remote camera/microphone capture, SMS harvesting, clipboard collection, and contact extraction are deliberately not implemented. Android permissions and visible device-user controls remain in force.

## Setup
1. Install Termux and Termux:API from F-Droid.
2. In Termux:
   `pkg update -y && pkg upgrade -y`
   `pkg install python termux-api -y`
   `pip install -r requirements.txt`
3. Create a Telegram bot with BotFather and copy its token.
4. Copy `config.example.py` to `config.py`, enter bot token and your Telegram numeric user ID.
5. Run: `python bot.py`

Keep Termux running and exempt it from battery optimization if appropriate. Do not publish your bot token.
