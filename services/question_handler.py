import threading
from queue import Queue
import time

class QuestionHandler:
    def __init__(self, tts_service):
        self.question_queue = Queue()
        self.tts_service = tts_service
        self.running = True

    def listen_for_questions(self):
        """Continuously listen for questions from the user."""
        while self.running:
            try:
                question = input("Enter a question (or leave blank to continue): ").strip()
                if question:
                    self.question_queue.put(question)
            except Exception as e:
                print(f"Error in listen_for_questions: {e}")

    def process_questions(self):
        """Process questions in the queue."""
        print("\n[Question] Processing queued questions.")
        while not self.question_queue.empty():
            question = self.question_queue.get()
            print(f"Student Question: {question}")
            time.sleep(1)
            self.tts_service.play("AI Answer: 'This is the AI-generated answer to your question.'")
            time.sleep(1)
