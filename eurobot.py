#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position

import os
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import json
import random
import glob
import telegram


TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN_EUROBOT', "EMPTY")
COUNTRIES = [ 
        "albania", "armenia", "australia", "austria", "azerbaijan", "belgium", "croatia", "cyprus", "czechia",
        "denmark", "estonia", "finland", "france", "georgia", "germany", "greece", "iceland", "ireland",
        "israel", "italy", "latvia", "lithuania", "luxembourg", "malta", "moldova", "netherlands", "norway",
        "poland", "portugal", "san marino", "serbia", "slovenia", "spain", "sweden", "switzerland", "ukraine",
        "united kingdom"
]
COUNTRY_FLAGS = {
    "norway": "🇳🇴", "malta": "🇲🇹", "serbia": "🇷🇸", "latvia": "🇱🇻", "portugal": "🇵🇹", "ireland": "🇮🇪", "croatia": "🇭🇷",
    "switzerland": "🇨🇭", "israel": "🇮🇱", "moldova": "🇲🇩", "sweden": "🇸🇪", "azerbaijan": "🇦🇿", "czechia": "🇨🇿",
    "netherlands": "🇳🇱", "finland": "🇫🇮", "denmark": "🇩🇰", "armenia": "🇦🇲", "romania": "🇷🇴", "estonia": "🇪🇪",
    "belgium": "🇧🇪", "cyprus": "🇨🇾", "iceland": "🇮🇸", "greece": "🇬🇷", "poland": "🇵🇱", "slovenia": "🇸🇮", "georgia": "🇬🇪", 
    "san marino": "🇸🇲", "austria": "🇦🇹", "albania": "🇦🇱", "lithuania": "🇱🇹", "australia": "🇦🇺", "france": "🇫🇷", 
    "germany": "🇩🇪", "italy": "🇮🇹", "spain": "🇪🇸", "ukraine": "🇺🇦", "united kingdom": "🇬🇧", "luxembourg": "🇱🇺" }

SONGS = {
    "albania": "Titan - Besa",
    "armenia": "Jako - Ladaniva",
    "australia": "One Milkali (One Blood) - Electric Fields",
    "austria": "We Will Rave - Kaleen",
    "azerbaijan": "Özünlə apar - Fahree feat. Ilkin Dovlatov",
    "belgium": "Before the Party's Over - Mustii",
    "croatia": "Rim Tim Tagi Dim - Baby Lasagna",
    "cyprus": "Liar - Silia Kapsis",
    "czechia": "Pedestal - Aiko",
    "denmark": "Sand - Saba",
    "estonia": "(Nendest) narkootikumidest ei tea me (küll) midagi - 5miinust and Puuluup",
    "finland": "No Rules! - Windows95man",
    "france": "Mon amour - Slimane",
    "georgia": "Firefighter - Nutsa Buzaladze",
    "germany": "Always on the Run - Isaak",
    "greece": "Zari - Marina Satti",
    "iceland": "Scared of Heights - Hera Björk",
    "ireland": "Doomsday Blue - Bambie Thug",
    "israel": "Hurricane - Eden Golan",
    "italy": "La noia - Angelina Mango",
    "latvia": "Hollow - Dons",
    "lithuania": "Luktelk - Silvester Belt",
    "luxembourg": "Fighter - Tali",
    "malta": "Loop - Sarah Bonnici",
    "moldova": "In the Middle - Natalia Barbu",
    "netherlands": "Europapa - Joost Klein",
    "norway": "Ulveham - Gåte",
    "poland": "The Tower - Luna",
    "portugal": "Grito - Iolanda",
    "san marino": "11:11 - Megara",
    "serbia": "Ramonda - Teya Dora",
    "slovenia": "Veronika - Raiven",
    "spain": "Zorra - Nebulossa",
    "sweden": "Unforgettable - Marcus & Martinus",
    "switzerland": "The Code - Nemo",
    "ukraine": "Teresa & Maria - Alyona Alyona and Jerry Heil",
    "united kingdom": "Dizzy - Olly Alexander",
}






class State:
    def __init__(self, chat_id) -> None:
        self.chat_id = chat_id
        if os.path.exists(path_for_chat_id(chat_id)):
            self.load_state()
        else:
            self.registered_users = {}
            self.current_picking_user = None
            self.picked_countries = {}
            self.finished_registration = False
            self.draft_complete = False
            self.draft_order = []
            self.picks = 0
            self.left_over = 0
            self.save_state()
    
    def save_state(self):
        with open(path_for_chat_id(self.chat_id), 'w') as outfile:
            json.dump(self.__dict__, outfile)
    
    def load_state(self):
        with open(path_for_chat_id(self.chat_id), 'r') as infile:
            self.__dict__ = json.load(infile)


def path_for_chat_id(chat_id):
    return 'state_' + str(chat_id) + '.json'

states = {}

def get_state_this_chat(update):
    chat_id = update.effective_chat.id
    if chat_id not in states.keys():
        states[chat_id] = State(chat_id)
    return states[chat_id]


# for every file that matches state*.json, load it
for file in glob.glob("state_*.json"):
    chat_id = int(file[6:-5])
    states[chat_id] = State(chat_id)


