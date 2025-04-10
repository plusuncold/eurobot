#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position

import os
from telegram import ForceReply, Update, KeyboardButton, ReplyKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import json
import random
import glob
import telegram


TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN_EUROBOT', "EMPTY")
COUNTRY_FLAGS = {
    "norway": "🇳🇴", "malta": "🇲🇹", "serbia": "🇷🇸", "latvia": "🇱🇻", "portugal": "🇵🇹", "ireland": "🇮🇪", "croatia": "🇭🇷",
    "switzerland": "🇨🇭", "israel": "🇮🇱", "moldova": "🇲🇩", "sweden": "🇸🇪", "azerbaijan": "🇦🇿", "czechia": "🇨🇿",
    "netherlands": "🇳🇱", "finland": "🇫🇮", "denmark": "🇩🇰", "armenia": "🇦🇲", "romania": "🇷🇴", "estonia": "🇪🇪",
    "belgium": "🇧🇪", "cyprus": "🇨🇾", "iceland": "🇮🇸", "greece": "🇬🇷", "poland": "🇵🇱", "slovenia": "🇸🇮", "georgia": "🇬🇪", 
    "san marino": "🇸🇲", "austria": "🇦🇹", "albania": "🇦🇱", "lithuania": "🇱🇹", "australia": "🇦🇺", "france": "🇫🇷", 
    "germany": "🇩🇪", "italy": "🇮🇹", "spain": "🇪🇸", "ukraine": "🇺🇦", "united kingdom": "🇬🇧", "luxembourg": "🇱🇺" }

SEMI_FINAL_ONE = [
    "Iceland",
    "Poland",
    "Slovenia",
    "Estonia",
    "Ukraine",
    "Sweden",
    "Portugal",
    "Norway",
    "Belgium",
    "Azerbaijan",
    "San Marino",
    "Albania",
    "Netherlands",
    "Croatia",
    "Cyprus"
]

SEMI_FINAL_TWO = [
    "Australia",
    "Montenegro",
    "Ireland",
    "Latvia",
    "Armenia",
    "Austria",
    "Greece",
    "Lithuania",
    "Malta",
    "Georgia",
    "Denmark",
    "Czechia",
    "Luxembourg",
    "Israel",
    "Serbia",
    "Finland"
]
SEMI_FINAL_ONE_ELIMINATED = []
SEMI_FINAL_TWO_ELIMINATED = []
RESULTS = {}

