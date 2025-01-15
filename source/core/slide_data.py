from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Any, Optional
import json
#from services.tts_offline import TTSService
from services.tts import TTSService

@dataclass
class SlideData:
    presentation_id: str
    slide_index: int
    object_id: Optional[str] = None  # New field for real slide ID
    speaker_notes: str = ""
    video_url: str = ""
    audio_file: Optional[Path] = None
    is_generated: bool = False

    def generate_and_attach_filename(self, output_dir="services/assets/audio/", extension="mp3") -> str:
        """
        Generate a filename based on the slide_index and attach it to the slide data.
        Returns the full path as a string.
        """
        filename = f"openai_{self.presentation_id}_{self.slide_index}_{self.object_id}.{extension}"
        full_path = output_dir + filename
        self.audio_file = full_path
        return self.audio_file

    def mark_as_generated(self):
        """Mark the slide's audio as generated."""
        self.is_generated = True

class SlideCollection:
    def __init__(self, slides: Optional[List[SlideData]] = None):
        self.slides: List[SlideData] = slides if slides is not None else []
    
    def len(self):
        return len(self.slides)
    
    def add_slide(self, slide: SlideData):
        self.slides.append(slide)

    def remove_slide(self, index: int):
        if 0 <= index < len(self.slides):
            self.slides.pop(index)

    def tts(self):
        for slide in self.slides:
            tts_service = TTSService()
            if slide.speaker_notes and not slide.is_generated:
                tts_service.offline(slide.speaker_notes, slide.generate_and_attach_filename())
                slide.mark_as_generated()

    def save_to_json(self, filepath: Path = "services/assets/google_slides_temp.json"):
        """
        Save the current slide collection to a JSON file.
        Converts Path objects to strings for JSON serialization.
        """
        # Convert each SlideData to a dict, converting audio_file to string if present
        slides_as_dicts = []
        for slide in self.slides:
            slide_dict = asdict(slide)
            # Convert Path to string for JSON serialization
            if slide_dict.get("audio_file") is not None:
                slide_dict["audio_file"] = str(slide_dict["audio_file"])
            slides_as_dicts.append(slide_dict)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(slides_as_dicts, f, indent=4)

    @classmethod
    def load_from_json(cls, filepath: Path) -> "SlideCollection":
        """
        Load a slide collection from a JSON file.
        Converts audio_file paths from strings back to Path objects.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        slides = []
        for slide_data in data:
            # Convert audio_file back to Path if it exists
            if slide_data.get("audio_file"):
                slide_data["audio_file"] = Path(slide_data["audio_file"])
            slides.append(SlideData(**slide_data))

        return cls(slides)

    def get_slide_by_index(self, index: int) -> Optional[SlideData]:
        """Retrieve a slide by its index."""
        if 0 <= index < len(self.slides):
            return self.slides[index]
        return None
