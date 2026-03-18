import os
import requests

COMMON_HEADER = "You are a _slightly_ toned down version of Graham Norton, the host of the Eurovision Song Contest. " + \
    "You are responding to a message from a user in a Telegram chat. "

LARGER_MODEL = "google/gemini-3-flash-preview"
SMALLER_MODEL = "google/gemini-3.1-flash-lite-preview"
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', "EMPTY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def get_llm_response(prompt, model):
    # Placeholder for LLM response generation logic
    # logs the prompt and the response from the openrouter API
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "EMPTY":
        return None
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    try:
        resp = requests.post(API_URL, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        log_request_and_response(prompt, content, model)
        return content
    except Exception as e:
        print(f"Error fetching LLM response: {e}")

    return "None"

def log_request_and_response(prompt, response, model):
    if not os.path.exists("llm_telegram.csv"):
        with open("llm_telegram.csv", "w") as log_file:
            log_file.write("prompt,response,model\n")
    with open("llm_telegram.csv", "a") as log_file:
        log_file.write(f'"{prompt.replace(chr(10), " ")}","{response.replace(chr(10), " ")}",{model}\n')


def is_llm_available():
    # Placeholder for logic to check if LLM is available
    return True


def get_user_intent(user_message, commands, user_is_registered, drafting_underway):
    commands_list = ", ".join(commands)
    llm_text = "Respond with the name of the command that best matches the user's intent. " + \
        "The user message is: \"" + user_message + "\"\n\n" + \
        "The commands are: " + commands_list + "\n" + \
        "The user is likely trying to interact with a Eurovision draft competition bot. " + \
        "If the user is just saying something that isn't a command, respond with 'None'. "
    if not user_is_registered:
        llm_text += "The user is not registered for the draft, so they are likely trying to register or asking for help. Interpret a 'hi' or 'hello' as an intent to register. "
    if drafting_underway:
        llm_text += "The draft is currently underway - the user is likely trying to pick a country - in which case return \"pick <country>\""

    response = get_llm_response(llm_text, SMALLER_MODEL)
    if not response in commands:
        if not response.startswith("pick "):
            return None
    return response


def get_banter_reply(user_message):
    llm_text = COMMON_HEADER + \
        "The user message is: " + user_message + "\n\n" + \
        "Respond with a witty, humorous, possibly slightly cheeky reply that Graham Norton might say. " + \
        "Keep to no more than about 100 characters. " + \
        "Make sure the reply is appropriate for a Telegram chat and does not contain any offensive content, or be risque."
    return get_llm_response(llm_text, LARGER_MODEL)

def get_boycott_reply(country):
    llm_text = COMMON_HEADER + \
        "The user has just tried to pick " + country.title() + ", but that country is boycotting Israel being" + \
        "in the competition, so they can't pick that country. " + \
        "Respond with a witty, humorous, possibly slightly cheeky reply that Graham Norton might say in response to this. " + \
        "Make sure the reply is appropriate for a Telegram chat and does not contain any offensive content, or be risque."
    return get_llm_response(llm_text, LARGER_MODEL)


def get_pick_reply(user_name, country, flag, song_title, song_url, song_detail):
    llm_text = COMMON_HEADER + \
        "The user " + user_name + " has just picked " + country.title() + " (" + flag + ") - " + song_title + ". " + \
        "The song details are: " + (song_detail if song_detail else "None") + ". " + \
        "The song URL is: " + (song_url if song_url else "None") + ". " + \
        "Respond with a witty, humorous, possibly slightly cheeky reply that Graham Norton might say in response to this pick. " + \
        "Make sure the reply is appropriate for a Telegram chat and does not contain any offensive content, or be risque."
    return get_llm_response(llm_text, LARGER_MODEL)