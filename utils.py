import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import random
import speech_recognition as sr
from pydub import AudioSegment
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except Exception as e:
    print(f"Error downloading NLTK data: {str(e)}")

def generate_title(content):
    try:
        words = word_tokenize(content.lower())
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
        word_freq = nltk.FreqDist(filtered_words)
        common_words = word_freq.most_common(3)
        title = " ".join(word for word, _ in common_words).capitalize()
        return title
    except Exception as e:
        print(f"Error generating title: {str(e)}")
        return "Unable to generate title"

def transcribe_audio(audio_file, language='en-US', enable_confidence=True):
    """Enhanced audio transcription with confidence scores and language support"""
    try:
        # Convert audio to appropriate format
        audio = AudioSegment.from_file(audio_file)
        
        # Normalize audio (improve quality)
        audio = audio.set_frame_rate(16000)
        audio = audio.set_channels(1)
        
        # Export to temporary file
        temp_file = "temp_audio.wav"
        audio.export(temp_file, format="wav")

        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8
        
        transcription_data = {}
        
        with sr.AudioFile(temp_file) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio_data = recognizer.record(source)
            
            try:
                # Primary transcription with Google
                transcription = recognizer.recognize_google(
                    audio_data, 
                    language=language,
                    show_all=enable_confidence
                )
                
                if enable_confidence and isinstance(transcription, dict):
                    # Extract best alternative
                    if 'alternative' in transcription and transcription['alternative']:
                        best_result = transcription['alternative'][0]
                        transcription_text = best_result.get('transcript', '')
                        confidence = best_result.get('confidence', 0.0)
                    else:
                        transcription_text = ''
                        confidence = 0.0
                else:
                    transcription_text = transcription if isinstance(transcription, str) else ''
                    confidence = 0.85  # Default confidence for simple mode
                
            except sr.UnknownValueError:
                transcription_text = ''
                confidence = 0.0
            except sr.RequestError as e:
                print(f"Google Speech Recognition service error: {e}")
                transcription_text = ''
                confidence = 0.0
        
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        if not transcription_text:
            return "Unable to transcribe audio - no speech detected", "No summary available", 0.0
        
        # Generate intelligent summary
        summary = generate_intelligent_summary(transcription_text)
        
        # Extract metadata
        word_count = len(transcription_text.split())
        duration_seconds = len(audio) / 1000.0
        
        return transcription_text, summary, confidence, word_count, duration_seconds
        
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        return "Unable to transcribe audio", "No summary available", 0.0, 0, 0

def generate_intelligent_summary(text, max_sentences=3):
    """Generate an intelligent summary using sentence scoring"""
    try:
        if not text or len(text.strip()) < 50:
            return text[:100] + "..." if len(text) > 100 else text
        
        # Split into sentences
        sentences = sent_tokenize(text)
        
        if len(sentences) <= max_sentences:
            return text
        
        # Calculate sentence scores
        words = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        word_freq = {}
        
        # Calculate word frequencies
        for word in words:
            if word.isalnum() and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Score sentences
        sentence_scores = {}
        for sentence in sentences:
            sentence_words = word_tokenize(sentence.lower())
            score = 0
            word_count = 0
            
            for word in sentence_words:
                if word in word_freq:
                    score += word_freq[word]
                    word_count += 1
            
            if word_count > 0:
                sentence_scores[sentence] = score / word_count
        
        # Get top sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        summary_sentences = [sent[0] for sent in top_sentences[:max_sentences]]
        
        # Maintain original order
        ordered_summary = []
        for sentence in sentences:
            if sentence in summary_sentences:
                ordered_summary.append(sentence)
        
        return " ".join(ordered_summary)
        
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        # Fallback to simple truncation
        words = text.split()
        return " ".join(words[:50]) + "..." if len(words) > 50 else text