# eurovision 2025
SONGS = {
    "albania": "Zjerm",
    "armenia": "Survivor",
    "australia": "Milkshake Man",
    "austria": "Wasted Love",
    "azerbaijan": "Run With U",
    "belgium": "Strobe Lights",
    "croatia": "Poison Cake",
    "cyprus": "Shh",
    "czechia": "Kiss Kiss Goodbye",
    "denmark": "Hallucination",
    "estonia": "Espresso Macchiato",
    "finland": "Ich komme",
    "france": "Maman",
    "georgia": "Freedom",
    "germany": "Baller",
    "greece": "Asteromáta",
    "iceland": "Róa",
    "ireland": "Laika Party",
    "israel": "New Day Will Rise",
    "italy": "Volevo essere un duro",
    "latvia": "Bur man laimi",
    "lithuania": "Tavo akys",
    "luxembourg": "La poupée monte le son",
    "malta": "Serving",
    "montenegro": "Dobrodošli",
    "netherlands": "C'est la vie",
    "norway": "Lighter",
    "poland": "Gaja",
    "portugal": "Deslocado",
    "san marino": "Tutta l'Italia",
    "serbia": "Mila",
    "slovenia": "How Much Time Do We Have Left",
    "spain": "Esa diva",
    "sweden": "Bara bada bastu",
    "switzerland": "Voyage",
    "ukraine": "Bird of Pray",
    "united kingdom": "What the Hell Just Happened?"
}
SONG_URLS = {
    "albania": "https://www.youtube.com/watch?v=Sfvb761EEcM",
    "armenia": "https://www.youtube.com/watch?v=RfH5o3XtI2c",
    "australia": "https://www.youtube.com/watch?v=_08I6mjHSLA",
    "austria": "https://www.youtube.com/watch?v=-ieSTNpxvio",
    "azerbaijan": "https://www.youtube.com/watch?v=upbiPJ9uA70",
    "belgium": "https://www.youtube.com/watch?v=ScupiVTosHU",
    "croatia": "https://www.youtube.com/watch?v=ie_v6qGCc5w",
    "cyprus": "https://www.youtube.com/watch?v=rbfQqWyqgJw",
    "czechia": "https://www.youtube.com/watch?v=Hm8CIICKAJU",
    "denmark": "https://www.youtube.com/watch?v=gdCAgiSIOUc",
    "estonia": "https://www.youtube.com/watch?v=5MS_Fczs_98",
    "finland": "https://www.youtube.com/watch?v=Kg3QoTpnqyw",
    "france": "https://www.youtube.com/watch?v=Pj2DTSLcNnI",
    "georgia": "https://www.youtube.com/watch?v=c3wu0dUNd4c",
    "germany": "https://www.youtube.com/watch?v=zJplC4-9Scs",
    "greece": "https://www.youtube.com/watch?v=aDiq8J9h6vQ",
    "iceland": "https://www.youtube.com/watch?v=s9P83Nl6D1M",
    "ireland": "https://www.youtube.com/watch?v=cZnusVb7yjs",
    "israel": "https://www.youtube.com/watch?v=Q3BELu4z6-U",
    "italy": "https://www.youtube.com/watch?v=-Alz9MnqyZI",
    "latvia": "https://www.youtube.com/watch?v=RKw0OCgPV3s",
    "lithuania": "https://www.youtube.com/watch?v=R2f2aZ6Fy58",
    "luxembourg": "https://www.youtube.com/watch?v=LVHu_KwHiKY",
    "malta": "https://www.youtube.com/watch?v=sLVSwfRRvMA",
    "montenegro": "https://www.youtube.com/watch?v=ydMkpaB0CWk",
    "netherlands": "https://www.youtube.com/watch?v=hEHwr5k9pd0",
    "norway": "https://www.youtube.com/watch?v=pUjWzQ671MQ",
    "poland": "https://www.youtube.com/watch?v=YXHHDjiclxA",
    "portugal": "https://www.youtube.com/watch?v=-s1Cc2uEj3U",
    "san marino": "https://www.youtube.com/watch?v=Le3WpaLYRvE",
    "serbia": "https://www.youtube.com/watch?v=18BCbtvDcag",
    "slovenia": "https://www.youtube.com/watch?v=GT1YhfRpq3Q",
    "spain": "https://www.youtube.com/watch?v=BvVxhbCW9rw",
    "sweden": "https://www.youtube.com/watch?v=WK3HOMhAeQY",
    "switzerland": "https://www.youtube.com/watch?v=dGX54zRExR8",
    "ukraine": "https://www.youtube.com/watch?v=OJ1x2aiL7ks",
    "united kingdom": "https://www.youtube.com/watch?v=-hu6R3ZnOdY"
}
COUNTRIES = list(SONGS.keys())





class State:
    def __init__(self, chat_id) -> None:
        self.chat_id = chat_id
        if os.path.exists(path_for_chat_id(chat_id)):
            self.load_state()
            self.make_everything_int()
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

    def make_everything_int(self):
        if isinstance(self.current_picking_user, str):
            self.current_picking_user = int(self.current_picking_user)
        registered_users = { int(k): v for k, v in self.registered_users.items() }
        self.registered_users = registered_users
        for i in range(len(self.draft_order)):
            if isinstance(self.draft_order[i], str):
                self.draft_order[i] = int(self.draft_order[i])


def path_for_chat_id(chat_id):
    return 'state_' + str(chat_id) + '.json'

states = {}

def get_state_this_chat(update):
    chat_id = update.effective_chat.id
    if chat_id not in states.keys():
        states[chat_id] = State(chat_id)
        print("Created new state for chat " + str(chat_id))
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
    await update.message.reply_text(get_picked_countries(update), parse_mode=telegram.constants.ParseMode.HTML)


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
    if state.finished_registration:
        text = "Picks:\n"
    else:
        text = "Picks so far:\n"
    for user_id, user_name in state.registered_users.items():
        if isinstance(user_id, str):
            user_id = int(user_id)
        text += "\n<b>" + user_name + "</b>:"
        list_empty = True
        for country, picker_id in state.picked_countries.items():
            if picker_id == user_id:
                eliminated = country in SEMI_FINAL_ONE_ELIMINATED or country in SEMI_FINAL_TWO_ELIMINATED
                text += " "
                if eliminated:
                    text += "<s>"
                text += country.title() + " (" + COUNTRY_FLAGS[country] + ")"
                if eliminated:
                    text += "</s>"
                text += ","
                list_empty = False
        if not list_empty:
            text = text[:-1]
        else:
            text += " None!"
    if state.finished_registration:
        text += "\n<b>Not picked:</b>"
        for country in COUNTRIES:
            if country not in state.picked_countries.keys():
                text += " "
                eliminated = country in SEMI_FINAL_ONE_ELIMINATED or country in SEMI_FINAL_TWO_ELIMINATED
                if eliminated:
                    text += "<s>"
                text += country.title() + " (" + COUNTRY_FLAGS[country] + ")"
                if eliminated:
                    text += "</s>"
                text += ","
                if text[-1] == ",":
                    text = text[:-1]
    return text


