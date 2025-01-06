import pyttsx3

class TTSService:
    def __init__(self):
        self.engine = pyttsx3.init()

    def play(self, text, slide_number):
        """
        Play the TTS audio for the given text and slide number.

        Args:
            text (str): The text to convert to speech.
            slide_number (int): The slide number being narrated.
        """
        print(f"\n[Slide {slide_number + 1}] Narrating: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
