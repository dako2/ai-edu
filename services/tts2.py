import os
import json
from pathlib import Path
from queue import Queue
from threading import Thread
from dotenv import load_dotenv  # pip install python-dotenv
from playsound import playsound  # pip install playsound
from openai import OpenAI  # Replace with the actual OpenAI SDK

# Load environment variables
load_dotenv()

import os
import json
from pathlib import Path

class SpeakerNotesMapper:
    def __init__(self, speaker_notes, output_dir="assets/audio/"):
        """
        Initialize the SpeakerNotesMapper class.

        Args:
            speaker_notes (list): List of speaker notes as strings.
            output_dir (str): Directory to save the audio files.
        """
        self.speaker_notes = speaker_notes
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_mapping(self, speaker_notes):
        """Create an initial mapping between speaker notes and audio files."""
        mapping = []
        for i, note in enumerate(self.speaker_notes, start=1):
            audio_filename = f"speech_{i}.wav"
            mapping.append({
                "speaker_note": note,
                "audio_file": str(self.output_dir / audio_filename),
                "is_generated": False
            })
        return mapping

    def update_generation_status(self, speaker_note, status=True):
        """
        Update the generation status of a specific speaker note.

        Args:
            speaker_note (str): The speaker note whose status needs updating.
            status (bool): The generation status to set (default: True).
        """
        for item in self.mapping:
            if item["speaker_note"] == speaker_note:
                item["is_generated"] = status
                break

    def save_mapping_to_json(self, filename="mapping.json"):
        """
        Save the mapping to a JSON file.

        Args:
            filename (str): The name of the JSON file to save the mapping.
        """
        json_path = self.output_dir / filename
        with open(json_path, "w") as f:
            json.dump(self.mapping, f, indent=4)

    def load_mapping_from_json(self, filename="mapping.json"):
        """
        Load the mapping from a JSON file.

        Args:
            filename (str): The name of the JSON file to load the mapping from.
        """
        json_path = self.output_dir / filename
        if json_path.exists():
            with open(json_path, "r") as f:
                self.mapping = json.load(f)

    def get_mapping(self):
        """
        Get the current mapping.

        Returns:
            list: A list of dictionaries representing the mapping.
        """
        return self.mapping

class TTSGenerator:
    def __init__(self, api_key=None, model="tts-1", voice="alloy", output_dir="assets/audio/"):
        """
        Initialize the TTS generation service.
        """
        self.model = model
        self.voice = voice
        self.client = OpenAI()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tts_queue = Queue()
        self.json_file = self.output_dir / "tts_output.json"

        # Create or load JSON metadata file
        if not self.json_file.exists():
            with open(self.json_file, "w") as f:
                json.dump([], f)

        # Start TTS processing thread
        self.tts_worker_thread = Thread(target=self._process_tts_queue, daemon=True)
        self.tts_worker_thread.start()

    def add_to_queue(self, text, slide_index=None, elements=None):
        """Add a TTS task to the queue."""
        self.tts_queue.put({"text": text, "slide_index": slide_index, "elements": elements})

    def _process_tts_queue(self):
        """Process TTS queue to generate audio."""
        while True:
            item = self.tts_queue.get()
            if item is None:
                break

            self._generate_and_save_audio(item)
            self.tts_queue.task_done()

    def _generate_and_save_audio(self, item):
        """Generate and save audio using TTS."""
        try:
            text = item["text"]
            slide_index = item.get("slide_index")
            elements = item.get("elements")

            sequence = len(os.listdir(self.output_dir)) + 1
            audio_filename = f"speech_{slide_index}_{sequence}.wav"
            audio_path = self.output_dir / audio_filename

            # Hypothetical TTS API call
            response = self.client.audio.speech.create(
                model=self.model, voice=self.voice, input=text
            )
            response.stream_to_file(audio_path)

            # Save metadata to JSON
            self._update_json_file(slide_index, elements, text, str(audio_path))

        except Exception as e:
            print(f"Error generating audio: {e}")

    def _update_json_file(self, slide_index, elements, text, audio_path):
        """Update metadata JSON file."""
        with open(self.json_file, "r+") as f:
            data = json.load(f)
            data.append({
                "slide_index": slide_index,
                "elements": elements,
                "speaker_notes": text,
                "audio_path": audio_path
            })
            f.seek(0)
            json.dump(data, f, indent=4)

    def stop(self):
        """Stop the TTS generation thread."""
        self.tts_queue.put(None)
        self.tts_worker_thread.join()

