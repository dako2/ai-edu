class SlideNarrationFSM:
    def __init__(self, slide_service, tts_service, state_service):
        self.state = "START"
        self.current_slide = 0
        self.interrupt_flag = False
        self.running = True
        self.slide_service = slide_service
        self.tts_service = tts_service
        self.state_service = state_service

    def start(self):
        """Start the FSM."""
        self.load_state()
        print("Session Started.")
        
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
        
        self.current_slide = 1
        self.transition("SLIDE_NARRATION")
    
    def save_state(self):
        """Save the current state."""
        self.state_service.save({
            "state": self.state,
            "current_slide": self.current_slide,
        })

    def load_state(self):
        """Load the last saved state."""
        state = self.state_service.load()
        if state:
            self.state = state.get("state", "START")
            self.current_slide = state.get("current_slide", 0)
            print(f"State loaded: {state}")

    def slide_narration(self):
        """Handle slide narration."""
        while self.current_slide < self.slide_service.total_slides() and self.running:
            slide_text = self.slide_service.get_slide(self.current_slide)
            print(f"\n[Slide {self.current_slide + 1}] Narrating: {slide_text}")
            self.tts_service.play(slide_text, self.current_slide)

            if not self.slide_service.question_queue_empty():
                self.interrupt_flag = True
            else:
                self.interrupt_flag = False

            if self.interrupt_flag:
                self.transition("QUESTION")
                return

            self.current_slide += 1

        self.transition("END")

    def question(self):
        """Process questions."""
        print("\n[Question] Processing queued questions.")
        while not self.slide_service.question_queue_empty():
            question = self.slide_service.get_question()
            print(f"Question: {question}")
            print("Answer: 'This is the AI-generated answer.'")
        self.transition("RESUME")

    def resume(self):
        """Resume slide narration."""
        self.current_slide += 1

        print("\n[Resume] Resuming slide narration...")
        self.transition("SLIDE_NARRATION")

    def transition(self, next_state):
        """Handle state transitions."""
        print(f"\n[Transition] Moving from {self.state} to {next_state}.")
        self.state = next_state
        self.save_state()
        if self.state == "SLIDE_NARRATION":
            self.slide_narration()
        elif self.state == "QUESTION":
            self.question()
        elif self.state == "RESUME":
            self.resume()
        elif self.state == "END":
            self.running = False
            print("Session Ended.")
