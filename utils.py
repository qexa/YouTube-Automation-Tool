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
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('averaged_perceptron_tagger_eng', quiet=True)
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

def enhance_description(content, video_content, enhancement_options=None):
    """Enhanced description generation with SEO optimization and structure"""
    try:
        if enhancement_options is None:
            enhancement_options = {
                'include_seo': True,
                'include_hashtags': True,
                'include_timestamps': False,
                'include_social_links': True,
                'include_call_to_action': True,
                'target_audience': 'general',
                'video_category': 'general'
            }
        
        enhanced_parts = []
        enhanced_parts.append(content)
        
        # Extract content insights
        keywords = extract_advanced_keywords(video_content)
        entities = extract_named_entities(video_content)
        topics = categorize_content(video_content)
        
        # Add SEO-optimized content
        if enhancement_options.get('include_seo', True):
            seo_content = generate_seo_content(keywords, topics, enhancement_options.get('video_category', 'general'))
            if seo_content:
                enhanced_parts.append("📚 What You'll Learn:")
                enhanced_parts.append(seo_content)
        
        # Add structured content sections
        structured_content = generate_structured_content(video_content, keywords, topics)
        if structured_content:
            enhanced_parts.append(structured_content)
        
        # Add call-to-action
        if enhancement_options.get('include_call_to_action', True):
            cta = generate_call_to_action(enhancement_options.get('target_audience', 'general'))
            enhanced_parts.append(cta)
        
        # Add hashtags
        if enhancement_options.get('include_hashtags', True):
            hashtags = generate_relevant_hashtags(keywords, topics, enhancement_options.get('video_category', 'general'))
            if hashtags:
                enhanced_parts.append(f"🏷️ Tags: {hashtags}")
        
        # Add social media links
        if enhancement_options.get('include_social_links', True):
            social_links = generate_social_media_section()
            enhanced_parts.append(social_links)
        
        return "\n\n".join(filter(None, enhanced_parts))
        
    except Exception as e:
        print(f"Error enhancing description: {str(e)}")
        return content

def extract_advanced_keywords(text, max_keywords=10):
    """Extract keywords using advanced NLP techniques"""
    try:
        if not text or len(text.strip()) < 10:
            return []
        
        # Tokenize and clean
        words = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        
        # Filter meaningful words
        meaningful_words = []
        for word in words:
            if (word.isalnum() and 
                len(word) > 2 and 
                word not in stop_words and
                word.isalpha()):
                meaningful_words.append(word)
        
        # Calculate frequency
        word_freq = nltk.FreqDist(meaningful_words)
        
        # Get top keywords with minimum frequency
        keywords = []
        for word, freq in word_freq.most_common(max_keywords * 2):
            if freq >= 2 or len(keywords) < 5:  # Include high-frequency or ensure minimum keywords
                keywords.append(word)
            if len(keywords) >= max_keywords:
                break
        
        return keywords
        
    except Exception as e:
        print(f"Error extracting advanced keywords: {str(e)}")
        return []

def extract_named_entities(text):
    """Extract named entities like people, organizations, locations"""
    try:
        if not text or len(text.strip()) < 10:
            return []
        
        # Use NLTK's named entity recognition
        tokens = word_tokenize(text)
        pos_tags = nltk.pos_tag(tokens)
        
        # Extract proper nouns as potential entities
        entities = []
        for word, pos in pos_tags:
            if pos in ['NNP', 'NNPS'] and len(word) > 2:  # Proper nouns
                entities.append(word)
        
        # Remove duplicates and return most common
        entity_freq = nltk.FreqDist(entities)
        return [entity for entity, _ in entity_freq.most_common(5)]
        
    except Exception as e:
        print(f"Error extracting named entities: {str(e)}")
        return []

def categorize_content(text):
    """Categorize content into topics"""
    try:
        if not text:
            return []
        
        text_lower = text.lower()
        
        # Define topic categories with keywords
        topic_keywords = {
            'technology': ['tech', 'software', 'code', 'programming', 'computer', 'digital', 'app', 'website', 'ai', 'machine learning'],
            'education': ['learn', 'teach', 'tutorial', 'course', 'lesson', 'study', 'skill', 'training', 'guide', 'how to'],
            'lifestyle': ['life', 'daily', 'routine', 'health', 'fitness', 'food', 'travel', 'fashion', 'home'],
            'business': ['business', 'entrepreneur', 'startup', 'marketing', 'sales', 'finance', 'money', 'investment'],
            'entertainment': ['fun', 'game', 'music', 'movie', 'show', 'comedy', 'entertainment', 'celebrity'],
            'science': ['science', 'research', 'experiment', 'discovery', 'theory', 'study', 'analysis'],
            'creative': ['art', 'design', 'creative', 'drawing', 'painting', 'photography', 'craft', 'diy']
        }
        
        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                topic_scores[topic] = score
        
        # Return topics sorted by relevance
        return [topic for topic, _ in sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)[:3]]
        
    except Exception as e:
        print(f"Error categorizing content: {str(e)}")
        return []