class AudioPlayer:
    def __init__(self):
        """
        Initialize the audio playback service.
        """
        self.playback_queue = Queue()
        self.playback_worker_thread = Thread(target=self._process_playback_queue, daemon=True)
        self.playback_worker_thread.start()

    def add_to_queue(self, audio_path):
        """Add an audio file to the playback queue."""
        self.playback_queue.put(audio_path)

    def _process_playback_queue(self):
        """Process playback queue to play audio."""
        while True:
            audio_path = self.playback_queue.get()
            if audio_path is None:
                break

            self._play_audio(audio_path)
            self.playback_queue.task_done()

    def _play_audio(self, audio_path):
        """Play an audio file."""
        try:
            playsound(str(audio_path))
        except Exception as e:
            print(f"Error playing audio: {e}")

    def stop(self):
        """Stop the audio playback thread."""
        self.playback_queue.put(None)
        self.playback_worker_thread.join()


# ----------------------------------------------------------------------------
# Usage Example
# ----------------------------------------------------------------------------
# Example slide bring-up code with SpeakerNotesMapper and TTSGenerator integration
if __name__ == "__main__":
    # Example slide data
    slide_data = [
        {
            "slide_index": 1,
            "elements": ["Title", "Image"],
            "speaker_notes": "This is the introduction slide."
        },
        {
            "slide_index": 2,
            "elements": ["Bullet Points"],
            "speaker_notes": "Here are the key points of the presentation."
        },
        {
            "slide_index": 3,
            "elements": ["Chart"],
            "speaker_notes": "This slide shows the revenue chart."
        }
    ]

    # Extract speaker notes from slides
    speaker_notes = [slide["speaker_notes"] for slide in slide_data]

    # Initialize SpeakerNotesMapper
    mapper = SpeakerNotesMapper(speaker_notes, output_dir="./assets/audio/")

    # Load existing mapping from JSON if available
    mapper.load_mapping_from_json()

    # Initialize TTSGenerator
    tts_generator = TTSGenerator(api_key=os.getenv("OPENAI_API_KEY"), output_dir="./assets/audio/")

    # Process each speaker note
    for slide in slide_data:
        speaker_note = slide["speaker_notes"]

        # Check if audio has already been generated
        mapping_entry = next((item for item in mapper.get_mapping() if item["speaker_note"] == speaker_note), None)

        if mapping_entry and mapping_entry["is_generated"]:
            print(f"Audio already generated for slide {slide['slide_index']}: {mapping_entry['audio_file']}")
        else:
            print(f"Generating audio for slide {slide['slide_index']}: {speaker_note}")
            tts_generator.add_to_queue(
                text=speaker_note,
                slide_index=slide["slide_index"],
                elements=slide.get("elements")
            )
            # Mark the mapping entry as "is_generated" after TTS
            mapper.update_generation_status(speaker_note, status=True)

    # Wait for TTS queue to complete
    tts_generator.tts_queue.join()

    # Save updated mapping to JSON
    mapper.save_mapping_to_json()

    # Initialize audio player (optional: play audio files sequentially)
    from pathlib import Path

    mapper = SpeakerNotesMapper(speaker_notes, output_dir="./assets/audio/")
    mapper.load_mapping_from_json()
    audio_player = AudioPlayer()
    for mapping_entry in mapper.get_mapping():
        if mapping_entry["is_generated"]:
            audio_path = Path(mapping_entry["audio_file"])
            if audio_path.exists():
                audio_player.add_to_queue(audio_path)

    # Wait for playback queue to complete
    audio_player.playback_queue.join()

    # Stop services
    tts_generator.stop()
    audio_player.stop()
