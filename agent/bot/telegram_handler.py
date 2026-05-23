from abc import update_abstractmethods
import logging
import os
from dotenv import load_dotenv
load_dotenv()

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage,SystemMessage

DEEPSEEK_API_KEY=os.getenv("DEEPSEEK_API_KEY")
TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")


llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
    max_completion_tokens=1024
)

# Setup logging (to see errors in your console)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# function to handle start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I am KYH-bot, powered by Deepseek. Ask me anything!"
    )

# function to handle user messages and sends them to DeepSeek
async def handle_ai_chat(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # showing "typing..." in telegram while waiting for the AI
    await context.bot.send_chat_action(chat_id=update.effective_chat.id,action="typing")

    try:
        messages=[
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=user_text)
        ]

        response = await llm.ainvoke(messages)

        await update.message.reply_text(response.content)

    except Exception as e:
        logging.error(f"Error calling DeepSeek: {e}")
        await update.message.reply_text("Sorry, I ran into an Error processing that request.")




if __name__=='__main__':

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler('start',start)
    application.add_handler(start_handler)

    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_ai_chat)
    application.add_handler(message_handler)

    print("Bot is running with DeepSeek AI.....")
    application.run_polling()
