from state import get_state_this_chat
from telegram import Update, ForceReply, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import telegram
import llm_telegram
from euro_information import *



# HELPER FUNCTIONS ----------------------------------------------------

def get_picked_countries(update):
    state = get_state_this_chat(update)
    if state.is_registration_closed():
        text = "Picks:\n"
    else:
        text = "Picks so far:\n"
    for user_id, user_name in state.get_registered_users():
        text += "\n<b>" + user_name + "</b>:"
        list_empty = True
        for country in state.get_picked_countries(user_id):
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
        text += "\n"
    if state.is_registration_closed():
        text += "\n<b>Not picked:</b>"
        for country in COUNTRIES:
            if not state.has_country_been_picked(country):
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
        if not state.has_country_been_picked(country):
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




# COMMANDS ----------------------------------------------------

def register_command_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /register is issued."""
    state = get_state_this_chat(update)
    if state.is_user_registered(update.effective_user.id):
        return "You are already registered!"
    state.add_user(update.effective_user.id, update.effective_user.full_name)
    return f"Hi {update.effective_user.full_name}, you are now registered for the Eurovision draft!"


async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_text = register_command_text(update, context)
    await update.message.reply_html(
        rf"{reply_text}",
        reply_markup=ForceReply(selective=True),
    )


def still_to_pick_command_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /still_to_pick is issued."""
    state = get_state_this_chat(update)
    if not state.is_registration_closed():
        return "Registration is not complete!"
    not_picked_countries = [ x for x in COUNTRIES if x not in state.get_all_picked_countries() ]
    reply_text = "Countries still to be picked:\n"
    for country in not_picked_countries:
        reply_text += f"{country.title()} {COUNTRY_FLAGS[country]} - {SONGS[country]}\n"
    return reply_text


async def still_to_pick_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /still_to_pick is issued."""
    reply_text = still_to_pick_command_text(update, context)
    await update.message.reply_text(reply_text)


def current_picks_command_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /current_picks is issued."""
    state = get_state_this_chat(update)
    if not state.is_registration_closed():
        return "Registration is not complete!"
    picked_countries_text = get_picked_countries(update)
    return picked_countries_text


async def current_picks_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /current_picks is issued."""
    reply_text = current_picks_command_text(update, context)
    await update.message.reply_text(reply_text, parse_mode=telegram.constants.ParseMode.HTML)


def wrap_user_message_as_link(state):
    current_picking_user_name = state.get_current_picking_user()
    current_picking_user_id = state.get_current_picking_user_id()
    return f"<a href=\"tg://user?id={current_picking_user_id}\">@{current_picking_user_name}</a>"

def end_registration_command_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /end_registration is issued."""
    state = get_state_this_chat(update)
    if state.get_registered_user_count() == 0:
        return "At least one person must be registered!"
    if state.is_registration_closed():
        return "Registration is already complete!"
    reply_text = "Registration is now finalized!\n"
    state.end_user_registration()

    reply_text += "\nDraft order: "
    for name in state.get_draft_order_names():
        reply_text += "\n" + name + ", "
    reply_text = reply_text[:-2] # remove the last comma and space
    reply_text += "\n\nThere are " + str(get_country_count()) + " countries to pick from.\n"
    reply_text += "\nThere will be a total of " + str(state.get_pick_count()) + " picks."
    reply_text += "\n\n" + str(state.get_left_over_count()) + " countries will be left over."
    reply_text += "\n\nFirst to pick is " + wrap_user_message_as_link(state) + "."
    return reply_text


async def end_registration_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_text = end_registration_command_text(update, context)
    await update.message.reply_text(reply_text)


