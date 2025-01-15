from google.oauth2 import service_account
from googleapiclient.discovery import build
from core.slide_data import SlideData, SlideCollection

class GoogleSlideService:
    def __init__(self, credentials_file, presentation_id):
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=["https://www.googleapis.com/auth/presentations"]
        )
        self.service = build('slides', 'v1', credentials=self.credentials)
        # Fetch slide data as a list of SlideData instances
        self.slides = self.get_slides(presentation_id)
        self.total_slides = self.slides.len()

    def get_slides(self, presentation_id):        
        """Fetch all slides in the presentation, including speaker notes and slide IDs."""
        self.presentation_id = presentation_id
        self.presentation = self.service.presentations().get(
            presentationId=self.presentation_id
        ).execute()

        slides = self.presentation.get('slides', [])
        self.slide_data_list = SlideCollection()
        for idx, slide in enumerate(slides):
            speaker_notes = self._get_speaker_notes(slide)
            video_url = extract_video_url(slide)
            slide_obj = SlideData(
                presentation_id=presentation_id,
                slide_index=idx,
                object_id=slide.get('objectId'),  # Capture the real slide ID
                video_url=video_url,
                speaker_notes=speaker_notes
            )
            self.slide_data_list.add_slide(slide_obj)

        self.slide_data_list.save_to_json()

        return self.slide_data_list

    def _get_speaker_notes(self, slide):
        """Extract speaker notes from a slide."""
        text = ""
        notes_page = slide.get('slideProperties', {}).get('notesPage', {})
        notes_elements = notes_page.get('pageElements', [])
        for element in notes_elements:
            text_content = element.get('shape', {}).get('text', {}).get('textElements', [])
            for text_element in text_content:
                if 'textRun' in text_element:
                    text += text_element['textRun']['content']
        return text

    def get_speaker_notes_for_slide(self, slide_index):
        """Retrieve the speaker notes for a specific slide using unified structure."""
        if 0 <= slide_index < len(self.slide_data):
            return self.slide_data[slide_index].speaker_notes
        else:
            return {"error": "Invalid slide index."}

    def add_slide(self, slide_layout="TITLE_AND_BODY", speaker_notes=""):
        """Add a new slide with optional speaker notes."""
        requests = [{
            'createSlide': {
                'slideLayoutReference': {
                    'predefinedLayout': slide_layout
                }
            }
        }]
        body = {'requests': requests}
        response = self.service.presentations().batchUpdate(
            presentationId=self.presentation_id, body=body
        ).execute()

        # Add speaker notes to the newly created slide
        new_slide_id = response['replies'][0]['createSlide']['objectId']
        self._add_speaker_notes(new_slide_id, speaker_notes)
        return response

    def show_slide(self, slide_index, mode='embed'):
        """
        Return a URL that opens the presentation at the specified slide index.
        
        mode='editor' -> open in edit mode
        mode='published' -> open in published (embed) mode
        """
        try:
            presentation = self.service.presentations().get(
                presentationId=self.presentation_id
            ).execute()
            slides = presentation.get('slides', [])

            if slide_index < 0 or slide_index >= len(slides):
                print(f"Invalid slide index: {slide_index}. Total slides: {len(slides)}")
                return None

            slide_id = slides[slide_index]['objectId']
            if mode == 'editor':
                # Editor URL
                url = (
                    f"https://docs.google.com/presentation/d/{self.presentation_id}/edit"
                    f"#slide=id.{slide_id}"
                )
            else:
                # Published/Embed URL
                url = (
                    f"https://docs.google.com/presentation/d/{self.presentation_id}/embed"
                    f"?start=false&loop=false&delayms=3000#slide=id.{slide_id}"
                )

            print(f"Slide {slide_index + 1} has objectId={slide_id}")
            print(f"URL ({mode}): {url}")
            return url

        except Exception as e:
            print(f"Error showing slide: {e}")
            return None

def extract_video_url(slide):
    """
    Extract video URLs from a slide if present.
    """
    page_elements = slide.get('pageElements', [])
    for element in page_elements:
        video = element.get('video')
        if video and isinstance(video, dict):  # Ensure video is a dictionary
            # Extract the video URL (Google Drive preview or YouTube link)
            source_url = video.get('url')  # Adjust key based on actual structure
            if source_url:
                return source_url
    return None
    
if __name__ == "__main__":

    credentials_file = "../source/secrets/closeby-440718-dd98e45706c2.json"
    presentation_id = "1cnaNzoYKHz2A-gbJ-9EJEaQT8L-uN2FDzNQOBy3lIbE"

    # Instantiate mock services
    slide_service = GoogleSlideService(credentials_file, presentation_id)
