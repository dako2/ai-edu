class TTSService:
    def __init__(self):
        import pyttsx3
        self.engine = pyttsx3.init()
        # Set the speaking rate (optional)
        self.engine.setProperty('rate', 180)  # Adjust the rate as needed
        # Select a Chinese voice (adjust index based on the voice list)
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'zh' in voice.id:  # Check for Chinese voice
                self.engine.setProperty('voice', voice.id)
                break

    def play(self, text):
        """
        Play the TTS audio for the given text and slide number.

        Args:
            text (str): The text to convert to speech.
            slide_number (int): The slide number being narrated.
        """
        print(f"\n[Slide Narrating: {text}")
        self.engine.say(text)
        self.engine.runAndWait()


