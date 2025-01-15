from flask import Flask, jsonify, render_template, request
from google_slides import GoogleSlideService

app = Flask(__name__, template_folder='templates')

# Configuration for Google Slides
SERVICE_ACCOUNT_FILE = "../source/secrets/closeby-440718-dd98e45706c2.json"  # Update with your file path
PRESENTATION_ID = '1cnaNzoYKHz2A-gbJ-9EJEaQT8L-uN2FDzNQOBy3lIbE'  # Default presentation ID

# Initialize the GoogleSlideService
slide_service = GoogleSlideService(
    credentials_file=SERVICE_ACCOUNT_FILE,
    presentation_id=PRESENTATION_ID
)

# In-memory cache for slides and current slide index
slide_cache = {"slides": []}
current_slide_index = 0

def fetch_slides():
    """
    Fetch slides from GoogleSlideService and cache them.
    """
    global slide_cache
    slide_cache['slides'] = slide_service.slides
    return slide_cache['slides']

@app.route('/')
def index():
    """
    Serve the main HTML page and pass the presentation ID to the template.
    """
    return render_template('index.html', presentation_id=PRESENTATION_ID)

@app.route('/set_slide_number/<int:slide>', methods=['POST'])
def set_slide_number(slide):
    """
    Update the current slide index and return the updated slide details.
    """
    global current_slide_index
    slides = slide_cache.get('slides', fetch_slides())

    if 0 <= slide < len(slides):
        current_slide_index = slide
        object_id = slides[slide]['object_id']
        speaker_notes = slides[slide].get('speakerNotes', '')
        return jsonify({
            "message": f"Slide index updated to {slide}",
            "slide": {
                "index": slide,
                "object_id": object_id,
                "se": speaker_notes
            }
        }), 200
    return jsonify({"error": "Invalid slide index"}), 400

@app.route('/get_slide_number', methods=['GET'])
def get_slide_number():
    """
    Get the current slide index and details.
    """
    global current_slide_index
    slides = slide_cache.get('slides', fetch_slides())

    if 0 <= current_slide_index < len(slides):
        slide = slides[current_slide_index]
        return jsonify({
            "index": current_slide_index,
            "objectId": slide['objectId'],
            "speakerNotes": slide.get('speakerNotes', '')
        }), 200
    return jsonify({"error": "Slide index out of range"}), 400

@app.route('/api/slides/<presentation_id>', methods=['GET'])
def api_get_slides(presentation_id):
    """
    API endpoint to fetch slide metadata.
    """
    try:
        slides = slide_service.slides
        return jsonify(slides=slides)
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(port=8000, debug=True)
