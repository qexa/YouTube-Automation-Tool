import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from utils import generate_title, transcribe_audio, enhance_description, assign_playlist, generate_hierarchical_number, upload_video, extract_video_frame, create_thumbnail_from_frame, create_custom_thumbnail, thumbnail_to_base64, detect_language_from_audio, extract_audio_features

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
    try:
        audio_file = request.files['audio']
        language = request.form.get('language', 'en-US')
        auto_detect = request.form.get('auto_detect', 'false').lower() == 'true'
        
        # Auto-detect language if requested
        if auto_detect:
            detected_language = detect_language_from_audio(audio_file)
            language = detected_language
            # Reset file pointer after detection
            audio_file.seek(0)
        
        # Extract audio features
        features = extract_audio_features(audio_file)
        audio_file.seek(0)  # Reset file pointer
        
        # Transcribe audio with enhanced features
        result = transcribe_audio(audio_file, language=language)
        
        if len(result) == 5:
            transcription, summary, confidence, word_count, duration = result
        else:
            # Fallback for backward compatibility
            transcription, summary = result[:2]
            confidence, word_count, duration = 0.0, 0, 0
        
        return jsonify({
            "transcription": transcription,
            "summary": summary,
            "confidence": confidence,
            "word_count": word_count,
            "duration_seconds": duration,
            "detected_language": language,
            "audio_features": features
        })
        
    except Exception as e:
        return jsonify({
            "transcription": "Error occurred during transcription",
            "summary": "No summary available",
            "error": str(e),
            "confidence": 0.0
        })

@app.route('/detect_language', methods=['POST'])
def detect_language_route():
    try:
        audio_file = request.files['audio']
        detected_language = detect_language_from_audio(audio_file)
        return jsonify({"detected_language": detected_language})
    except Exception as e:
        return jsonify({"error": str(e), "detected_language": "en-US"})

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
    
    temp_path = f"temp_{video_file.filename}"
    video_file.save(temp_path)
    
    video_id = upload_video(title, description, tags, category_id, privacy_status, temp_path)
    
    os.remove(temp_path)
    
    if video_id:
        return jsonify({"success": True, "video_id": video_id})
    else:
        return jsonify({"success": False, "error": "Failed to upload video"})

@app.route('/generate_thumbnail_from_video', methods=['POST'])
def generate_thumbnail_from_video_route():
    try:
        video_file = request.files['video']
        title = request.form.get('title', '')
        timestamp = request.form.get('timestamp')
        
        if timestamp:
            timestamp = float(timestamp)
        else:
            timestamp = None
        
        # Save video temporarily
        temp_path = f"temp_{video_file.filename}"
        video_file.save(temp_path)
        
        # Extract frame
        frame = extract_video_frame(temp_path, timestamp)
        
        # Clean up temp file
        os.remove(temp_path)
        
        if frame is not None:
            # Create thumbnail
            thumbnail = create_thumbnail_from_frame(frame, title)
            if thumbnail:
                # Convert to base64 for web display
                thumbnail_b64 = thumbnail_to_base64(thumbnail)
                return jsonify({"success": True, "thumbnail": thumbnail_b64})
        
        return jsonify({"success": False, "error": "Failed to generate thumbnail from video"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/generate_custom_thumbnail', methods=['POST'])
def generate_custom_thumbnail_route():
    try:
        title = request.json.get('title', '')
        subtitle = request.json.get('subtitle', '')
        template = request.json.get('template', 'gradient')
        
        # Create custom thumbnail
        thumbnail = create_custom_thumbnail(title, subtitle, template)
        
        if thumbnail:
            # Convert to base64 for web display
            thumbnail_b64 = thumbnail_to_base64(thumbnail)
            return jsonify({"success": True, "thumbnail": thumbnail_b64})
        else:
            return jsonify({"success": False, "error": "Failed to generate custom thumbnail"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)