def pick_command_text(update: Update, context: ContextTypes.DEFAULT_TYPE, llm: bool, country_from_llm: str) -> None:
    """Send a message when the command /pick is issued."""
    state = get_state_this_chat(update)
    if not state.is_registration_closed():
        return "Registration is not yet complete!"
    if not state.is_user_turn(update.effective_user.id):
        return f"It is {state.get_current_picking_user()}'s turn to pick!"
    if state.is_draft_complete():
        return "Draft is already complete!"
    # if the message is just "/pick" (or /pick@....), send a keyboard with all the countries that have not been picked yet
    if len(update.message.text.split()) == 1 and update.message.text[:5] == "/pick":
        if not llm:
            return None
        else:
            return "Error - shouldn't be here in LLM mode"

    # remove the leading "/pick " from the message
    country = ""
    if country_from_llm:
        country = country_from_llm.lower()
    elif len(update.message.text.split()) >= 2:
        country = update.message.text.split()[1].lower()

    # extract the country name from the COUNTRY_FLAGS dict
    country = convert_possible_emoji_to_country(country)
    country = convert_first_word_to_country(country)

    if not country in COUNTRIES:
        if country in BOYCOTT_COUNTRIES:
            return llm_telegram.get_boycott_reply(country)
        return "Invalid country!"
    if state.has_country_been_picked(country):
        return f"Country '{country.title()}' already picked!"
    
    state.set_picked_country(country, update.effective_user.id)

    flag = COUNTRY_FLAGS[country]
    song_title = SONGS[country]
    song_url = SONG_URLS[country] if country in SONG_URLS else None
    song_detail = get_song_detail(country)
    reply_text = update.effective_user.full_name +  " picked " + country.title() + " (" + flag + ") - " + song_title + " "
    if song_url:
        reply_text += song_url
    reply_text += ". "
    if llm:
        reply_text += llm_telegram.get_pick_reply(update.effective_user.full_name, country, flag, song_title, song_url, song_detail)
    reply_text += "\n\nThere are " + str(state.get_left_to_pick_country_count()) + " countries left to pick (type \\still_to_pick to see them).\n"
    if state.is_draft_complete():
        reply_text += "\n\nDraft complete!"
    else:
        reply_text += "\nThe next person to pick is " + wrap_user_message_as_link(state) + "."
    
    return reply_text


async def pick_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /pick is issued."""
    reply_text = pick_command_text(update, context, False, "")
    if not reply_text:
        # send a keyboard with all the countries that have not been picked yet
        await pick_country_via_keyboard(update)
        return
    await update.message.reply_text(reply_text)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    if llm_telegram.is_llm_available():
        message = f"Welcome to Eurovision {get_current_year()} Draft Bot!" + \
                   "You can type /help to see a list of commands or you can just talk to me and tell me what you want to do.\n\n" + \
                   "Each participant needs to register by typing /register or by just telling me that they want to register." + \
                   "Once everyone has registered, type /end_registration or just tell me to end registration to start the draft."
    else:
        message = f"Welcome to the Eurovision {get_current_year()} Draft Bot! Type /help to see a list of commands.\n\n" + \
                  "Each participant needs to register by typing /register. Once everyone has registered, type /end_registration to start the draft."
    await update.message.reply_text(message)


def help_command_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = get_state_this_chat(update)
    message = "Commands:\n" + \
              "\\help - Show this message"
    if not state.is_registration_closed():
        message += "\\register - Register yourself in the draft\n" + \
                   "\\registered_users - See the list of registered users\n" \
                   "\\end_registration - End registration and start making picks\n"
    if state.is_registration_closed() and not state.is_draft_complete():
        message += "\\pick [country] - Pick a country, where [country] is either the country name or the flag emoji\n" + \
                   "\\current_picks - See the current picks\n" + \
                   "\\still_to_pick - See the countries that are still to be picked\n" + \
                   "\\draft_order - See the draft order and who is currently picking and who is next to pick\n"
    if llm_telegram.is_llm_available():
        message += "\n\nYou can also just tell me what you want to do, for example 'I want to register for the draft' or 'Who is currently picking?'"
    return message
    

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    message = help_command_text(update, context)
    await update.message.reply_text(message)


def draft_order_command_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /draft_order is issued."""
    state = get_state_this_chat(update)
    if not state.is_registration_closed():
        return "Registration is not complete!"
    reply_text = "Draft order: "
    for user in state.get_draft_order_names():
        reply_text += "\n" + user
    reply_text += "\n\nCurrently picking: " + state.get_current_picking_user()
    next_to_pick = state.get_next_picking_user()
    if next_to_pick:
        reply_text += "\nNext to pick: " + state.get_next_picking_user()
    else:
        reply_text += "\nNo next picker (draft will be complete!)"
    return reply_text


