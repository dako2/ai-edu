# services/container.py
from services.tts_offline import TTSService
from services.question_handler import QuestionHandler
from services.google_slides import GoogleSlideService
#from services.pptx_slides import PptxSlideService
from services.control_slide import ControlSlide

server_url = "http://localhost:8000"
control_slide = ControlSlide(server_url)
#from services.control_ppt import ControlSlide

#pptx_file = "/Users/dako22/Downloads/test_full.pptx"  # Replace with your pptx path
#control_slide = ControlSlide(pptx_file)

tts_service = TTSService()

question_handler = QuestionHandler(tts_service)

slide_service = GoogleSlideService(
    credentials_file="secrets/closeby-440718-dd98e45706c2.json",
    presentation_id="1cnaNzoYKHz2A-gbJ-9EJEaQT8L-uN2FDzNQOBy3lIbE"
)

#pptx_file = "/Users/dako22/Downloads/test_full.pptx"
#slide_service = PptxSlideService(pptx_file)

