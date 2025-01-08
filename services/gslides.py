from google.oauth2 import service_account
from googleapiclient.discovery import build

class GoogleSlideService:
    def __init__(self, credentials_file, presentation_id):
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=["https://www.googleapis.com/auth/presentations"]
        )
        self.service = build('slides', 'v1', credentials=self.credentials)
        self.presentation_id = presentation_id

        self.total_slides = self.total_slides()

        ##qi tang WIP
        self.slide_data = self.get_slides()
        self.speaker_notes = [x["speaker_notes"] for x in self.slide_data]

    def get_slides(self):
        """Fetch all slides in the presentation, including speaker notes."""
        presentation = self.service.presentations().get(presentationId=self.presentation_id).execute()
        slides = presentation.get('slides', [])
        slide_data = []
        for idx, slide in enumerate(slides):
            speaker_notes = self._get_speaker_notes(slide)
            slide_data.append({
                "slide_index": idx,
                "elements": slide.get('pageElements', []),
                "speaker_notes": speaker_notes
            })
        return slide_data

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

    def total_slides(self):
        """Return the total number of slides in the presentation."""
        slides = self.get_slides()
        return len(slides)

    def get_speaker_notes(self, slide_index):
        """Retrieve the speaker notes for a specific slide."""
        slides = self.get_slides()
        if 0 <= slide_index < len(slides):
            return slides[slide_index]['speaker_notes']
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
            presentationId=self.presentation_id, body=body).execute()

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
            presentationId=self.presentation_id, body=body).execute()

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
            slides = presentation['slides']

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
