import json
import time
import threading
from queue import Queue, Empty

class SlideNarrationFSM:
    SAVE_FILE = "fsm_state.json"  # File to save the state

    def __init__(self):
        self.state = "START"
        self.current_slide = 0
        self.total_slides = 3
        self.speaker_notes = self.load_speaker_notes()
        self.question_queue = Queue()  # Queue to hold user questions
        self.interrupt_flag = False  # Flag to check if there are interruptions
        self.running = True  # Flag to manage the main loop

    def load_speaker_notes(self):
        # Mock speaker notes for slides
        return [
            "Introduction to Chemistry.",
            "The history of Alchemy and its transition to modern Chemistry.",
            "Key contributions of Mendeleev to the periodic table."
        ]

    def save_state(self):
        """Save the current state to a file."""
        state_data = {
            "state": self.state,
            "current_slide": self.current_slide,
        }
        with open(self.SAVE_FILE, "w") as file:
            json.dump(state_data, file)
        print(f"State saved: {state_data}")

    def load_state(self):
        """Load the state from a file."""
        try:
            with open(self.SAVE_FILE, "r") as file:
                state_data = json.load(file)
                self.state = state_data.get("state", "START")
                self.current_slide = state_data.get("current_slide", 0)
                print(f"State loaded: {state_data}")
        except FileNotFoundError:
            print("No saved state found. Starting from the beginning.")
            self.state = "START"
            self.current_slide = 0

    def start(self):
        print("Session Started.")
        self.load_state()  # Load saved state if available

        # Allow user to choose starting slide
        user_choice = input("Do you want to (1) Resume from the last state or (2) Start from a specific slide? (Enter 1 or 2): ")
        if user_choice == "2":
            try:
                slide_number = int(input(f"Enter slide number (1-{self.total_slides}): ")) - 1
                if 0 <= slide_number < self.total_slides:
                    self.current_slide = slide_number
                else:
                    print("Invalid slide number. Starting from the beginning.")
            except ValueError:
                print("Invalid input. Starting from the beginning.")

        # Start a background thread to listen for questions
        threading.Thread(target=self.listen_for_questions, daemon=True).start()
        self.transition("SLIDE_NARRATION")

    def slide_narration(self):
        while self.current_slide < self.total_slides and self.running:
            print(f"\n[Slide {self.current_slide + 1}] Narrating: {self.speaker_notes[self.current_slide]}")
            for i in range(3):  # Simulate TTS streaming for 3 seconds
                print(f"Streaming TTS: '{self.speaker_notes[self.current_slide]}...' ({i+1}s)")
                time.sleep(1)  # Simulate real-time streaming
                
            if not self.question_queue.empty():
                self.interrupt_flag = True
            else:
                self.interrupt_flag = False #qi tang

            if self.interrupt_flag:
                self.transition("QUESTION")
                return  # Exit the loop to handle the question

            self.current_slide += 1  # Increment slide after narration completes

        self.transition("END")

    def question(self):
        print("\n[Question] Processing queued questions.")
        while not self.question_queue.empty():
            question = self.question_queue.get()
            print(f"Student Question: {question}")
            time.sleep(2)  # Simulate delay in AI response
            print("AI Answer: 'This is the AI-generated answer to your question.'")
            time.sleep(2)

        self.transition("RESUME")

    def resume(self):
        print("\n[Resume] Resuming slide narration...")
        self.current_slide += 1
        self.transition("SLIDE_NARRATION")

    def transition(self, next_state):
        print(f"\n[Transition] Moving from {self.state} to {next_state}.")
        self.state = next_state
        self.save_state()  # Save the state on every transition
        if self.state == "SLIDE_NARRATION":
            self.slide_narration()
        elif self.state == "QUESTION":
            self.question()
        elif self.state == "RESUME":
            self.resume()
        elif self.state == "END":
            self.running = False
            print("\nSession Ended. Thank you for participating!")

    def listen_for_questions(self):
        while self.running:
            try:
                question = input("Enter a question (or leave blank to continue): ").strip()
                if question:
                    self.question_queue.put(question)
            except Exception as e:
                print(f"Error in listen_for_questions: {e}")

# Main Program
if __name__ == "__main__":
    fsm = SlideNarrationFSM()
    fsm.start()
