#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position

import os
from telegram.ext import Application, CommandHandler
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
    application.add_handler(CommandHandler("register", telegram_commands.register_command))
    application.add_handler(CommandHandler("end_registration", telegram_commands.end_registration_command))
    application.add_handler(CommandHandler("pick", telegram_commands.pick_command))
    application.add_handler(CommandHandler("current_picks", telegram_commands.current_picks_command))
    application.add_handler(CommandHandler("still_to_pick", telegram_commands.still_to_pick_command))
    application.add_handler(CommandHandler("start", telegram_commands.start_command))
    application.add_handler(CommandHandler("help", telegram_commands.help_command))
    application.add_handler(CommandHandler("draft_order", telegram_commands.draft_order_command))
    application.add_handler(CommandHandler("registered_users", telegram_commands.registered_users_command))
    application.add_handler(CommandHandler("semifinals", telegram_commands.semi_finals_command))
    application.add_handler(CommandHandler("results", telegram_commands.results_command))

    # Run the bot until the user presses Ctrl-C
    while True:
        try:
            application.run_polling()
        except Exception as e:
            pass


if __name__ == "__main__":
    main()