from queue import Queue

class SlideService:
    def __init__(self):
        self.slides = [
            "Introduction to Chemistry.",
            "The history of Alchemy and its transition to modern Chemistry.",
            "Key contributions of Mendeleev to the periodic table."
        ]
        self.question_queue = Queue()

    def total_slides(self):
        return len(self.slides)

    def get_slide(self, slide_number):
        return self.slides[slide_number] if 0 <= slide_number < len(self.slides) else None

    def add_question(self, question):
        self.question_queue.put(question)

    def get_question(self):
        return self.question_queue.get() if not self.question_queue.empty() else None

    def question_queue_empty(self):
        return self.question_queue.empty()

# Example usage
if __name__ == "__main__":
    slide_ctrl = SlideController()
    print(slide_ctrl.get_slide(1))  # Should print Slide 2 content