async def pick_country_via_keyboard(update):
    state = get_state_this_chat(update)
    # create a sequence of buttons for each country that has not been picked yet
    entries = []
    for country in COUNTRIES:
        if country not in state.picked_countries.keys():
            entries.append(KeyboardButton(text="/pick " + country.title() + " " + COUNTRY_FLAGS[country]))
    
    keyboard = []
    if len(entries) % 2 == 0:
        # get two buttons per row
        keyboard = [entries[i:i+2] for i in range(0, len(entries), 2)]
    else:
        # get two buttons per row, except for the last row
        keyboard = [entries[i:i+2] for i in range(0, len(entries)-1, 2)]
        # add the last row
        keyboard.append([entries[-1]])

    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True)
    reply = await update.message.reply_text('Please pick a country:', reply_markup=reply_markup)
    print(reply)


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
    # if the message is just "/pick" (or /pick@....), send a keyboard with all the countries that have not been picked yet
    if len(update.message.text.split()) == 1 and update.message.text[:5] == "/pick":
        await pick_country_via_keyboard(update)
        return

    # remove the leading "/pick " from the message
    country = ""
    if len(update.message.text.split()) >= 2:
        country = update.message.text.split()[1].lower()

    # extract the country name from the COUNTRY_FLAGS dict
    if country in COUNTRY_FLAGS.values():
        country = [key for key, value in COUNTRY_FLAGS.items() if value == country][0]
    
    if country == "czech":
        country = "czech republic"
    if country == "united":
        country = "united kingdom"
    if country == "san":
        country = "san marino"

    if not country in COUNTRIES:
        await update.message.reply_text("Invalid country!")
        return
    if country in state.picked_countries:
        await update.message.reply_text(f"Country '{country.title()}' already picked!")
        return
    state.picked_countries[country] = update.effective_user.id

    flag = COUNTRY_FLAGS[country]
    song_title = SONGS[country]
    song_url = SONG_URLS[country]
    reply_text = update.effective_user.full_name +  " picked " + country.title() + " (" + flag + ") - " + song_title + " " + song_url + "."
    reply_text += "\n\nThere are " + str(state.picks - len(state.picked_countries)) + " countries left to pick (type \\still_to_pick to see them).\n"
    if len(state.picked_countries) == state.picks:
        reply_text += "\n\nDraft complete!"
        state.draft_complete = True
    else:
        reply_text += "\nThe next person to pick is " + get_next_picking_user(update)
    state.save_state()
    await update.message.reply_text(reply_text)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    message = "Welcome to the Eurovision Draft Bot! Type /help to see a list of commands.\n\n" + \
              "Each participant needs to register by typing /register. Once everyone has registered, type /end_registration to start the draft."
    await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    state = get_state_this_chat(update)
    message = "Commands:\n" + \
              "\\help - Show this message"
    if not state.finished_registration:
        message += "\\register - Register yourself in the draft\n" + \
                   "\\registered_users - See the list of registered users\n" \
                   "\\end_registration - End registration and start making picks\n"
    if state.finished_registration and not state.draft_complete:
        message += "\\pick [country] - Pick a country, where [country] is either the country name or the flag emoji\n" + \
                   "\\current_picks - See the current picks\n" + \
                   "\\still_to_pick - See the countries that are still to be picked\n" + \
                   "\\draft_order - See the draft order and who is currently picking and who is next to pick\n" + \
    await update.message.reply_text(message)


async def draft_order_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /draft_order is issued."""
    state = get_state_this_chat(update)
    if not state.finished_registration:
        await update.message.reply_text("Registration is not complete!")
    reply_text = "Draft order: "
    for user_id in state.draft_order:
        if isinstance(user_id, str):
            user_id = int(user_id)
        reply_text += "\n" + state.registered_users[user_id]
    reply_text += "\n\nCurrently picking: " + state.registered_users[state.current_picking_user]
    id_of_next_picking_user = state.draft_order[(state.draft_order.index(state.current_picking_user) + 1) % len(state.draft_order)]
    reply_text += "\nNext to pick: " + state.registered_users[id_of_next_picking_user]
    await update.message.reply_text(reply_text)

async def registered_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /registered_users is issued."""
    state = get_state_this_chat(update)
    if not state.finished_registration:
        await update.message.reply_text("Registration is not complete!")
    reply_text = "Registered users: "
    for user_id in state.registered_users:
        reply_text += "\n" + state.registered_users[user_id]
    await update.message.reply_text(reply_text)


