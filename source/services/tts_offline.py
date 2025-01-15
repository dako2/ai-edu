import threading
from queue import Queue
import tempfile
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

class TTSService:
    def __init__(self):
        # Initialize a thread-safe queue to hold TTS requests
        self.queue = Queue()
        # Start a dedicated worker thread to process the queue
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def play(self, text, lang='zh'):
        """
        Public method to enqueue a new TTS request.
        """
        self.queue.put((text, lang))

    def offline(self, text, audio_path, lang='zh'):
        """
        Generate a speech audio file from the provided text and save it offline.
        Returns a list of audio file paths (in this case, just one path).
        """
       #audio_files = []
        try:
            # Generate speech using gTTS with the specified language
            tts = gTTS(text=text, lang=lang)
            # Save the audio file to the specified path
            tts.save(audio_path)
            # Add the saved file path to the list
            #audio_files.append(audio_path)
        except Exception as e:
            print(f"Error during offline TTS generation: {e}")
        return audio_path

    def _worker(self):
        """
        The worker method runs in a separate thread, processing TTS
        requests from the queue sequentially.
        """
        while True:
            # Block until an item is available in the queue
            text, lang = self.queue.get()
            try:
                # Generate speech using gTTS
                tts = gTTS(text=text, lang=lang)
                # Create a temporary file to save the audio
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as f:
                    temp_file = f.name
                    tts.save(temp_file)

                    # Load the audio file using pydub
                    sound = AudioSegment.from_file(temp_file, format="mp3")
                    # Play the audio synchronously (blocking call)
                    play(sound)
            except Exception as e:
                print(f"Error during TTS playback: {e}")
            finally:
                # Signal that the current queue task is complete
                self.queue.task_done()

# Example usage:
if __name__ == "__main__":
    tts_manager = TTSService()
    
    # Enqueue multiple speech requests
    tts_manager.play("Hello world!")
    tts_manager.play("This will be played after the first utterance.")
    tts_manager.play("Each message is queued and played sequentially.")
    
    # Optionally wait for the queue to be empty before exiting:
    tts_manager.queue.join()  # Blocks until all tasks are done
