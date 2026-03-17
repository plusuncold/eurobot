import os

def get_llm_response(prompt):
    # Placeholder for LLM response generation logic
    return "None"


def is_llm_available():
    # Placeholder for logic to check if LLM is available
    return True

def can_handle_banter():
    return os.environ.get('LLM_BANTER', "False").lower() == "true"


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

