import os

def get_llm_response(prompt):
    # Placeholder for LLM response generation logic
    # logs the prompt and the response from the openrouter API
    
    return "None"


def is_llm_available():
    # Placeholder for logic to check if LLM is available
    return True


def get_user_intent(user_message, commands, user_is_registered):
    commands_list = ", ".join(commands)
    llm_text = "Respond with the name of the command that best matches the user's intent." + \
        "The user message is: " + user_message + "\n\n" + \
        "The commands are: " + commands_list + "\n" + \
        "The user is likely trying to interact with a Eurovision draft competition bot." + \
        "If the user is just saying something that isn't a command, respond with 'None'."
    if not user_is_registered:
        llm_text += "The user is not registered for the draft, so they are likely trying to register or asking for help."
    
    response = get_llm_response(llm_text)
    if not response in commands:
        return None
    return response


def get_banter_reply(user_message):
    llm_text = "You are a _slightly_ toned down version of Graham Norton, the host of the Eurovision Song Contest. " + \
        "You are responding to a message from a user in a Telegram chat. " + \
        "The user message is: " + user_message + "\n\n" + \
        "Respond with a witty, humorous, possibly slightly cheeky reply that Graham Norton might say. " + \
        "Make sure the reply is appropriate for a Telegram chat and does not contain any offensive content."
    return get_llm_response(llm_text)