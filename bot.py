import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# Lấy cấu hình từ biến môi trường của Railway
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Gemini đã sẵn sàng! Hãy gửi câu hỏi, tôi sẽ trả lời ngắn gọn và đúng trọng tâm.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text:
        return

    # Hiển thị trạng thái đang soạn tin
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction="Bạn là trợ lý AI trên Telegram. Hãy trả lời ngắn gọn, súc tích, đi thẳng vào trọng tâm câu hỏi của người dùng.",
                temperature=0.3,
            ),
        )

        reply_text = response.text or "Không nhận được phản hồi."

        # Xử lý chia tin nhắn nếu nội dung dài hơn giới hạn Telegram
        if len(reply_text) > 4000:
            for i in range(0, len(reply_text), 4000):
                await update.message.reply_text(reply_text[i:i+4000])
        else:
            await update.message.reply_text(reply_text)

    except Exception as e:
        logging.error(f"Lỗi khi xử lý: {e}")
        await update.message.reply_text("Đã xảy ra lỗi trong quá trình xử lý tin nhắn.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot đang khởi động trên Railway...")
    app.run_polling()