async def semi_finals_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /semi_finals is issued."""
    state = get_state_this_chat(update)
    if not state.finished_registration:
        await update.message.reply_text("Registration is not complete!")
    non_picks = [ x for x in COUNTRIES if x not in state.picked_countries ]
    non_picks_semi_final_one = [ x for x in non_picks if x in SEMI_FINAL_ONE ]
    non_picks_semi_final_two = [ x for x in non_picks if x in SEMI_FINAL_TWO ]
    non_picks_final = [ x for x in non_picks if x not in SEMI_FINAL_ONE and x not in SEMI_FINAL_TWO ]

    reply_text = "\n<b><u>Semi-final 1 (Tuesday)</u></b>:"
    for id, name in state.registered_users.items():
        reply_text += "\n<b>" + name + "</b>: "
        picks = [ x for x in state.picked_countries if state.picked_countries[x] == id and x in SEMI_FINAL_ONE ]
        for pick in picks:
            eliminated = pick in SEMI_FINAL_ONE_ELIMINATED
            if eliminated:
                reply_text += "<s>"
            reply_text += pick.title() + " (" + COUNTRY_FLAGS[pick] + ")"
            if eliminated:
                reply_text += "</s>"
            reply_text += ", "
        if reply_text[-2:] == ", ":
            reply_text = reply_text[:-2]
    if non_picks_semi_final_one:
        reply_text += "\n<b>Not Picked</b>: "
        for country in non_picks_semi_final_one:
            reply_text += country.title() + " (" + COUNTRY_FLAGS[country] + "), "
        if reply_text[-2:] == ", ":
            reply_text = reply_text[:-2]

    reply_text += "\n\n\n<b><u>Semi-final 2 (Thursday)</u></b>:"
    for id, name in state.registered_users.items():
        reply_text += "\n<b>" + name + "</b>: "
        picks = [ x for x in state.picked_countries if state.picked_countries[x] == id and x in SEMI_FINAL_TWO ]
        for pick in picks:
            eliminated = pick in SEMI_FINAL_TWO_ELIMINATED
            if eliminated:
                reply_text += "</s>"
            reply_text += pick.title() + " (" + COUNTRY_FLAGS[pick] + ")"
            if eliminated:
                reply_text += "</s>"
            reply_text += ", "
        if reply_text[-2:] == ", ":
            reply_text = reply_text[:-2]
    if non_picks_semi_final_two:
        reply_text += "\n<b>Not Picked</b>: "
        for country in non_picks_semi_final_two:
            reply_text += country.title() + " (" + COUNTRY_FLAGS[country] + "), "
        if reply_text[-2:] == ", ":
            reply_text = reply_text[:-2]
    
    reply_text += "\n\n\n<b><u>Final</u></b>:"
    for id, name in state.registered_users.items():
        picks = [ x for x in state.picked_countries if state.picked_countries[x] == id and x not in SEMI_FINAL_ONE and x not in SEMI_FINAL_TWO ]
        if not picks:
            continue
        reply_text += "\n<b>" + name + "</b>: "
        for pick in picks:
            reply_text += pick.title() + " (" + COUNTRY_FLAGS[pick] + "), "
        if reply_text[-2:] == ", ":
            reply_text = reply_text[:-2]
    if non_picks_final:
        reply_text += "\n<b>Not Picked</b>: "
        for country in non_picks_final:
            reply_text += country.title() + " (" + COUNTRY_FLAGS[country] + "), "
        if reply_text[-2:] == ", ":
            reply_text = reply_text[:-2]

    await update.message.reply_text(reply_text, parse_mode=telegram.constants.ParseMode.HTML)


async def results_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /results is issued."""
    state = get_state_this_chat(update)
    if not state.finished_registration:
        await update.message.reply_text("Registration is not complete!")
    reply_text = "Results: "

    # winning pick
    points = { k: (v["jury"] + v["televote"]) for k,v in RESULTS.items() }
    max_points_country = max(points, key=points.get)
    picker_max_points_country = state.registered_users[state.picked_countries[max_points_country]]
    reply_text += "\n\n<b><u>Overall Winner</u></b>:"
    reply_text += "\n<b>" + picker_max_points_country + "</b>"

    # total points
    reply_text += "\n\n<b><u>Total Points</u></b>:"
    result_dict = {}
    for id, name in state.registered_users.items():
        points = 0
        picks = [ x for x in state.picked_countries if state.picked_countries[x] == id ]
        for pick in picks:
            if pick not in RESULTS:
                continue
            points += RESULTS[pick]["jury"] + RESULTS[pick]["televote"]
        result_dict[name] = points
    for name, points in sorted(result_dict.items(), key=lambda x: x[1], reverse=True):
        reply_text += "\n<b>" + name + "</b>: " + str(points) + " points"

    # jury - winning pick
    jury_points = { k: v["jury"] for k,v in RESULTS.items() }
    max_jury_points_country = max(jury_points, key=jury_points.get)
    picker_max_jury_points_country = state.registered_users[state.picked_countries[max_jury_points_country]]
    reply_text += "\n\n<b><u>Jury Vote Winner</u></b>:"
    reply_text += "\n<b>" + picker_max_jury_points_country + "</b>"

    # jury - most points
    reply_text += "\n\n<b><u>Jury Points</u></b>:"
    result_dict = {}
    for id, name in state.registered_users.items():
        points = 0
        picks = [ x for x in state.picked_countries if state.picked_countries[x] == id ]
        for pick in picks:
            if pick not in RESULTS:
                continue
            points += RESULTS[pick]["jury"]
        result_dict[name] = points
    for name, points in sorted(result_dict.items(), key=lambda x: x[1], reverse=True):
        reply_text += "\n<b>" + name + "</b>: " + str(points) + " points"

    # televote - winning pick
    televote_points = { k: v["televote"] for k,v in RESULTS.items() }
    max_televote_points_country = max(televote_points, key=televote_points.get)
    picker_max_televote_points_country = state.registered_users[state.picked_countries[max_televote_points_country]]
    reply_text += "\n\n<b><u>Televote Vote Winner</u></b>:"
    reply_text += "\n<b>" + picker_max_televote_points_country + "</b>"

    # televote - most points
    reply_text += "\n\n<b><u>Televote Points</u></b>:"
    result_dict = {}
    for id, name in state.registered_users.items():
        points = 0
        picks = [ x for x in state.picked_countries if state.picked_countries[x] == id ]
        for pick in picks:
            if pick not in RESULTS:
                continue
            points += RESULTS[pick]["televote"]
        result_dict[name] = points
    for name, points in sorted(result_dict.items(), key=lambda x: x[1], reverse=True):
        reply_text += "\n<b>" + name + "</b>: " + str(points) + " points"

    # most picks through to final
    reply_text += "\n\n<b><u>Most Picks Through to Final</u></b>:"
    pick_count = 0
    result_dict = {}
    for id, name in state.registered_users.items():
        picks = [ x for x in state.picked_countries if state.picked_countries[x] == id ]
        pick_count = len(picks)
        picks_not_eliminated = [ x for x in picks if x not in SEMI_FINAL_ONE_ELIMINATED and x not in SEMI_FINAL_TWO_ELIMINATED ]
        result_dict[name] = len(picks_not_eliminated)
    for name, countries_in_final in sorted(result_dict.items(), key=lambda x: x[1], reverse=True):
        reply_text += "\n<b>" + name + "</b>: " + str(countries_in_final) + " picks in final, " + str(pick_count - countries_in_final) + " picks eliminated"
    await update.message.reply_text(reply_text, parse_mode=telegram.constants.ParseMode.HTML)



def main() -> None:
    """Start the bot."""
    print("Running with token: " + TELEGRAM_TOKEN)
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()


    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("register", register_command))
    application.add_handler(CommandHandler("end_registration", end_registration_command))
    application.add_handler(CommandHandler("pick", pick_command))
    application.add_handler(CommandHandler("current_picks", current_picks_command))
    application.add_handler(CommandHandler("still_to_pick", still_to_pick_command))
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("draft_order", draft_order_command))
    application.add_handler(CommandHandler("registered_users", registered_users_command))
    application.add_handler(CommandHandler("semifinals", semi_finals_command))
    application.add_handler(CommandHandler("results", results_command))

    # Run the bot until the user presses Ctrl-C
    while True:
        try:
            application.run_polling()
        except Exception as e:
            pass


if __name__ == "__main__":
    main()