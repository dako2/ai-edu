from flask import Flask, Response, jsonify, request, render_template
from flask_socketio import SocketIO
from services.google_slides import GoogleSlideService
import subprocess
from services.container import question_handler
from services.control_slide import ControlSlide

app = Flask(__name__)

socketio = SocketIO(app, async_mode='threading')

# In-memory cache for slide data and current index
slide_cache = {}
current_slide_index = 0

service = GoogleSlideService(
    credentials_file="secrets/closeby-440718-dd98e45706c2.json",
    presentation_id="1cnaNzoYKHz2A-gbJ-9EJEaQT8L-uN2FDzNQOBy3lIbE"
)

def fetch_slides():
    """
    Fetch slide metadata from Google Slides API and update the cache.
    """
    presentation = service.service.presentations().get(
        presentationId=service.presentation_id
    ).execute()
    slides = presentation.get('slides', [])
    slide_cache['slides'] = [{"objectId": slide['objectId']} for slide in slides]
    return slide_cache['slides']

@app.route('/update_cache', methods=['GET'])
def update_cache():
    """
    Update the slide cache by fetching metadata from Google Slides API.
    """
    slides = fetch_slides()
    return jsonify({"message": "Cache updated", "slides": slides})
 
@app.route('/')
def index():
    slides = slide_cache.get('slides', fetch_slides())

    # Fallback if out of range
    if current_slide_index < 0 or current_slide_index >= len(slides):
        actual_slide_id = slides[0]['objectId']
    else:
        actual_slide_id = slides[current_slide_index]['objectId']

    # Determine actual_slide_id as before...
    embed_url = (
        f"https://docs.google.com/presentation/d/{service.presentation_id}/embed"
        f"?start=false&loop=false&delayms=10#slide=id.{actual_slide_id}"
    )
    return render_template('index.html', embed_url=embed_url, presentation_id=service.presentation_id)

@app.route('/set_slide_number/<int:slide>', methods=['POST'])
def set_slide_number(slide):
    """
    Update the current slide index and notify clients via WebSocket.
    """
    global current_slide_index
    slides = slide_cache.get('slides', fetch_slides())

    if 0 <= slide < len(slides):
        current_slide_index = slide
        object_id = slides[slide]['objectId']
        socketio.emit('slide_update', {'index': slide, 'objectId': object_id})
        return jsonify({"message": f"Slide index updated to {slide}"})
    return jsonify({"error": "Invalid slide index"}), 400

@app.route('/get_slide_index', methods=['GET'])
def get_slide_index():
    """
    Return the current slide index as JSON.
    """
    global current_slide_index
    return jsonify({"slideIndex": current_slide_index})

@app.route('/new_question', methods=['POST'])
def new_question():
    data = request.get_json()  # Expecting JSON data from the client
    question = data.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400
    print(f"Received new question: {question}")
    # Enqueue the question to be processed by QuestionHandler
    question_handler.enqueue_question(question)
    # Process the question immediately (optional synchronous processing)
    answer = question_handler.process_questions()
    
    # Respond with the answer
    return jsonify({"answer": answer})
 
"""
@app.route('/start', methods=['POST'])
def start_main():
    try:
        # Start main.py using subprocess
        process = subprocess.Popen(["python", "main.py"])
        return jsonify({"message": "main.py started", "pid": process.pid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500"""

server_url = "http://localhost:8000"
control_slide = ControlSlide(server_url)

@app.route('/api/slides', methods=['GET'])
def get_slides():
    slides_data = [{
        'speakerNotes': slide.speaker_notes
    } for slide in service.slides]
    return jsonify({
        'slides': slides_data,
        'totalSlides': len(slides_data)
    })

if __name__ == '__main__':
    # Run the app with WebSocket support
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)