async def draft_order_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /draft_order is issued."""
    reply_text = draft_order_command_text(update, context)
    await update.message.reply_text(reply_text)


def registered_users_command_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /registered_users is issued."""
    state = get_state_this_chat(update)
    reply_text = "Registered users: "
    for _, user_name in state.get_registered_users():
        reply_text += "\n" + user_name
    return reply_text


async def registered_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /registered_users is issued."""
    reply_text = registered_users_command_text(update, context)
    await update.message.reply_text(reply_text)


def semi_finals_command_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /semi_finals is issued."""
    state = get_state_this_chat(update)
    if not state.is_registration_closed():
        return "Registration is not complete!"
    non_picks = [ x for x in COUNTRIES if x not in state.picked_countries ]
    non_picks_semi_final_one = [ x for x in non_picks if x in SEMI_FINAL_ONE ]
    non_picks_semi_final_two = [ x for x in non_picks if x in SEMI_FINAL_TWO ]
    non_picks_final = [ x for x in non_picks if x not in SEMI_FINAL_ONE and x not in SEMI_FINAL_TWO ]

    def add_non_picks(text, list):
        if list:
            text += "\n<b>Not Picked</b>: "
            for country in list:
                text += country.title() + " (" + COUNTRY_FLAGS[country] + "), "
            if text[-2:] == ", ":
                text = text[:-2]
        return text
    
    def add_picks(text, state, full_list, eliminated_list):
        for id, name in state.get_registered_users():
            picks = [ x for x in state.get_picked_countries(id) if x in full_list ]
            if not picks:
                continue
            text += "\n<b>" + name + "</b>: "
            for pick in picks:
                eliminated = pick in eliminated_list
                if eliminated:
                    text += "<s>"
                text += pick.title() + " (" + COUNTRY_FLAGS[pick] + ")"
                if eliminated:
                    text += "</s>"
                text += ", "
            if text[-2:] == ", ":
                text = text[:-2]
        return text

    reply_text = "\n<b><u>Semi-final 1 (Tuesday)</u></b>:"
    reply_text = add_picks(reply_text, state, SEMI_FINAL_ONE, SEMI_FINAL_ONE_ELIMINATED)
    reply_text = add_non_picks(reply_text, non_picks_semi_final_one)

    reply_text += "\n\n\n<b><u>Semi-final 2 (Thursday)</u></b>:"
    reply_text = add_picks(reply_text, state, SEMI_FINAL_TWO, SEMI_FINAL_TWO_ELIMINATED)
    reply_text = add_non_picks(reply_text, non_picks_semi_final_two)
    
    reply_text += "\n\n\n<b><u>Final</u></b>:"
    combined_final_list = SEMI_FINAL_ONE + SEMI_FINAL_TWO
    reply_text = add_picks(reply_text, state, combined_final_list, [])
    reply_text = add_non_picks(reply_text, non_picks_final)
    return reply_text


