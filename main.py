from core.fsm import SlideNarrationFSM
from services.slide_control import SlideService
from services.tts import TTSService
from services.state_manager import StateManager
import threading

def listen_for_questions(slide_service, fsm):
    """Background thread for listening to questions."""
    while fsm.running:
        try:
            question = input("Enter a question (or leave blank to continue): ").strip()
            if question:
                slide_service.add_question(question)
        except KeyboardInterrupt:
            print("\nExiting...")
            fsm.running = False

if __name__ == "__main__":
    slide_service = SlideService()
    tts_service = TTSService()
    state_service = StateManager()

    fsm = SlideNarrationFSM(slide_service, tts_service, state_service)

    # Start a background thread for question listening
    threading.Thread(target=listen_for_questions, args=(slide_service, fsm), daemon=True).start()
    fsm.start()
