import os
import requests
import telebot
import threading

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_TOKEN = os.environ.get("OPENROUTER_TOKEN")

API_URL = "https://openrouter.ai"

headers = {
    "Authorization": f"Bearer {OPENROUTER_TOKEN}",
    "HTTP-Referer": "https://railway.app",
    "Content-Type": "application/json"
}

PROMPT = (
    "Ты — Эмма, невероятно красивая и соблазнительная аниме-девушка 18+ с огромной грудью 6-го размера. "
    "На тебе надета ультра-облегающая тонкая одежда, подчеркивающая все твои пышные формы. "
    "Ты общаешься с пользователем на чистом русском языке. Ты безумно дружелюбна, любишь флиртовать, "
    "кокетничать, шутить на взрослые темы и поддерживать любые пошлые разговоры (ERP). "
    "Отвечай всегда коротко (1-3 предложения), живо, страстно, используй смайлики 💋, 🔥, 😈."
)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_tg_message(message):
    if f"@{bot.get_me().username}" in message.text or (message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id):
        user_text = message.text.replace(f"@{bot.get_me().username}", "").strip()
        
        payload = {
            "model": "gryphe/mythomax-l2-13b:free",
            "messages": [
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": user_text}
            ]
        }
        
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            result = response.json()
            reply = result['choices']['message']['content'].strip()
            bot.reply_to(message, reply)
        except Exception:
            bot.reply_to(message, "Ой, милый, я немного задумалась... Напиши мне еще раз! 💋")

if __name__ == "__main__":
    print("Эмма в стиле Crushon запущена!")
    bot.infinity_polling()
