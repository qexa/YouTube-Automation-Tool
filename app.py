import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from utils import generate_title, transcribe_audio, enhance_description, assign_playlist, generate_hierarchical_number, upload_video

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
    video_content = request.json['video_content']
    enhanced_description = enhance_description(content, video_content)
    return jsonify({"description": enhanced_description})

@app.route('/assign_playlist', methods=['POST'])
def assign_playlist_route():
    transcription = request.json['transcription']
    playlist, certainty = assign_playlist(transcription)
    return jsonify({"playlist": playlist, "certainty": certainty})

@app.route('/generate_number', methods=['POST'])
def generate_number_route():
    video_type = request.json['video_type']
    parent_number = request.json.get('parent_number')
    number = generate_hierarchical_number(video_type, parent_number)
    return jsonify({"number": number})

@app.route('/upload_video', methods=['POST'])
def upload_video_route():
    title = request.form['title']
    description = request.form['description']
    tags = request.form['tags'].split(',')
    category_id = request.form['category_id']
    privacy_status = request.form['privacy_status']
    video_file = request.files['video']
    
    # Save the video file temporarily
    temp_path = f"temp_{video_file.filename}"
    video_file.save(temp_path)
    
    video_id = upload_video(title, description, tags, category_id, privacy_status, temp_path)
    
    # Remove the temporary file
    os.remove(temp_path)
    
    if video_id:
        return jsonify({"success": True, "video_id": video_id})
    else:
        return jsonify({"success": False, "error": "Failed to upload video"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