async def semi_finals_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /semi_finals is issued."""
    reply_text = semi_finals_command_text(update, context)
    await update.message.reply_text(reply_text, parse_mode=telegram.constants.ParseMode.HTML)


def results_command_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /results is issued."""
    state = get_state_this_chat(update)
    if not state.is_registration_closed():
        return "Registration is not complete!"
    reply_text = "Results: "

    # winning pick
    points = { k: (v["jury"] + v["televote"]) for k,v in RESULTS.items() }
    max_points_country = max(points, key=points.get)
    picker_max_points_country = state.get_user_name_who_picked_country(max_points_country)
    reply_text += "\n\n<b><u>Overall Winner</u></b>:"
    reply_text += "\n<b>" + picker_max_points_country + "</b>"

    def get_winning_pick_text(reply_text, state, section):
        points = { k: v[section] for k,v in RESULTS.items() }
        max_points_country = max(points, key=points.get)
        picker_max_points_country = state.get_user_name_who_picked_country(max_points_country)
        reply_text += "\n\n<b><u>" + section.title() + " Winner</u></b>:"
        reply_text += "\n<b>" + picker_max_points_country + "</b>"
        return reply_text
    
    def get_most_points_text(reply_text, state, section):
        reply_text += "\n\n<b><u>" + section.title() + " Most Points</u></b>:"
        result_dict = {}
        for id, name in state.get_registered_users():
            points = 0
            for pick in state.get_picked_countries(id):
                if pick not in RESULTS:
                    continue
                if section == "total":
                    points += RESULTS[pick]["jury"] + RESULTS[pick]["televote"]
                else:
                    points += RESULTS[pick][section]
            result_dict[name] = points
        for name, points in sorted(result_dict.items(), key=lambda x: x[1], reverse=True):
            reply_text += "\n<b>" + name + "</b>: " + str(points) + " points"
        return reply_text

    reply_text = get_most_points_text(reply_text, state, "total")
    reply_text = get_winning_pick_text(reply_text, state, "jury")
    reply_text = get_most_points_text(reply_text, state, "jury")
    reply_text = get_winning_pick_text(reply_text, state, "televote")
    reply_text = get_most_points_text(reply_text, state, "televote")

    # most picks through to final
    reply_text += "\n\n<b><u>Most Picks Through to Final</u></b>:"
    pick_count = 0
    result_dict = {}
    for id, name in state.get_registered_users():
        picks = [ x for x in state.picked_countries if state.picked_countries[x] == id ]
        pick_count = len(picks)
        picks_not_eliminated = [ x for x in picks if x not in SEMI_FINAL_ONE_ELIMINATED and x not in SEMI_FINAL_TWO_ELIMINATED ]
        result_dict[name] = len(picks_not_eliminated)
    for name, countries_in_final in sorted(result_dict.items(), key=lambda x: x[1], reverse=True):
        reply_text += "\n<b>" + name + "</b>: " + str(countries_in_final) + " picks in final, " + str(pick_count - countries_in_final) + " picks eliminated"
    return reply_text


async def results_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /results is issued."""
    reply_text = results_command_text(update, context)
    await update.message.reply_text(reply_text, parse_mode=telegram.constants.ParseMode.HTML)


async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""

    if not update.message:
        return

    reply_text = "Sorry, I didn't understand that."
    user_is_registered = get_state_this_chat(update).is_user_registered(update.effective_user.id)
    state = get_state_this_chat(update)
    drafting_underway = state.is_registration_closed() and not state.is_draft_complete()
    user_intent = llm_telegram.get_user_intent(update.message.text, COMMANDS, user_is_registered, drafting_underway)

    if not user_intent:
        reply_text = llm_telegram.get_banter_reply(update.message.text)
    elif user_intent == "pick":
        if len(update.message.text.split()) >= 2:
            user_intent = update.message.text.split()[1].lower()
        elif len(update.message.text.split()) == 1:
            user_intent = "pick " + update.message.text.split()[0]
        else:
            await update.message.reply_text("Sorry, I didn't understand that.")
            return  
    
    for command_name, command_function in LLM_COMMANDS.items():
        if user_intent and user_intent.startswith("pick ") and command_name == "pick":
            reply_text = pick_command_text(update, context, True, user_intent[5:])
            break
        if user_intent == command_name:
            reply_text = command_function(update, context)

    await update.message.reply_text(reply_text, parse_mode=telegram.constants.ParseMode.HTML)



# COMMANDS
COMMANDS = {
    "register": register_command,
    "end_registration": end_registration_command,
    "pick": pick_command,
    "current_picks": current_picks_command,
    "still_to_pick": still_to_pick_command,
    "start": start_command,
    "help": help_command,
    "draft_order": draft_order_command,
    "registered_users": registered_users_command,
    "semifinals": semi_finals_command,
    "results": results_command
}

LLM_COMMANDS = {
    "register": register_command_text,
    "end_registration": end_registration_command_text,
    "pick": pick_command_text,
    "current_picks": current_picks_command_text,
    "still_to_pick": still_to_pick_command_text,
    "help": help_command_text,
    "draft_order": draft_order_command_text,
    "registered_users": registered_users_command_text,
    "semifinals": semi_finals_command_text,
    "results": results_command_text
}