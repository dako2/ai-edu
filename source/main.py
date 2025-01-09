import threading
from core.fsm import SlideNarrationFSM
from services.question_handler import QuestionHandler
from services.tts import TTSService
from services.google_slides import GoogleSlideService
from services.control_slide import ControlSlide

credentials_file = "secrets/closeby-440718-dd98e45706c2.json"
presentation_id = "1xyLjzu7KcvRCn5eDQmTCP_FanifShm9wPZwqyGgAq0E"

# Instantiate mock services
slide_service = GoogleSlideService(credentials_file, presentation_id)
tts_service = TTSService()

####
for data in slide_service.slides:
    audio_path = data.generate_and_attach_filename()
    res = tts_service.generate(data.speaker_notes, audio_path)
    print(f"generating wav file for slide {data.object_id} speaker notes {data.speaker_notes}")
    if res: 
        data.mark_as_generated()

from dataclasses import asdict
import json
slides_dict = [asdict(slide) for slide in slide_service.slides]
with open("slides_data.json", "w", encoding="utf-8") as f:
    json.dump(slides_dict, f, indent=4)
###
    

server_url = "http://localhost:5001"
control_slide = ControlSlide(server_url)  # Use ControlSlide with the Flask server URL

# Create the FSM and question handler
question_handler = QuestionHandler(tts_service)
fsm = SlideNarrationFSM(slide_service, tts_service, question_handler, control_slide)

# Start the question listener in a separate thread
question_listener_thread = threading.Thread(target=question_handler.listen_for_questions, daemon=True)
question_listener_thread.start()

# Run the FSM
try:
    fsm.start()
except KeyboardInterrupt:
    print("\n[Interrupt] Session terminated by the user.")
finally:
    # Stop the question handler gracefully
    question_handler.running = False
    question_listener_thread.join()
    print("Application exited.")
