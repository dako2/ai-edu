from flask import Flask, Response, jsonify, request, render_template
from flask_socketio import SocketIO
from services.google_slides import GoogleSlideService
from services.container import app, socketio, question_handler, slide_service
from flask import Response

# In-memory cache for slide data and current index
slide_cache = {}
current_slide_index = 0

service = slide_service

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
    Serve the main page with the current slide and a chatbox.
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
  <title>Google Slides Viewer with Chat</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      background-color: #f5f5f5;
    }}
    .container {{
      display: flex;
      height: 100vh;
    }}
    .slide-container {{
      flex: 2;
      padding: 10px;
    }}
    .chat-container {{
      flex: 1;
      display: flex;
      flex-direction: column;
      border-left: 1px solid #ccc;
      padding: 10px;
      background: #fff;
    }}
    iframe {{
      border: none;
      width: 100%;
      height: 100%;
    }}
    .messages {{
      flex: 1;
      overflow-y: auto;
      border: 1px solid #ddd;
      padding: 5px;
      margin-bottom: 10px;
    }}
    .input-group {{
      display: flex;
    }}
    .input-group input[type="text"] {{
      flex: 1;
      padding: 5px;
    }}
    .input-group button {{
      padding: 5px 10px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="slide-container">
      <iframe id="slidesIframe" src="{embed_url}" allowfullscreen></iframe>
    </div>
    <div class="chat-container">
      <div class="messages" id="messages"></div>
      <div class="input-group">
        <input type="text" id="questionInput" placeholder="Type your question..." />
        <button id="sendButton">Send</button>
      </div>
    </div>
  </div>
  
  <script src="https://cdn.jsdelivr.net/npm/socket.io-client/dist/socket.io.min.js"></script>
  <script>
    const socket = io();

    // Update slide when server notifies clients
    socket.on('slide_update', (data) => {{
      const iframe = document.getElementById('slidesIframe');
      iframe.src = `https://docs.google.com/presentation/d/{service.presentation_id}/embed?start=false&loop=false&delayms=10#slide=id.${{data.objectId}}`;
    }});

    // Chat functionality
    const messagesDiv = document.getElementById('messages');
    const questionInput = document.getElementById('questionInput');
    const sendButton = document.getElementById('sendButton');

    sendButton.addEventListener('click', () => {{
      const question = questionInput.value.trim();
      if (question) {{
        // Display the question in the chat window
        const msgElem = document.createElement('div');
        msgElem.textContent = "You: " + question;
        messagesDiv.appendChild(msgElem);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

        // Send the question to the server
        socket.emit('new_question', {{ question }});
        questionInput.value = '';
      }}
    }});

    // Handle receiving answers from the server
    socket.on('answer', (data) => {{
      const msgElem = document.createElement('div');
      msgElem.textContent = "Answer: " + data.answer;
      messagesDiv.appendChild(msgElem);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }});
  </script>
</body>
</html>
    """
    return Response(html_content, mimetype='text/html')

@socketio.on("new_question")
def handle_new_question(data):
    question = data.get("question")
    if question:
        question_handler.enqueue_question(question)
        print("here is the question answering pair")

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