def detect_language_from_audio(audio_file):
    """Attempt to detect language from audio content"""
    try:
        audio = AudioSegment.from_file(audio_file)
        temp_file = "temp_lang_detect.wav"
        audio.export(temp_file, format="wav")
        
        recognizer = sr.Recognizer()
        
        # Try multiple languages
        languages = ['en-US', 'es-ES', 'fr-FR', 'de-DE', 'it-IT', 'pt-BR', 'ja-JP', 'ko-KR', 'zh-CN']
        
        with sr.AudioFile(temp_file) as source:
            audio_data = recognizer.record(source)
            
            for lang in languages:
                try:
                    result = recognizer.recognize_google(audio_data, language=lang)
                    if result and len(result) > 10:  # Reasonable transcription length
                        os.remove(temp_file)
                        return lang
                except:
                    continue
        
        os.remove(temp_file)
        return 'en-US'  # Default fallback
        
    except Exception as e:
        print(f"Error detecting language: {str(e)}")
        return 'en-US'

def extract_audio_features(audio_file):
    """Extract basic audio features for analysis"""
    try:
        audio = AudioSegment.from_file(audio_file)
        
        features = {
            'duration_seconds': len(audio) / 1000.0,
            'sample_rate': audio.frame_rate,
            'channels': audio.channels,
            'format': audio_file.filename.split('.')[-1] if hasattr(audio_file, 'filename') else 'unknown',
            'file_size_mb': len(audio.raw_data) / (1024 * 1024),
            'average_loudness': audio.dBFS
        }
        
        return features
        
    except Exception as e:
        print(f"Error extracting audio features: {str(e)}")
        return {}

def enhance_description(content, video_content):
    try:
        social_media_links = """
        Follow us on social media:
        - Twitter: https://twitter.com/our_channel
        - Instagram: https://instagram.com/our_channel
        - Facebook: https://facebook.com/our_channel
        """
        
        additional_text = generate_additional_text(video_content)
        
        enhanced_description = f"{content}\n\n{additional_text}\n\n{social_media_links}"
        return enhanced_description
    except Exception as e:
        print(f"Error enhancing description: {str(e)}")
        return content

def generate_additional_text(video_content):
    try:
        keywords = extract_keywords(video_content)
        return f"This video covers topics such as: {', '.join(keywords)}. Learn more about these topics in our other videos!"
    except Exception as e:
        print(f"Error generating additional text: {str(e)}")
        return ""

def extract_keywords(text):
    try:
        words = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
        word_freq = nltk.FreqDist(filtered_words)
        return [word for word, _ in word_freq.most_common(5)]
    except Exception as e:
        print(f"Error extracting keywords: {str(e)}")
        return []

def assign_playlist(transcription):
    try:
        playlists = {
            "tech": ["technology", "coding", "programming"],
            "lifestyle": ["fashion", "food", "travel"],
            "education": ["learn", "study", "school"],
        }

        transcription_lower = transcription.lower()
        matches = {}
        for playlist, keywords in playlists.items():
            matches[playlist] = sum(keyword in transcription_lower for keyword in keywords)
        
        total_matches = sum(matches.values())
        if total_matches == 0:
            return None, 0

        best_playlist = max(matches, key=matches.get)
        certainty = (matches[best_playlist] / total_matches) * 100

        if certainty >= 95:
            return best_playlist, certainty
        elif 50 <= certainty < 95:
            return best_playlist, certainty
        else:
            return None, certainty
    except Exception as e:
        print(f"Error assigning playlist: {str(e)}")
        return None, 0

def generate_hierarchical_number(video_type, parent_number=None):
    try:
        if video_type == "main":
            return f"{random.randint(1, 999):03d}"
        elif video_type == "follow_up":
            main_number, *_ = parent_number.split('.')
            return f"{main_number}.{random.randint(1, 99):02d}"
        elif video_type == "clarification":
            main_number, sub_number = parent_number.split('.')
            return f"{main_number}.{sub_number}{chr(random.randint(65, 90))}"
    except Exception as e:
        print(f"Error generating hierarchical number: {str(e)}")
        return "000"

def get_authenticated_service():
    try:
        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
        )
        flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
        credentials = flow.credentials
        return build('youtube', 'v3', credentials=credentials)
    except Exception as e:
        print(f"Error getting authenticated service: {str(e)}")
        return None

