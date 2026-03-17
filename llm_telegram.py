import os


def can_handle_banter():
    return os.environ.get('LLM_BANTER', "False").lower() == "true"

def get_user_intent(user_message, commands):
    commands_list = ", ".join(commands)
    llm_text = "Respond with the name of the command that best matches the user's intent." \
        "The user message is: " + user_message + "\n\n" \
        "The commands are: " + commands_list + "\n" \
        "The user is likely trying to interact with a Eurovision draft competition bot." \
        "If the user is just saying something that isn't a command, respond with 'None'."
    
    response = get_llm_response(llm_text)
    if not response in commands:
        return None
    return response

