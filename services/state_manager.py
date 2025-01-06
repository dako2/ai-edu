import json

class StateManager:
    def __init__(self, filename="fsm_state.json"):
        self.filename = filename

    def save(self, state):
        with open(self.filename, "w") as file:
            json.dump(state, file)
        print(f"State saved: {state}")

    def load(self):
        try:
            with open(self.filename, "r") as file:
                state = json.load(file)
                print(f"State loaded: {state}")
                return state
        except FileNotFoundError:
            print("No saved state found.")
            return None
