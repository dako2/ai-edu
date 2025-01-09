from google.oauth2 import service_account
from googleapiclient.discovery import build
from core.slide_data import SlideData  # Importing the unified data structure

class GoogleSlideService:
    def __init__(self, credentials_file, presentation_id):
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=["https://www.googleapis.com/auth/presentations"]
        )
        self.service = build('slides', 'v1', credentials=self.credentials)
        self.presentation_id = presentation_id

        # Fetch slide data as a list of SlideData instances
        self.slides = self.get_slides()
        self.total_slides = len(self.slides)

        

    def get_slides(self):
        """Fetch all slides in the presentation, including speaker notes and slide IDs."""
        presentation = self.service.presentations().get(
            presentationId=self.presentation_id
        ).execute()
        slides = presentation.get('slides', [])
        slide_data_list = []
        for idx, slide in enumerate(slides):
            speaker_notes = self._get_speaker_notes(slide)
            slide_obj = SlideData(
                slide_index=idx,
                object_id=slide.get('objectId'),  # Capture the real slide ID
                elements=slide.get('pageElements', []),
                speaker_notes=speaker_notes
            )
            slide_data_list.append(slide_obj)
        return slide_data_list

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

    def _add_speaker_notes(self, slide_id, notes):
        """Add speaker notes to a specific slide."""
        requests = [{
            'createShape': {
                'objectId': f"{slide_id}_notes",
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'height': {'magnitude': 100, 'unit': 'PT'},
                        'width': {'magnitude': 300, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': 100, 'translateY': 400,
                        'unit': 'PT'
                    }
                }
            }
        }, {
            'insertText': {
                'objectId': f"{slide_id}_notes",
                'text': notes
            }
        }]
        body = {'requests': requests}
        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id, body=body
        ).execute()

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
        
if __name__ == "__main__":

    credentials_file = "secrets/closeby-440718-dd98e45706c2.json"
    presentation_id = "1xyLjzu7KcvRCn5eDQmTCP_FanifShm9wPZwqyGgAq0E"

    # Instantiate mock services
    slide_service = GoogleSlideService(credentials_file, presentation_id)
    a = slide_service.slides[1].speaker_notes