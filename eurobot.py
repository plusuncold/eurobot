#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position

import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from state import load_all_states
import telegram_commands



def main() -> None:
    """Start the bot."""

    print("Loading states...")
    load_all_states()

    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN_EUROBOT', "EMPTY")
    print("Running with token: " + TELEGRAM_TOKEN)
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # on different commands - answer in Telegram
    for command_name, command_function in telegram_commands.COMMANDS.items():
        application.add_handler(CommandHandler(command_name, command_function))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_commands.messages))

    # Run the bot until the user presses Ctrl-C
    while True:
        try:
            application.run_polling()
        except Exception as e:
            pass


if __name__ == "__main__":
    main()