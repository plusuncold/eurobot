import os
import json
import glob

# Global variable to hold the state of each chat. Key is chat_id, value is State object.
states = {}

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
    return 'states/state_' + str(chat_id) + '.json'


def get_state_this_chat(update):
    chat_id = update.effective_chat.id
    if chat_id not in states.keys():
        states[chat_id] = State(chat_id)
        print("Created new state for chat " + str(chat_id))
    return states[chat_id]


def load_all_states():
    # for every file that matches state*.json, load it
    for file in glob.glob("states/state_*.json"):
        chat_id = int(file[13:-5])
        states[chat_id] = State(chat_id)