# services/question_handler.py
import time
from queue import Queue

from services.llm_services import OpenAILLM

class QuestionHandler:
    def __init__(self, tts_service):
        self.question_queue = Queue()
        self.tts_service = tts_service
        self.running = True
        self.llm = OpenAILLM()

    def enqueue_question(self, question):
        """Add a new question to the internal queue."""
        self.question_queue.put(question)

    def process_questions(self):
        """Process questions in the queue. This can be called periodically or in a dedicated thread."""
        while not self.question_queue.empty():
            question = self.question_queue.get()
            print(f"[QuestionHandler] Student Question: {question}")
            
            answer_text = self.llm.answer(question)
            # Text-to-speech or any other logic
            if not answer_text:
                answer_text = "no response"

            print(answer_text)
            #self.tts_service.play(answer_text)
            #self.tts_service.queue.join()
   
            #print(answer_text)

            return answer_text
