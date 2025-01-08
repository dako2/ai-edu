from flask import Flask, Response, jsonify, request
from flask_socketio import SocketIO
from services.gslides import GoogleSlideService

app = Flask(__name__)

socketio = SocketIO(app, async_mode='threading')

# In-memory cache for slide data and current index
slide_cache = {}
current_slide_index = 0

service = GoogleSlideService(
    credentials_file="secrets/closeby-440718-dd98e45706c2.json",
    presentation_id="1xyLjzu7KcvRCn5eDQmTCP_FanifShm9wPZwqyGgAq0E"
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
    """
    Serve the main page with the current slide.
    """
    slides = slide_cache.get('slides', fetch_slides())

    # Fallback if out of range
    if current_slide_index < 0 or current_slide_index >= len(slides):
        actual_slide_id = slides[0]['objectId']
    else:
        actual_slide_id = slides[current_slide_index]['objectId']

    embed_url = (
        f"https://docs.google.com/presentation/d/{service.presentation_id}/embed"
        f"?start=false&loop=false&delayms=10#slide=id.{actual_slide_id}"
    )

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Google Slides Viewer</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; background-color: #f5f5f5; }}
        iframe {{ border: none; width: 100%; height: 600px; max-width: 900px; }}
    </style>
</head>
<body>
    <iframe id="slidesIframe" src="{embed_url}" allowfullscreen></iframe>
    <script src="https://cdn.jsdelivr.net/npm/socket.io-client/dist/socket.io.min.js"></script>

    <script>
        const socket = io();
        socket.on('slide_update', (data) => {{
            const iframe = document.getElementById('slidesIframe');
            iframe.src = `https://docs.google.com/presentation/d/{service.presentation_id}/embed?start=false&loop=false&delayms=10#slide=id.${{data.objectId}}`;
        }});
    </script>
</body>
</html>
    """
    return Response(html_content, mimetype='text/html')

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

if __name__ == '__main__':
    # Run the app with WebSocket support
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