def generate_seo_content(keywords, topics, category):
    """Generate SEO-optimized content based on keywords and topics"""
    try:
        if not keywords and not topics:
            return ""
        
        seo_parts = []
        
        # Create topic-based descriptions
        if topics:
            primary_topic = topics[0]
            if primary_topic == 'technology':
                seo_parts.append("• Master cutting-edge technology concepts and practical applications")
            elif primary_topic == 'education':
                seo_parts.append("• Step-by-step learning process with actionable insights")
            elif primary_topic == 'business':
                seo_parts.append("• Proven strategies for business growth and success")
            elif primary_topic == 'lifestyle':
                seo_parts.append("• Practical tips to improve your daily life and well-being")
            else:
                seo_parts.append(f"• Comprehensive insights into {primary_topic} and related concepts")
        
        # Add keyword-based content
        if keywords:
            key_concepts = keywords[:3]
            seo_parts.append(f"• Key concepts covered: {', '.join(key_concepts)}")
        
        # Add value propositions
        seo_parts.append("• Expert insights and real-world examples")
        seo_parts.append("• Perfect for beginners and advanced learners alike")
        
        return "\n".join(seo_parts)
        
    except Exception as e:
        print(f"Error generating SEO content: {str(e)}")
        return ""

def generate_structured_content(video_content, keywords, topics):
    """Generate structured content sections"""
    try:
        sections = []
        
        # Generate content overview if we have enough information
        if keywords or topics:
            sections.append("🎯 Content Overview:")
            if topics:
                sections.append(f"This video focuses on {topics[0]} with practical insights and actionable advice.")
            
            if keywords:
                key_points = keywords[:4]
                sections.append(f"Key areas covered include: {', '.join(key_points)}.")
        
        # Add engagement section
        sections.append("\n💡 Why Watch This Video:")
        sections.append("• Get actionable insights you can apply immediately")
        sections.append("• Learn from real-world examples and case studies")
        sections.append("• Join a community of like-minded learners")
        
        return "\n".join(sections) if sections else ""
        
    except Exception as e:
        print(f"Error generating structured content: {str(e)}")
        return ""

def generate_call_to_action(target_audience='general'):
    """Generate targeted call-to-action based on audience"""
    try:
        cta_templates = {
            'general': [
                "👍 If this video helped you, please like and subscribe for more content!",
                "💬 Let us know your thoughts in the comments below!",
                "🔔 Hit the notification bell to stay updated with our latest videos!"
            ],
            'educational': [
                "📚 Subscribe for more learning content and tutorials!",
                "💡 Share your learning journey in the comments!",
                "🎓 Join our educational community by subscribing!"
            ],
            'professional': [
                "🚀 Subscribe for more professional development content!",
                "💼 Connect with us for more industry insights!",
                "📈 Help others grow by sharing this video!"
            ]
        }
        
        ctas = cta_templates.get(target_audience, cta_templates['general'])
        return "\n".join(ctas)
        
    except Exception as e:
        print(f"Error generating call-to-action: {str(e)}")
        return "👍 Like, subscribe, and share if you found this helpful!"