async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /register is issued."""
    state = get_state_this_chat(update)
    if update.effective_user.id in state.registered_users.keys():
        await update.message.reply_text("You are already registered!")
        return
    id = update.effective_user.id
    if isinstance(id, str):
        id = int(id)
    state.registered_users[id] = update.effective_user.full_name
    state.save_state()

    await update.message.reply_html(
        rf"Hi {update.effective_user.full_name}, you are now registered for the Eurovision draft!",
        reply_markup=ForceReply(selective=True),
    )

def get_next_picking_user(update):
    state = get_state_this_chat(update)
    if state.current_picking_user is None:
        state.current_picking_user = state.draft_order[0]
    else:
        pick = len(state.picked_countries)
        index = pick % len(state.draft_order)
        state.current_picking_user = state.draft_order[index]
    state.save_state()
    if state.current_picking_user in state.registered_users.keys():
        return state.registered_users[state.current_picking_user]
    elif str(state.current_picking_user) in state.registered_users.keys():
        return state.registered_users[str(state.current_picking_user)]


async def still_to_pick_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /still_to_pick is issued."""
    state = get_state_this_chat(update)
    if not state.finished_registration:
        await update.message.reply_text("Registration is not complete!")
        return
    not_picked_countries = [ x for x in COUNTRIES if x not in state.picked_countries.keys() ]
    reply_text = "Countries still to be picked:\n"
    for country in not_picked_countries:
        reply_text += f"{country.title()} {COUNTRY_FLAGS[country]} - {SONGS[country]}\n"
    await update.message.reply_text(reply_text)


async def current_picks_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /current_picks is issued."""
    state = get_state_this_chat(update)
    if not state.finished_registration:
        await update.message.reply_text("Registration is not complete!")
        return
    await update.message.reply_text(get_picked_countries(update), parse_mode=telegram.constants.ParseMode.MARKDOWN)


async def end_registration_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /end_registration is issued."""
    state = get_state_this_chat(update)
    if len(state.registered_users) == 0:
        await update.message.reply_text("At least one person must be registered!")
        return
    if state.finished_registration:
        await update.message.reply_text("Registration is already complete!")
        return
    reply_text = "Registration is now finalized!\n"
    state.finished_registration = True

    state.draft_order = list(state.registered_users.keys()).copy()
    random.shuffle(state.draft_order)
    reversed = state.draft_order.copy()
    reversed.reverse()
    state.draft_order.extend(reversed)
    # add elements from reversed to draft_order


    reply_text += "\nDraft order: "
    for entry in state.draft_order:
        reply_text += state.registered_users[entry] + ", "
    if len(state.draft_order) != 0:
        reply_text = reply_text[:-2]
    
    reply_text += "\n\nThere are " + str(len(COUNTRIES)) + " countries to pick from.\n"
    rounds = len(COUNTRIES) // len(state.registered_users)
    state.picks = len(state.registered_users) * rounds
    state.left_over = len(COUNTRIES) - state.picks
    reply_text += "\nThere will be a total of " + str(state.picks) + " picks. \n\n" + str(state.left_over) + " countries will be left over."
    
    reply_text += "\n\nFirst to pick is " + get_next_picking_user(update)

    state.save_state()
    await update.message.reply_text(reply_text)


def get_picked_countries(update):
    state = get_state_this_chat(update)
    text = "Picks so far:"
    for user_id, user_name in state.registered_users.items():
        if isinstance(user_id, str):
            user_id = int(user_id)
        text += "\n**" + user_name + "**:"
        list_empty = True
        for country, picker_id in state.picked_countries.items():
            if picker_id == user_id:
                text += " " + country.title() + " (" + COUNTRY_FLAGS[country] + "),"
                list_empty = False
        if not list_empty:
            text = text[:-1]
        else:
            text += " None!"
    return text


async def pick_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /pick is issued."""
    state = get_state_this_chat(update)
    if not state.finished_registration:
        await update.message.reply_text("Registration is not complete!")
        return
    if not update.effective_user.id == int(state.current_picking_user) and not state.current_picking_user is None:
        await update.message.reply_text(f"It is {state.registered_users[state.current_picking_user]}'s turn to pick!")
        return
    if state.draft_complete:
        await update.message.reply_text("Draft is already complete!")
        return
    if update.message.text == "/pick":
        await update.message.reply_text("You must specify a country!")
        return
    country = update.message.text[6:].lower()

    # extract the country name from the COUNTRY_FLAGS dict
    if update.message.text[6:] in COUNTRY_FLAGS.values():
        country = [key for key, value in COUNTRY_FLAGS.items() if value == update.message.text[6:]][0]

    if not country in COUNTRIES:
        await update.message.reply_text("Invalid country!")
        return
    if country in state.picked_countries:
        await update.message.reply_text(f"Country '{country.title()}' already picked!")
        return
    state.picked_countries[country] = update.effective_user.id

    reply_text = update.effective_user.full_name +  " picked " + country.title() + " (" + COUNTRY_FLAGS[country] + ") - " + SONGS[country] + "."
    reply_text += "\n\nThere are " + str(state.picks - len(state.picked_countries)) + " countries left to pick (type \\still_to_pick to see them).\n"
    if len(state.picked_countries) == state.picks:
        reply_text += "\n\nDraft complete!"
        state.draft_complete = True
    else:
        reply_text += "\nThe next person to pick is " + get_next_picking_user(update)
    state.save_state()
    await update.message.reply_text(reply_text)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("register", register_command))
    application.add_handler(CommandHandler("end_registration", end_registration_command))
    application.add_handler(CommandHandler("pick", pick_command))
    application.add_handler(CommandHandler("current_picks", current_picks_command))
    application.add_handler(CommandHandler("still_to_pick", still_to_pick_command))

    # Run the bot until the user presses Ctrl-C
    while True:
        try:
            application.run_polling()
        except Exception as e:
            pass


if __name__ == "__main__":
    main()