import telegram
from telegram.ext import Application, MessageHandler, filters
from datetime import datetime
import logging
import os # <-- ADDED: Needed to read environment variables

# --- CONFIGURATION ---
# IMPORTANT: The BOT_TOKEN is now read securely from the environment.
# You must set the BOT_TOKEN variable in the hosting platform's settings.
BOT_TOKEN = os.environ.get('BOT_TOKEN') 

# If the token is not found (e.g., during local testing), stop the script
if not BOT_TOKEN:
    print("FATAL ERROR: BOT_TOKEN environment variable not found. Please set it in your host's settings.")
    # Exit if the token is missing to prevent errors
    exit() 

# Group 1 (Source: where the message is sent)
SOURCE_CHAT_ID = -1003160364537 
# Group 2 (Destination: where the bot forwards the message)
DESTINATION_CHAT_ID = -1003003382573 
# The bot looks for this exact username at the start of the message
TRIGGER_BOT_USERNAME = "@OpsUpdatesBot" 

# --- LOGGING SETUP ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- HANDLER FUNCTION ---
async def message_handler(update, context):
    """
    Monitors SOURCE_CHAT_ID for a mention of the bot, then formats 
    and sends the message to DESTINATION_CHAT_ID.
    """
    try:
        # Check 1: Is the message from the correct source chat?
        if update.effective_chat.id != SOURCE_CHAT_ID:
            return 

        # Check 2: Does the message contain text?
        if not update.message or not update.message.text:
            return 

        message_text = update.message.text.strip()

        # Check 3: Does the message start with the bot's username (a mention)?
        if message_text.lower().startswith(TRIGGER_BOT_USERNAME.lower()):

            # 1. Clean up the message (remove the @bot mention)
            clean_message = message_text[len(TRIGGER_BOT_USERNAME):].strip()

            # 2. Get the current time and format it
            now = datetime.now()
            # Format: 10/02 04:49 (Example)
            date_time_str = now.strftime("%m/%d %H:%M") 

            # 3. Create the final message
            final_message = f"{clean_message} at {date_time_str}"

            # 4. Send the message to the destination chat (Group 2)
            await context.bot.send_message(
                chat_id=DESTINATION_CHAT_ID,
                text=final_message
            )

            logger.info(f"Triggered by '{clean_message}'. Sent to {DESTINATION_CHAT_ID}")

    except telegram.error.Unauthorized:
        logger.error("Unauthorized. Check your BOT_TOKEN is correct and has not been revoked.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

# --- MAIN BOT LOOP ---

def main():
    """Starts the bot listener (polling loop) using the Application class."""

    # 1. Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # 2. Register the handler: calls 'message_handler' for any new text message
    # We use a lambda to filter for only messages that are not commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # 3. Start the Bot
    logger.info("Bot is running and monitoring Group 1...")
    application.run_polling()


if __name__ == '__main__':
    main()
    