def generate_relevant_hashtags(keywords, topics, category, max_hashtags=10):
    """Generate relevant hashtags based on content analysis"""
    try:
        hashtags = set()
        
        # Add topic-based hashtags
        topic_hashtags = {
            'technology': ['#Tech', '#Innovation', '#Digital', '#Future'],
            'education': ['#Learning', '#Education', '#Tutorial', '#Knowledge'],
            'business': ['#Business', '#Entrepreneur', '#Success', '#Growth'],
            'lifestyle': ['#Lifestyle', '#Life', '#Tips', '#Wellness'],
            'entertainment': ['#Fun', '#Entertainment', '#Content'],
            'science': ['#Science', '#Research', '#Discovery'],
            'creative': ['#Creative', '#Art', '#Design', '#DIY']
        }
        
        # Add hashtags from topics
        for topic in topics[:2]:  # Use top 2 topics
            if topic in topic_hashtags:
                hashtags.update(topic_hashtags[topic][:3])
        
        # Add keyword-based hashtags
        for keyword in keywords[:5]:
            if len(keyword) > 3:
                hashtag = f"#{keyword.capitalize()}"
                if len(hashtag) <= 20:  # Keep hashtags reasonable length
                    hashtags.add(hashtag)
        
        # Add general content hashtags
        general_hashtags = ['#YouTube', '#Content', '#Video', '#Learn', '#Share']
        hashtags.update(general_hashtags[:2])
        
        # Limit to max_hashtags
        hashtag_list = list(hashtags)[:max_hashtags]
        return " ".join(hashtag_list)
        
    except Exception as e:
        print(f"Error generating hashtags: {str(e)}")
        return "#Content #Video #YouTube"

def generate_social_media_section():
    """Generate social media links section"""
    try:
        social_content = """🌐 Connect With Us:
• Subscribe: Hit that subscribe button for more amazing content!
• Social Media: Follow us for behind-the-scenes content and updates
• Community: Join our growing community of learners and creators

📞 Business Inquiries: Contact us through our channel's about section"""
        
        return social_content
        
    except Exception as e:
        print(f"Error generating social media section: {str(e)}")
        return "📱 Follow us on social media for more content!"

def generate_additional_text(video_content):
    """Legacy function for backward compatibility"""
    try:
        keywords = extract_advanced_keywords(video_content)
        if not keywords:
            return ""
        return f"This video covers topics such as: {', '.join(keywords[:5])}. Learn more about these topics in our other videos!"
    except Exception as e:
        print(f"Error generating additional text: {str(e)}")
        return ""

def extract_keywords(text):
    """Legacy function for backward compatibility"""
    return extract_advanced_keywords(text, max_keywords=5)

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

# Video Tags and Category Management Functions

