import logging
from datetime import datetime

from agent.config.settings import TELEGRAM_BOT_TOKEN
from agent.graph.graph import graph
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# currently using In-Memory state store (will use MongoDb later)
user_states = {}


def initial_state(user_id: str, user_text: str) -> dict:
    return {
        "user_id": user_id,
        "date": datetime.now().strftime("%d-%m-%Y"),
        "user_input": user_text,
        "messages": [],
        "bot_reply": "",
        "conversation_stage": "idle",
        "meals": {},
        "logged_meals": [],
        "workout": {},
        "others": {},
        "daily_totals": {},
        "feedback": "",
        "plan": "",
        "weekly_report": "",
    }


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    reply = (
        "🏋️ KYH - Know Your Habit\n\n"
        "I track your fitness habits. Log meals, workouts, sleep, water.\n\n"
        "What do you want to lod?\n\n"
        "🍽️ Food       🏋️ Workout      📊 Others        📈 Report"
    )

    # Reset state for new session
    user_states[user_id] = initial_state(user_id, "/start")
    user_states[user_id]["bot_reply"] = reply
    user_states[user_id]["messages"].append(f"KYH: {reply}")
    user_states[user_id]["conversation_stage"] = "awaiting_category"

    await update.message.reply_text(reply)


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_text = update.message.text

    # Load or create state
    if user_id not in user_states:
        user_states[user_id] = initial_state(user_id=user_id, user_text=user_text)

    # Run graph
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )
    final_state = await graph.ainvoke(user_states[user_id])

    # save state
    user_states[user_id] = final_state

    # sending reply
    if final_state["bot_reply"]:
        await update.message.reply_text(final_state["bot_reply"])


def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_messages))
    print("🤖 KYH bot is running...")
    app.run_polling()


# ######################
# ###### OLD CODE ######
# ######################

# # function to handle start command
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(
#         "I am KYH-bot, powered by Deepseek. Ask me anything!"
#     )


# # function to handle user messages and sends them to DeepSeek
# async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_text = update.message.text

#     # showing "typing..." in telegram while waiting for the AI
#     await context.bot.send_chat_action(
#         chat_id=update.effective_chat.id, action="typing"
#     )

#     try:
#         messages = [
#             SystemMessage(content="You are a helpful assistant."),
#             HumanMessage(content=user_text),
#         ]

#         response = await llm.ainvoke(messages)

#         await update.message.reply_text(response.content)

#     except Exception as e:
#         logging.error(f"Error calling DeepSeek: {e}")
#         await update.message.reply_text(
#             "Sorry, I ran into an Error processing that request."
#         )


# if __name__ == "__main__":
#     application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

#     start_handler = CommandHandler("start", start)
#     application.add_handler(start_handler)

#     message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_ai_chat)
#     application.add_handler(message_handler)

#     print("Bot is running with DeepSeek AI.....")
#     application.run_polling()
