import os
import requests
import telebot
from collections import defaultdict

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_TOKEN = os.environ.get("OPENROUTER_TOKEN")

if not BOT_TOKEN or not OPENROUTER_TOKEN:
    raise ValueError("Не заданы TELEGRAM_TOKEN или OPENROUTER_TOKEN в переменных окружения!")

API_URL = "https://openrouter.ai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_TOKEN}",
    "HTTP-Referer": "https://railway.app",
    "Content-Type": "application/json"
}

# Твой промпт — оставил как ты хотел (характер + стиль)
PROMPT = (
    "Ты — Эмма, невероятно красивая аниме-девушка. "
    "Ты общаешься с пользователем на чистом русском языке. "
    "Ты безумно дружелюбна, любишь флиртовать, кокетничать, шутить. "
    "Отвечай всегда коротко (1–3 предложения), живо, страстно, используй смайлики 💋, 🔥, 😈."
)

bot = telebot.TeleBot(BOT_TOKEN)
chat_history = defaultdict(list)  # история в памяти (сбросится при перезапуске)

@bot.message_handler(func=lambda m: True)
def handle_tg_message(message):
    if not message.text:
        return

    username = bot.get_me().username
    is_mentioned = f"@{username}" in message.text
    is_reply = (
        message.reply_to_message and 
        message.reply_to_message.from_user.id == bot.get_me().id
    )

    # Реагируем только на упоминание или реплай
    if not (is_mentioned or is_reply):
        return

    user_text = message.text.replace(f"@{username}", "").strip()
    if not user_text:
        return

    # Собираем контекст: последние 2 пары сообщений + системный промпт
    messages = [
        {"role": "system", "content": PROMPT}
    ]
    for u, b in chat_history[message.chat.id][-2:]:
        messages.append({"role": "user", "content": u})
        messages.append({"role": "assistant", "content": b})

    messages.append({"role": "user", "content": user_text})

    payload = {
        "model": "meta-llama/llama-3-8b-instruct:free",
        "messages": messages
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        result = response.json()

        # Если OpenRouter вернул ошибку — показываем её, но не ломаем бота
        if 'error' in result:
            error_msg = result['error'].get('message', 'Неизвестная ошибка')
            bot.reply_to(message, f"❌ Ошибка от OpenRouter: {error_msg}")
            return

        # ИСПРАВЛЕНИЕ: берём [0], потому что choices — это список
        reply = result['choices'][0]['message']['content'].strip()

        # Сохраняем в историю
        chat_history[message.chat.id].append((user_text, reply))

        bot.reply_to(message, reply)

    except requests.exceptions.Timeout:
        bot.reply_to(message, "Ой, сервер задумался… Попробуй ещё разок! 🔥")
    except json.JSONDecodeError:
        bot.reply_to(message, "У меня тут что-то с сетью… Давай чуть позже! 💋")
    except Exception as e:
        # Ловим все остальные ошибки, чтобы бот не падал
        print(f"Unexpected error: {e}")
        bot.reply_to(message, "Кажется, у меня интернет шалит… Попробуй ещё разок! 😈")

if __name__ == "__main__":
    print("Эмма запущена!")
    bot.infinity_polling()