def generate_video_tags(content, options=None):
    """Generate intelligent video tags based on content analysis"""
    if options is None:
        options = {
            'max_tags': 10,
            'include_keywords': True,
            'include_trending': True,
            'include_long_tail': True,
            'include_branded': False,
            'language': 'en',
            'category': 'auto'
        }
    
    try:
        # Extract keywords and entities
        keywords = extract_advanced_keywords(content, max_keywords=20)
        entities = extract_named_entities(content)
        topics = categorize_content(content)
        
        # Generate different types of tags
        all_tags = []
        
        # Content-based keywords
        if options.get('include_keywords', True):
            content_tags = keywords[:options.get('max_tags', 10) // 2]
            all_tags.extend(content_tags)
        
        # Trending and popular terms
        if options.get('include_trending', True):
            trending_tags = generate_trending_tags(topics, entities)
            all_tags.extend(trending_tags[:3])
        
        # Long-tail keywords
        if options.get('include_long_tail', True):
            long_tail_tags = generate_long_tail_tags(content, keywords)
            all_tags.extend(long_tail_tags[:4])
        
        # Entity-based tags
        entity_tags = [entity.lower().replace(' ', '') for entity in entities[:3]]
        all_tags.extend(entity_tags)
        
        # Remove duplicates and limit to max_tags
        unique_tags = []
        seen = set()
        for tag in all_tags:
            tag_clean = tag.lower().strip()
            if tag_clean and tag_clean not in seen and len(tag_clean) > 2:
                unique_tags.append(tag)
                seen.add(tag_clean)
                if len(unique_tags) >= options.get('max_tags', 10):
                    break
        
        # Calculate SEO score
        seo_score = calculate_tag_seo_score(unique_tags, content)
        
        # Generate insights
        insights = generate_tag_insights(unique_tags, topics, entities)
        
        return {
            'tags': unique_tags,
            'character_count': sum(len(tag) for tag in unique_tags) + len(unique_tags) - 1,  # Including commas
            'seo_score': seo_score,
            'insights': insights,
            'topics': topics,
            'entities': entities
        }
        
    except Exception as e:
        print(f"Error generating tags: {str(e)}")
        # Fallback to basic keyword extraction
        basic_keywords = extract_keywords(content)
        return {
            'tags': basic_keywords[:10],
            'character_count': sum(len(tag) for tag in basic_keywords[:10]) + 9,
            'seo_score': 75,
            'insights': 'Basic tag generation used due to processing error.',
            'topics': ['general'],
            'entities': []
        }

def generate_trending_tags(topics, entities):
    """Generate trending tags based on topics and entities"""
    trending_base = {
        'technology': ['tech', 'innovation', 'digital', 'future', 'ai', 'coding'],
        'education': ['learning', 'tutorial', 'howto', 'guide', 'tips', 'educational'],
        'entertainment': ['fun', 'viral', 'trending', 'popular', 'amazing', 'awesome'],
        'business': ['entrepreneur', 'startup', 'marketing', 'business', 'success', 'money'],
        'lifestyle': ['lifestyle', 'daily', 'routine', 'life', 'personal', 'journey'],
        'science': ['science', 'research', 'discovery', 'experiment', 'facts', 'amazing'],
        'creative': ['creative', 'art', 'design', 'diy', 'craft', 'tutorial']
    }
    
    trending_tags = []
    for topic in topics:
        if topic in trending_base:
            trending_tags.extend(trending_base[topic][:2])
    
    # Add year for trending context
    from datetime import datetime
    current_year = datetime.now().year
    trending_tags.append(str(current_year))
    
    return trending_tags

def generate_long_tail_tags(content, keywords):
    """Generate long-tail keyword combinations"""
    long_tail_tags = []
    
    # Common long-tail patterns
    patterns = [
        'how to {}',
        '{} tutorial',
        '{} guide',
        '{} tips',
        'best {}',
        '{} explained',
        '{} for beginners'
    ]
    
    for keyword in keywords[:3]:
        for pattern in patterns[:2]:  # Limit to avoid too many tags
            long_tail = pattern.format(keyword)
            if len(long_tail) <= 30:  # YouTube tag length limit
                long_tail_tags.append(long_tail)
    
    return long_tail_tags

def calculate_tag_seo_score(tags, content):
    """Calculate SEO effectiveness score for tags"""
    score = 0
    content_lower = content.lower()
    
    # Check tag relevance to content
    relevant_tags = 0
    for tag in tags:
        if tag.lower() in content_lower:
            relevant_tags += 1
    
    relevance_score = (relevant_tags / len(tags)) * 40 if tags else 0
    
    # Check tag diversity
    unique_chars = set(''.join(tags).lower())
    diversity_score = min(len(unique_chars) / 20, 1) * 30
    
    # Check tag length distribution
    avg_length = sum(len(tag) for tag in tags) / len(tags) if tags else 0
    length_score = 30 if 5 <= avg_length <= 15 else 20
    
    total_score = relevance_score + diversity_score + length_score
    return min(int(total_score), 100)

def generate_tag_insights(tags, topics, entities):
    """Generate performance insights for tags"""
    insights = []
    
    # Tag count analysis
    tag_count = len(tags)
    if tag_count < 5:
        insights.append("⚠️ Consider adding more tags (5-15 recommended)")
    elif tag_count > 15:
        insights.append("⚠️ Too many tags may reduce effectiveness")
    else:
        insights.append("✅ Good tag count for optimal discoverability")
    
    # Topic coverage
    if len(topics) > 1:
        insights.append(f"✅ Multi-topic content covering: {', '.join(topics[:3])}")
    else:
        insights.append("💡 Consider broader topic coverage for better reach")
    
    # Entity recognition
    if entities:
        insights.append(f"🎯 Key entities identified: {', '.join(entities[:3])}")
    
    # Tag length analysis
    long_tags = [tag for tag in tags if len(tag) > 20]
    if long_tags:
        insights.append(f"💡 {len(long_tags)} long-tail tags for specific searches")
    
    return ' • '.join(insights)

def suggest_youtube_category(content, topics=None):
    """Suggest appropriate YouTube category based on content analysis"""
    if topics is None:
        topics = categorize_content(content)
    
    # YouTube category mapping
    category_mapping = {
        'education': ('27', 'Education'),
        'technology': ('28', 'Science & Technology'),
        'entertainment': ('24', 'Entertainment'),
        'business': ('25', 'News & Politics'),
        'lifestyle': ('26', 'Howto & Style'),
        'creative': ('1', 'Film & Animation'),
        'science': ('28', 'Science & Technology'),
        'music': ('10', 'Music'),
        'gaming': ('20', 'Gaming'),
        'sports': ('17', 'Sports'),
        'travel': ('19', 'Travel & Events'),
        'comedy': ('23', 'Comedy'),
        'pets': ('15', 'Pets & Animals'),
        'vehicles': ('2', 'Autos & Vehicles'),
        'people': ('22', 'People & Blogs')
    }
    
    # Find best matching category
    content_lower = content.lower()
    
    # Check for explicit category keywords
    explicit_matches = {
        'tutorial': 'education',
        'how to': 'education', 
        'guide': 'education',
        'review': 'technology',
        'unboxing': 'technology',
        'vlog': 'people',
        'comedy': 'comedy',
        'funny': 'comedy',
        'music': 'music',
        'song': 'music',
        'game': 'gaming',
        'gameplay': 'gaming',
        'travel': 'travel',
        'recipe': 'lifestyle',
        'workout': 'lifestyle'
    }
    
    for keyword, category in explicit_matches.items():
        if keyword in content_lower:
            if category in category_mapping:
                cat_id, cat_name = category_mapping[category]
                return {
                    'category_id': cat_id,
                    'category_name': cat_name,
                    'confidence': 'High',
                    'reason': f'Content contains "{keyword}" indicating {category} category'
                }
    
    # Use topic-based suggestion
    if topics:
        primary_topic = topics[0]
        if primary_topic in category_mapping:
            cat_id, cat_name = category_mapping[primary_topic]
            return {
                'category_id': cat_id,
                'category_name': cat_name,
                'confidence': 'Medium',
                'reason': f'Content classified as {primary_topic}'
            }
    
    # Default suggestion
    return {
        'category_id': '22',
        'category_name': 'People & Blogs',
        'confidence': 'Low',
        'reason': 'General content category recommended'
    }

def analyze_content_for_tags(content):
    """Analyze content specifically for tag generation insights"""
    try:
        # Extract various content features
        keywords = extract_advanced_keywords(content, max_keywords=15)
        entities = extract_named_entities(content)
        topics = categorize_content(content)
        
        # Calculate content metrics
        word_count = len(content.split())
        sentence_count = len([s for s in content.split('.') if s.strip()])
        
        # Content quality score
        quality_score = calculate_content_quality_score(content, keywords, entities)
        
        return {
            'keywords': keywords,
            'entities': entities,
            'topics': topics,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'quality_score': quality_score,
            'tag_potential': len(keywords) + len(entities),
            'content_type': determine_content_type(content)
        }
        
    except Exception as e:
        print(f"Error analyzing content for tags: {str(e)}")
        return {
            'keywords': [],
            'entities': [],
            'topics': ['general'],
            'word_count': 0,
            'sentence_count': 0,
            'quality_score': 50,
            'tag_potential': 0,
            'content_type': 'general'
        }

def calculate_content_quality_score(content, keywords, entities):
    """Calculate content quality score for tag generation"""
    score = 0
    
    # Length score (20 points)
    word_count = len(content.split())
    if 50 <= word_count <= 300:
        score += 20
    elif word_count > 20:
        score += 15
    else:
        score += 5
    
    # Keyword density (30 points)
    if keywords:
        unique_keywords = len(set(keywords))
        if unique_keywords >= 5:
            score += 30
        else:
            score += unique_keywords * 6
    
    # Entity recognition (25 points)
    if entities:
        entity_count = len(entities)
        score += min(entity_count * 8, 25)
    
    # Content structure (25 points)
    sentences = content.split('.')
    avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
    if 10 <= avg_sentence_length <= 25:
        score += 25
    else:
        score += 15
    
    return min(score, 100)

def determine_content_type(content):
    """Determine the type of content for better tag generation"""
    content_lower = content.lower()
    
    content_indicators = {
        'tutorial': ['how to', 'step by step', 'tutorial', 'guide', 'learn', 'teach'],
        'review': ['review', 'unboxing', 'test', 'comparison', 'vs', 'better'],
        'vlog': ['vlog', 'daily', 'routine', 'my day', 'life', 'personal'],
        'news': ['news', 'update', 'announcement', 'breaking', 'latest'],
        'entertainment': ['funny', 'comedy', 'entertainment', 'fun', 'hilarious'],
        'educational': ['explain', 'education', 'science', 'facts', 'research']
    }
    
    for content_type, indicators in content_indicators.items():
        if any(indicator in content_lower for indicator in indicators):
            return content_type
    
    return 'general'