def upload_video(title, description, tags, category_id, privacy_status, file_path):
    try:
        youtube = get_authenticated_service()
        
        request_body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }

        response = youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=file_path
        ).execute()
        return response['id']
    except Exception as e:
        print(f"An error occurred while uploading video: {e}")
        return None

def extract_video_frame(video_file_path, timestamp=None):
    """Extract a frame from video at specified timestamp (in seconds)"""
    try:
        cap = cv2.VideoCapture(video_file_path)
        if not cap.isOpened():
            raise Exception("Unable to open video file")
        
        if timestamp is not None:
            cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        else:
            # Default to middle of video
            total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            raise Exception("Unable to extract frame from video")
    except Exception as e:
        print(f"Error extracting video frame: {str(e)}")
        return None

def create_thumbnail_from_frame(frame, title="", width=1280, height=720):
    """Create a YouTube thumbnail from a video frame"""
    try:
        # Convert numpy array to PIL Image
        pil_image = Image.fromarray(frame)
        
        # Resize to YouTube thumbnail dimensions
        pil_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)
        
        # Create overlay for title
        if title:
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Try to use a bold font, fallback to default
            try:
                font_size = min(width // 20, 60)
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Add text with shadow effect
            text_bbox = draw.textbbox((0, 0), title, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Position text at bottom
            x = (width - text_width) // 2
            y = height - text_height - 50
            
            # Draw shadow
            draw.text((x + 2, y + 2), title, font=font, fill=(0, 0, 0, 180))
            # Draw main text
            draw.text((x, y), title, font=font, fill=(255, 255, 255, 255))
            
            # Composite overlay onto image
            pil_image = Image.alpha_composite(pil_image.convert('RGBA'), overlay)
            pil_image = pil_image.convert('RGB')
        
        return pil_image
    except Exception as e:
        print(f"Error creating thumbnail: {str(e)}")
        return None

def create_custom_thumbnail(title, subtitle="", template="gradient", width=1280, height=720):
    """Create a custom thumbnail with text and background"""
    try:
        # Create base image
        img = Image.new('RGB', (width, height), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        if template == "gradient":
            # Create gradient background
            for y in range(height):
                r = int(30 + (200 - 30) * y / height)
                g = int(30 + (100 - 30) * y / height)
                b = int(30 + (200 - 30) * y / height)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
        elif template == "solid":
            # Solid color background
            draw.rectangle([0, 0, width, height], fill=(64, 128, 255))
        elif template == "pattern":
            # Simple pattern
            for x in range(0, width, 100):
                for y in range(0, height, 100):
                    if (x // 100 + y // 100) % 2:
                        draw.rectangle([x, y, x + 100, y + 100], fill=(50, 50, 80))
        
        # Add title text
        if title:
            try:
                title_font_size = min(width // 15, 80)
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", title_font_size)
            except:
                title_font = ImageFont.load_default()
            
            # Calculate text position
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
            
            title_x = (width - title_width) // 2
            title_y = height // 2 - title_height // 2
            
            # Draw title with shadow
            draw.text((title_x + 3, title_y + 3), title, font=title_font, fill=(0, 0, 0, 200))
            draw.text((title_x, title_y), title, font=title_font, fill=(255, 255, 255))
        
        # Add subtitle
        if subtitle:
            try:
                subtitle_font_size = min(width // 25, 40)
                subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", subtitle_font_size)
            except:
                subtitle_font = ImageFont.load_default()
            
            subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]
            
            subtitle_x = (width - subtitle_width) // 2
            subtitle_y = title_y + title_height + 20
            
            # Draw subtitle with shadow
            draw.text((subtitle_x + 2, subtitle_y + 2), subtitle, font=subtitle_font, fill=(0, 0, 0, 150))
            draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=(220, 220, 220))
        
        return img
    except Exception as e:
        print(f"Error creating custom thumbnail: {str(e)}")
        return None

def thumbnail_to_base64(thumbnail_image):
    """Convert PIL Image to base64 string for web display"""
    try:
        buffer = io.BytesIO()
        thumbnail_image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue())
        return img_str.decode()
    except Exception as e:
        print(f"Error converting thumbnail to base64: {str(e)}")
        return None