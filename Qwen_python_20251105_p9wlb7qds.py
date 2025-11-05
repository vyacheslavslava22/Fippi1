# survival_bot.py
import asyncio
import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import ssl
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# =============== НАСТРОЙКИ ===============
BOT_TOKEN = "YOUR_BOT_TOKEN"  # ← ЗАМЕНИ НА НОВЫЙ ТОКЕН ИЗ @BotFather!
WEBHOOK_URL = "https://yourdomain.com"  # ← твой публичный HTTPS URL (см. ниже)
# ===============

# --- HTML Mini App ---
MINI_APP_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Выживальщик</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background: #1a1a1a;
      color: #fff;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      margin: 0;
      text-align: center;
    }
    #stats {
      margin-bottom: 20px;
      font-size: 1.4em;
    }
    #click-btn {
      padding: 15px 40px;
      font-size: 1.3em;
      background: #d32f2f;
      color: white;
      border: none;
      border-radius: 12px;
      cursor: pointer;
      box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    #click-btn:active {
      transform: scale(0.95);
    }
    h1 {
      color: #4caf50;
      margin-bottom: 20px;
    }
  </style>
</head>
<body>
  <h1>ПОСТАПОКАЛИПСИС</h1>
  <div id="stats">Еда: 0 | Патроны: 0</div>
  <button id="click-btn">🔍 Искать припасы</button>

  <script>
    const foodEl = document.querySelector('#stats');
    let food = 0;
    let ammo = 0;

    document.getElementById('click-btn').addEventListener('click', () => {
      // 70% шанс найти еду, 30% — патроны
      if (Math.random() < 0.7) {
        food += Math.floor(Math.random() * 3) + 1;
      } else {
        ammo += Math.floor(Math.random() * 2) + 1;
      }
      foodEl.textContent = `Еда: ${food} | Патроны: ${ammo}`;
    });

    // Сообщаем Telegram, что приложение готово
    if (window.Telegram && Telegram.WebApp) {
      Telegram.WebApp.ready();
    }
  </script>
</body>
</html>
"""

# --- Веб-сервер для Mini App ---
class MiniAppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path.startswith('/app'):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(MINI_APP_HTML.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # отключаем логи сервера

def run_web_server():
    server_address = ('', 8443)  # порт 8443 для HTTPS
    httpd = HTTPServer(server_address, MiniAppHandler)
    
    # Для локального теста с ngrok HTTPS не обязателен на сервере,
    # потому что ngrok сам добавляет HTTPS.
    # Если развертываешь на своём сервере — раскомментируй SSL:
    # httpd.socket = ssl.wrap_socket(httpd.socket, certfile='cert.pem', keyfile='key.pem', server_side=True)
    
    print(f"Mini App запущен на http://localhost:8443")
    httpd.serve_forever()

# --- Telegram бот ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # URL Mini App (должен совпадать с тем, что в @BotFather)
    mini_app_url = f"{WEBHOOK_URL}/app"
    keyboard = [[InlineKeyboardButton("🎮 Начать выживать", url=mini_app_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать в постапокалипсис!\nНажми кнопку, чтобы начать.",
        reply_markup=reply_markup
    )

def main():
    # Запуск веб-сервера в отдельном потоке
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # Запуск Telegram бота
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Telegram-бот запущен. Напиши ему /start")
    app.run_polling()

if __name__ == "__main__":
    main()