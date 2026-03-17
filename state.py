import os
import json
import glob
import random

# Global variable to hold the state of each chat. Key is chat_id, value is State object.
states = {}

class State:
    def __init__(self, chat_id) -> None:
        self._chat_id = chat_id
        if os.path.exists(path_for_chat_id(chat_id)):
            self.load_state()
        else:
            self._registered_users = {}
            self._current_picking_user = None
            self._picked_countries = {}
            self._finished_registration = False
            self._draft_complete = False
            self._draft_order = []
            self._picks = 0
            self._left_over = 0
            self.save_state()
    
    def save_state(self):
        with open(path_for_chat_id(self._chat_id), 'w') as outfile:
            json.dump(self.__dict__, outfile)
    
    def load_state(self):
        with open(path_for_chat_id(self._chat_id), 'r') as infile:
            self.__dict__ = json.load(infile)
    
    def is_registration_closed(self):
        return self._finished_registration
    
    def get_registered_users(self):
        for user_id, user_name in self._registered_users.items():
            if isinstance(user_id, str):
                user_id = int(user_id)
            yield user_id, user_name
    
    def get_registered_user_ids(self):
        for user_id in self._registered_users.keys():
            if isinstance(user_id, str):
                user_id = int(user_id)
            yield user_id
    
    def add_user(self, user_id, user_name):
        if isinstance(user_id, str):
            user_id = int(user_id)
        self._registered_users[user_id] = user_name
        self.save_state()
    
    def is_draft_complete(self):
        return self._draft_complete

    def get_user_name(self, user_id):
        if isinstance(user_id, str):
            user_id = int(user_id)
        if user_id not in self._registered_users.keys():
            return None
        return self._registered_users[user_id]
    
    def get_registered_user_count(self):
        return len(self._registered_users.keys())
    
    def end_user_registration(self):
        self._finished_registration = True
        self._shuffle_users_into_draft_order()
        self.save_state()
    
    def _shuffle_users_into_draft_order(self):
        self._draft_order = list(self._registered_users.keys()).copy()
        random.shuffle(self._draft_order)
        reversed = self.draft_order.copy()
        reversed.reverse()
        self._draft_order.extend(reversed)
        self.save_state()
    
    def get_draft_order_names(self):
        for user_id in self._draft_order:
            yield self.get_user_name(user_id)
    




# HELPER FUNCTIONS ----------------------------------------------------

def path_for_chat_id(chat_id):
    return 'states/state_' + str(chat_id) + '.json'


def get_state_this_chat(update):
    """How the rest of the system gets the relevant state for the chat. If it doesn't exist, create it."""
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