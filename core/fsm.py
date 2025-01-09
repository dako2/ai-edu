import json
import time
import threading
from queue import Queue, Empty


class SlideNarrationFSM:
    SAVE_FILE = "assets/fsm_state.json"  # File to save the state

    def __init__(self, slide_service, tts_service, question_handler, control_slide):

        self.state = "START"

        self.slide_service = slide_service
        self.tts_service = tts_service
        self.control_slide = control_slide

        self.current_slide = 0
        self.total_slides = self.slide_service.total_slides
        self.speaker_notes = self.slide_service.speaker_notes
        self.slide_data = self.slide_service.slide_data

        self.interrupt_flag = False  # Flag to check if there are interruptions
        self.running = True  # Flag to manage the main loop

        self.question_handler = question_handler  # Queue to hold user questions

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
                if self.state == "END":
                    self.state = "START"
                    self.current_slide = 0
                    print(f"Restarting...")
        except FileNotFoundError:
            print("No saved state found. Starting from the beginning.")
            self.state = "START"
            self.current_slide = 0

    def start(self):
        print("Session Started.")
        self.load_state()  # Load saved state if available
        
        self.transition("SLIDE_NARRATION")

    def slide_narration(self):
        while self.current_slide < self.total_slides and self.running:

            slide_text = self.slide_service.speaker_notes[self.current_slide]
            print(f"\n[Slide {self.current_slide + 1}] Narrating: {slide_text}")
            
            
            self.control_slide.navigate_slide(self.current_slide)
            self.tts_service.play(slide_text)
            
            if not self.question_handler.question_queue.empty():
                self.interrupt_flag = True
            else:
                self.interrupt_flag = False #qi tang

            if self.interrupt_flag:
                self.transition("QUESTION")
                return  # Exit the loop to handle the question

            self.current_slide += 1  # Increment slide after narration completes

        self.transition("END")

    def question(self):
        self.question_handler.process_questions()
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
