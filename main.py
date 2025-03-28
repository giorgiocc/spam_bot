import asyncio
import threading
from telethon import TelegramClient, events
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, Bot is Running!'

api_id = 27129882
api_hash = '13cf2eb9849b490a933c9beb89de5edf'
session_name = 'my_session'
target_bot = '@Vinmege_bot'

client = TelegramClient(session_name, api_id, api_hash)

in_chat = False
trigger_enabled = True  
blocked_detected = False  

async def send_message(text: str):
    """
    Sends a message to the target bot.
    """
    try:
        await client.send_message(target_bot, text)
        print(f"Sent: {text}")
    except Exception as e:
        print("Error sending message:", e)

@client.on(events.NewMessage(chats=target_bot))
async def target_bot_handler(event):
    """
    Handles incoming messages from the target bot.
    """
    global in_chat, trigger_enabled, blocked_detected
    if not trigger_enabled:
        print("Trigger is off. Ignoring incoming message.")
        return

    text = event.raw_text
    print("Received from target:", text)

    if "You're blocked. Try again later." in text:
        print("Detected block message. Turning off bot for 30 minutes.")
        trigger_enabled = False
        blocked_detected = True
        await asyncio.sleep(1800)  
        print("Reactivating bot after 30 minutes.")
        trigger_enabled = True
        blocked_detected = False
        await send_message("/start")

    elif "You're already in queue" in text:
        print("Detected queue message. Sending /next")
        await send_message("/next")

    elif "Partner found!" in text:
        print("Detected 'Partner found!'")
        await send_message("t.me/GeorgiaChatBot")
        await send_message("გადმო ჩატბოთში")
        await send_message("@GeorgiaChatBot")
        in_chat = True

        await asyncio.sleep(30)

        messages = await client.get_messages(target_bot, limit=5)
        ended_detected = any("Your partner ended the chat" in msg.raw_text for msg in messages)

        if ended_detected:
            print("Detected end-of-chat after 30 seconds.")
        else:
            print("No end-of-chat detected within 30 seconds.")

        await send_message("/next")
        in_chat = False

    elif "Your partner ended the chat" in text:
        print("Detected 'Your partner ended the chat'")
        if not in_chat:
            await send_message("/next")

@client.on(events.NewMessage(from_users="me"))
async def trigger_control_handler(event):
    """
    Handles trigger control commands sent from your own account.
    Send '/on' to enable or '/off' to disable the automation.
    """
    global trigger_enabled
    text = event.raw_text.lower().strip()
    if text == "/on":
        trigger_enabled = True
        print("Trigger turned ON")
        await event.reply("Trigger is now ON")
    elif text == "/off":
        trigger_enabled = False
        print("Trigger turned OFF")
        await event.reply("Trigger is now OFF")

async def main():
    print("Connecting to Telegram...")
    await client.start()
    print("Connected!")
    await send_message("/start")
    print("Waiting for messages from", target_bot)
    await client.run_until_disconnected()

def run_flask():
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port)  

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
