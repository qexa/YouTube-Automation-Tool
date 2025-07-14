import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from utils import generate_title, transcribe_audio, enhance_description, assign_playlist, generate_hierarchical_number, upload_video, extract_video_frame, create_thumbnail_from_frame, create_custom_thumbnail, thumbnail_to_base64, detect_language_from_audio, extract_audio_features, generate_video_tags, suggest_youtube_category, analyze_content_for_tags, analyze_content_for_playlists

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

@app.route('/manual')
def manual():
    return render_template('manual.html')

@app.route('/PRODUCT_MANUAL.md')
def download_manual():
    return app.send_static_file('../PRODUCT_MANUAL.md')

@app.route('/generate_title', methods=['POST'])
def generate_title_route():
    try:
        content = request.json['content']
        title_options = request.json.get('options', {})
        
        result = generate_title(content, title_options)
        
        return jsonify({
            "success": True,
            "titles": result['titles'],
            "analysis": result['analysis'],
            "recommendations": result['recommendations'],
            "engagement_insights": result.get('engagement_insights', [])
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "titles": ["Error generating titles"],
            "analysis": {},
            "recommendations": []
        })

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
    try:
        data = request.json
        content = data.get('content', '')
        video_content = data.get('video_content', '')
        
        # Get enhancement options from request
        enhancement_options = {
            'include_seo': data.get('include_seo', True),
            'include_hashtags': data.get('include_hashtags', True),
            'include_timestamps': data.get('include_timestamps', False),
            'include_social_links': data.get('include_social_links', True),
            'include_call_to_action': data.get('include_call_to_action', True),
            'target_audience': data.get('target_audience', 'general'),
            'video_category': data.get('video_category', 'general')
        }
        
        # Generate enhanced description
        enhanced_description = enhance_description(content, video_content, enhancement_options)
        
        # Extract additional insights for the response
        from utils import extract_advanced_keywords, categorize_content, extract_named_entities
        
        keywords = extract_advanced_keywords(video_content)
        topics = categorize_content(video_content)
        entities = extract_named_entities(video_content)
        
        return jsonify({
            "description": enhanced_description,
            "analysis": {
                "keywords": keywords[:10],
                "topics": topics,
                "entities": entities,
                "word_count": len(enhanced_description.split()),
                "estimated_read_time": len(enhanced_description.split()) // 200 + 1  # minutes
            }
        })
        
    except Exception as e:
        return jsonify({
            "description": content if 'content' in locals() else "Error occurred",
            "error": str(e)
        })

@app.route('/analyze_content', methods=['POST'])
def analyze_content_route():
    """Endpoint for content analysis without enhancement"""
    try:
        data = request.json
        content = data.get('content', '')
        
        from utils import extract_advanced_keywords, categorize_content, extract_named_entities
        
        keywords = extract_advanced_keywords(content)
        topics = categorize_content(content)
        entities = extract_named_entities(content)
        
        return jsonify({
            "keywords": keywords,
            "topics": topics,
            "entities": entities,
            "word_count": len(content.split()) if content else 0
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/assign_playlist', methods=['POST'])
def assign_playlist_route():
    """Enhanced playlist assignment endpoint with comprehensive SEO analysis"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'})
        
        content = data.get('content', data.get('transcription', ''))
        options = data.get('options', {})
        
        if not content:
            return jsonify({'error': 'Content is required for playlist assignment'})
        
        # Get comprehensive playlist assignment
        assignment_result = assign_playlist(content, options)
        
        if 'error' in assignment_result:
            return jsonify({'error': assignment_result['error']})
        
        return jsonify({
            'assignment': assignment_result,
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': f'Error assigning playlist: {str(e)}'})

@app.route('/analyze_playlist_content', methods=['POST'])
def analyze_playlist_content_route():
    """Endpoint for content analysis specifically for playlist assignment"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'})
        
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'Content is required for analysis'})
        
        analysis = analyze_content_for_playlists(content)
        
        return jsonify({
            'analysis': analysis,
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': f'Error analyzing content: {str(e)}'})

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

@app.route('/generate_tags', methods=['POST'])
def generate_tags_route():
    """Endpoint for intelligent video tag generation"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'Content is required for tag generation'})
        
        # Extract options from request
        options = {
            'max_tags': data.get('max_tags', 10),
            'include_keywords': data.get('include_keywords', True),
            'include_trending': data.get('include_trending', True),
            'include_long_tail': data.get('include_long_tail', True),
            'include_branded': data.get('include_branded', False),
            'language': data.get('language', 'en'),
            'category': data.get('category', 'auto')
        }
        
        # Generate tags
        tag_data = generate_video_tags(content, options)
        
        # Get category suggestion
        category_suggestion = suggest_youtube_category(content, tag_data.get('topics'))
        
        return jsonify({
            'tags': tag_data['tags'],
            'character_count': tag_data['character_count'],
            'seo_score': tag_data['seo_score'],
            'insights': tag_data['insights'],
            'category': category_suggestion,
            'analysis': {
                'topics': tag_data['topics'],
                'entities': tag_data['entities'],
                'tag_count': len(tag_data['tags'])
            }
        })
        
    except Exception as e:
        print(f"Error generating tags: {str(e)}")
        return jsonify({'error': f'Error generating tags: {str(e)}'})

@app.route('/suggest_category', methods=['POST'])
def suggest_category_route():
    """Endpoint for YouTube category suggestion"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'Content is required for category suggestion'})
        
        category_suggestion = suggest_youtube_category(content)
        
        return jsonify({
            'category': category_suggestion,
            'success': True
        })
        
    except Exception as e:
        print(f"Error suggesting category: {str(e)}")
        return jsonify({'error': f'Error suggesting category: {str(e)}'})

@app.route('/analyze_tags_content', methods=['POST'])
def analyze_tags_content_route():
    """Endpoint for content analysis specifically for tag generation"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'Content is required for analysis'})
        
        analysis = analyze_content_for_tags(content)
        
        return jsonify({
            'analysis': analysis,
            'success': True
        })
        
    except Exception as e:
        print(f"Error analyzing content for tags: {str(e)}")
        return jsonify({'error': f'Error analyzing content: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)