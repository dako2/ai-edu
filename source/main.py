import multiprocessing
from services.container import slide_service, tts_service, question_handler, control_slide
from core.fsm import SlideNarrationFSM

def run_fsm():
    """Function to initialize and start the FSM logic."""
    fsm = SlideNarrationFSM(slide_service, tts_service, question_handler, control_slide)
    fsm.start()
run_fsm()