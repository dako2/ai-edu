from flask import Flask, render_template, url_for, jsonify, request
import json

app = Flask(__name__)

# Load JSON data
with open('slides.json', 'r', encoding='utf-8') as file:
    slide_audio_mapping = json.load(file)

@app.route('/')
def index():
    return render_template('index.html', slides=slide_audio_mapping)

if __name__ == '__main__':
    app.run("0.0.0.0",port=8000,debug=True)
