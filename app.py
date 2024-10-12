import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from utils import generate_title, transcribe_audio, enhance_description, assign_playlist, generate_hierarchical_number

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///youtube_automation.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

with app.app_context():
    import models
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_title', methods=['POST'])
def generate_title_route():
    content = request.json['content']
    title = generate_title(content)
    return jsonify({"title": title})

@app.route('/transcribe', methods=['POST'])
def transcribe_route():
    audio_file = request.files['audio']
    transcription, summary = transcribe_audio(audio_file)
    return jsonify({"transcription": transcription, "summary": summary})

@app.route('/enhance_description', methods=['POST'])
def enhance_description_route():
    content = request.json['content']
    enhanced_description = enhance_description(content)
    return jsonify({"description": enhanced_description})

@app.route('/assign_playlist', methods=['POST'])
def assign_playlist_route():
    transcription = request.json['transcription']
    playlist = assign_playlist(transcription)
    return jsonify({"playlist": playlist})

@app.route('/generate_number', methods=['POST'])
def generate_number_route():
    video_type = request.json['video_type']
    parent_number = request.json.get('parent_number')
    number = generate_hierarchical_number(video_type, parent_number)
    return jsonify({"number": number})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
