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

def generate_title(content, title_options=None):
    """Generate compelling YouTube-optimized titles with multiple variations for maximum engagement"""
    try:
        if title_options is None:
            title_options = {}
        
        # Extract key information from content
        analysis = analyze_content_for_title_generation(content)
        
        # Generate multiple title variations
        titles = []
        
        # Enhanced power words for maximum engagement
        power_words = {
            'curiosity': ["Secret", "Hidden", "Forbidden", "Exposed", "Revealed", "Uncovered", "Behind-the-Scenes"],
            'urgency': ["Now", "Today", "Immediately", "Right Now", "Instantly", "Fast", "Quick"],
            'authority': ["Expert", "Pro", "Master", "Guru", "Professional", "Advanced", "Elite"],
            'emotion': ["Amazing", "Incredible", "Shocking", "Mind-Blowing", "Jaw-Dropping", "Unbelievable", "Stunning"],
            'value': ["Ultimate", "Complete", "Perfect", "Best", "Top", "Premium", "Exclusive", "Essential"],
            'transformation': ["Revolutionary", "Game-Changing", "Life-Changing", "Breakthrough", "Powerful", "Epic"]
        }
        
        # Viral title patterns that drive engagement
        viral_patterns = [
            "This {emotion} {keyword} Trick Will {benefit}",
            "Why Everyone is {action} with {keyword} (You Should Too!)",
            "The {authority} {keyword} Method That {result}",
            "{number} {keyword} Secrets That Will {transformation}",
            "What Happens When You {action} {keyword} for {timeframe}",
            "I Tried {keyword} for {timeframe} - Here's What Happened",
            "The Dark Truth About {keyword} Nobody Talks About",
            "{keyword}: From {before_state} to {after_state} in {timeframe}"
        ]
        
        # Extract content insights
        keywords = analysis['keywords'][:5] if analysis['keywords'] else ['content']
        primary_topic = analysis.get('primary_topic', 'general')
        entities = analysis.get('entities', [])
        content_type = analysis.get('content_type', 'tutorial')
        
        # Identify the main topic phrase for better titles
        main_topic = identify_main_topic(keywords, primary_topic, content)
        
        # Generate engagement-focused titles using different strategies
        
        # 1. Curiosity-driven titles (highest engagement)
        if main_topic:
            secret_word = random.choice(power_words['curiosity'])
            emotion_word = random.choice(power_words['emotion'])
            titles.extend([
                f"The {secret_word} {main_topic} Method That Changed Everything",
                f"{emotion_word} {main_topic} Technique Everyone's Talking About",
                f"What They Don't Want You to Know About {main_topic}"
            ])
        
        # 2. Problem-solution with emotional hooks
        if main_topic:
            titles.extend([
                f"Struggling with {main_topic}? This Method Works in Minutes",
                f"Why Your {main_topic} Strategy Fails (And How to Fix It)",
                f"From {main_topic} Beginner to {main_topic} Success Story"
            ])
        
        # 3. Achievement and transformation stories
        if main_topic:
            transform_word = random.choice(power_words['transformation'])
            titles.extend([
                f"How I Mastered {main_topic} in 30 Days (Step-by-Step)",
                f"My {transform_word} {main_topic} Journey: Before vs After",
                f"Zero to {main_topic} Hero: The Complete Transformation"
            ])
        
        # 4. Competitive and comparison titles
        if main_topic and len(keywords) >= 2:
            alt_topic = keywords[1].title() if keywords[1] != keywords[0] else f"{main_topic} Strategies"
            titles.extend([
                f"{main_topic} vs Traditional Methods: The Ultimate Showdown",
                f"Which Works Better: {main_topic} or Old-School Tactics? (Surprising Results)",
                f"I Tested {main_topic} vs Competition - You Won't Believe the Winner"
            ])
        
        # 5. List-based with emotional amplifiers
        if main_topic:
            numbers = [5, 7, 10, 15, 20]
            number = random.choice(numbers)
            emotion = random.choice(power_words['emotion'])
            titles.extend([
                f"{number} {emotion} {main_topic} Tips That Actually Work",
                f"Top {number} {main_topic} Mistakes Killing Your Results",
                f"{number} Mind-Blowing {main_topic} Hacks for Instant Success"
            ])
        
        # 6. Time-sensitive and urgency-driven
        if main_topic:
            urgency_word = random.choice(power_words['urgency'])
            timeframes = ["24 Hours", "1 Week", "30 Days", "This Month"]
            timeframe = random.choice(timeframes)
            titles.extend([
                f"Master {main_topic} {urgency_word} - Complete Guide for {timeframe}",
                f"Learn {main_topic} in {timeframe} or Get Your Money Back",
                f"{urgency_word}: The {main_topic} Strategy Taking Over {primary_topic.title()}"
            ])
        
        # 7. Authority and credibility-based
        if main_topic:
            authority_word = random.choice(power_words['authority'])
            entity = entities[0] if entities else f"{primary_topic.title()} Expert"
            titles.extend([
                f"{authority_word} {entity} Reveals: The Real {main_topic} Method",
                f"Industry {authority_word} Shares {main_topic} Secrets",
                f"{entity}'s {main_topic} System That Beats Everything Else"
            ])
        
        # 8. Controversy and debate starters
        if main_topic:
            titles.extend([
                f"Is {main_topic} Worth It? Honest Review After 1 Year",
                f"The {main_topic} Debate: Why Experts Are Divided",
                f"Controversial: Why Most {main_topic} Advice is Wrong"
            ])
        
        # Filter and optimize titles
        unique_titles = []
        for title in titles:
            if title and len(title) <= 100 and title not in unique_titles:
                # Optimize title for engagement
                optimized_title = optimize_title_for_engagement(title)
                unique_titles.append(optimized_title)
        
        # Sort by engagement potential and return top titles
        scored_titles = score_titles_for_engagement(unique_titles, analysis)
        final_titles = [title for title, score in scored_titles[:8]]  # Top 8 titles
        
        return {
            'titles': final_titles if final_titles else ["Incredible Content That Will Transform Your Perspective"],
            'analysis': analysis,
            'recommendations': generate_title_recommendations(analysis, final_titles),
            'engagement_insights': generate_engagement_insights(scored_titles[:8])
        }
        
    except Exception as e:
        print(f"Error generating title: {str(e)}")
        return {
            'titles': ["Amazing Content You Need to See"],
            'analysis': {'error': str(e)},
            'recommendations': [],
            'engagement_insights': []
        }

def identify_main_topic(keywords, primary_topic, content):
    """Identify the main topic phrase for compelling titles"""
    if not keywords:
        return "Amazing Content"
    
    # Define topic-specific combinations
    topic_combinations = {
        'business': ['online business', 'digital marketing', 'business growth', 'profitable business', 'business strategies'],
        'technology': ['programming', 'web development', 'software development', 'tech tutorials', 'coding skills'],
        'education': ['learning strategies', 'study methods', 'educational content', 'skill building', 'knowledge mastery'],
        'lifestyle': ['life hacks', 'productivity tips', 'wellness strategies', 'lifestyle changes', 'personal growth'],
        'entertainment': ['entertainment content', 'creative projects', 'fun activities', 'viral content', 'engaging material'],
        'science': ['scientific methods', 'research techniques', 'data analysis', 'scientific discoveries', 'innovation'],
        'creative': ['creative processes', 'artistic techniques', 'design methods', 'creative projects', 'artistic expression']
    }
    
    # Look for specific combinations based on content
    content_lower = content.lower()
    
    # Business-related topics
    if any(word in keywords for word in ['business', 'marketing', 'sales', 'profitable', 'online', 'digital']):
        if 'online' in keywords and 'business' in keywords:
            return "Online Business"
        elif 'digital' in keywords and 'marketing' in keywords:
            return "Digital Marketing"
        elif 'profitable' in keywords and 'business' in keywords:
            return "Profitable Business"
        elif 'business' in keywords:
            return "Business Growth"
        elif 'marketing' in keywords:
            return "Marketing Strategy"
    
    # Technology topics
    if any(word in keywords for word in ['programming', 'coding', 'development', 'software', 'tech', 'python', 'javascript']):
        if 'programming' in keywords or 'coding' in keywords:
            return "Programming"
        elif 'development' in keywords:
            return "Development"
        else:
            return "Tech Skills"
    
    # Education topics
    if any(word in keywords for word in ['learn', 'tutorial', 'guide', 'education', 'teaching', 'study']):
        if 'tutorial' in keywords:
            return "Tutorial"
        elif 'learn' in keywords:
            return "Learning"
        else:
            return "Education"
    
    # Fitness/Health topics
    if any(word in keywords for word in ['fitness', 'health', 'workout', 'exercise', 'nutrition']):
        return "Fitness"
    
    # Creative topics
    if any(word in keywords for word in ['creative', 'design', 'art', 'music', 'video', 'content']):
        if 'content' in keywords:
            return "Content Creation"
        else:
            return "Creative Projects"
    
    # Default to combining top keywords meaningfully
    if len(keywords) >= 2:
        # Create meaningful combinations
        first_keyword = keywords[0].title()
        second_keyword = keywords[1].title()
        
        # Check if they form a natural phrase
        natural_phrases = [
            f"{first_keyword} {second_keyword}",
            f"{first_keyword} Strategy",
            f"{first_keyword} Mastery",
            f"{first_keyword} Success"
        ]
        
        # Return the most natural sounding phrase
        return natural_phrases[0] if len(f"{first_keyword} {second_keyword}") <= 25 else f"{first_keyword} Mastery"
    
    # Single keyword fallback
    return keywords[0].title() if keywords else "Amazing Content"

def create_keyword_phrase(keywords):
    """Create a natural phrase from keywords (legacy function)"""
    return identify_main_topic(keywords, 'general', ' '.join(keywords))

def optimize_title_for_engagement(title):
    """Optimize individual title for maximum engagement"""
    # Capitalize first letter of each major word
    words = title.split()
    optimized_words = []
    
    for word in words:
        # Keep certain words lowercase unless they're the first word
        if word.lower() in ['a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'] and len(optimized_words) > 0:
            optimized_words.append(word.lower())
        else:
            optimized_words.append(word.capitalize())
    
    optimized_title = ' '.join(optimized_words)
    
    # Ensure proper punctuation for engagement
    if not optimized_title.endswith(('!', '?', ')')):
        if any(word in optimized_title.lower() for word in ['how', 'why', 'what', 'when', 'where', 'which']):
            optimized_title += '?'
        elif any(word in optimized_title.lower() for word in ['amazing', 'incredible', 'shocking', 'unbelievable']):
            optimized_title += '!'
    
    return optimized_title

def score_titles_for_engagement(titles, analysis):
    """Score titles based on engagement potential"""
    scored_titles = []
    
    high_engagement_words = [
        'secret', 'hidden', 'revealed', 'exposed', 'shocking', 'amazing', 'incredible',
        'unbelievable', 'mind-blowing', 'game-changing', 'ultimate', 'complete',
        'versus', 'vs', 'battle', 'showdown', 'truth', 'honest', 'real'
    ]
    
    emotional_triggers = [
        'you won\'t believe', 'will change everything', 'nobody talks about',
        'changed my life', 'transformed', 'breakthrough', 'revolutionary'
    ]
    
    for title in titles:
        score = 0
        title_lower = title.lower()
        
        # Score based on engagement elements
        score += sum(5 for word in high_engagement_words if word in title_lower)
        score += sum(8 for trigger in emotional_triggers if trigger in title_lower)
        score += 3 if any(char.isdigit() for char in title) else 0  # Numbers boost engagement
        score += 2 if title.endswith('!') else 0
        score += 1 if title.endswith('?') else 0
        score += 2 if '(' in title and ')' in title else 0  # Parentheses add intrigue
        score += 1 if ':' in title else 0  # Colons create structure
        
        # Penalize overly long titles
        if len(title) > 80:
            score -= 3
        
        # Bonus for optimal length (50-70 characters)
        if 50 <= len(title) <= 70:
            score += 2
        
        scored_titles.append((title, score))
    
    # Sort by score (highest first)
    return sorted(scored_titles, key=lambda x: x[1], reverse=True)

def generate_engagement_insights(scored_titles):
    """Generate insights about title engagement potential"""
    insights = []
    
    if scored_titles:
        best_title, best_score = scored_titles[0]
        
        insights.append(f"Highest engagement potential: '{best_title}' (Score: {best_score})")
        
        # Analyze what makes titles engaging
        high_scoring = [title for title, score in scored_titles if score >= 10]
        if high_scoring:
            insights.append(f"{len(high_scoring)} titles have high engagement potential")
        
        # Check for emotional triggers
        emotional_count = sum(1 for title, _ in scored_titles if any(trigger in title.lower() 
                            for trigger in ['amazing', 'incredible', 'shocking', 'secret', 'revealed']))
        if emotional_count > 0:
            insights.append(f"{emotional_count} titles use emotional triggers for better engagement")
        
        # Check for curiosity gaps
        curiosity_count = sum(1 for title, _ in scored_titles if title.endswith('?') or 
                            any(word in title.lower() for word in ['why', 'what', 'how', 'which']))
        if curiosity_count > 0:
            insights.append(f"{curiosity_count} titles create curiosity gaps to drive clicks")
    
    return insights[:4]  # Return top 4 insights

def analyze_content_for_title_generation(content):
    """Analyze content specifically for title generation"""
    try:
        # Tokenize and process
        words = word_tokenize(content.lower())
        sentences = sent_tokenize(content)
        
        # Remove stop words and extract keywords
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if word.isalnum() and word not in stop_words and len(word) > 2]
        
        # Get word frequency
        word_freq = nltk.FreqDist(filtered_words)
        keywords = [word for word, _ in word_freq.most_common(10)]
        
        # Extract named entities (simplified)
        entities = extract_named_entities(content)
        
        # Determine primary topic
        primary_topic = categorize_content(content)[0] if categorize_content(content) else 'general'
        
        # Content metrics
        word_count = len(words)
        sentence_count = len(sentences)
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        return {
            'keywords': keywords,
            'entities': entities[:3],  # Top 3 entities
            'primary_topic': primary_topic,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'content_type': determine_content_type(content)
        }
        
    except Exception as e:
        return {
            'keywords': [],
            'entities': [],
            'primary_topic': 'general',
            'word_count': 0,
            'sentence_count': 0,
            'avg_sentence_length': 0,
            'content_type': 'unknown',
            'error': str(e)
        }

def generate_title_recommendations(analysis, titles):
    """Generate optimization recommendations for titles"""
    recommendations = []
    
    try:
        # Check title length optimization
        for title in titles:
            if len(title) > 60:
                recommendations.append("Consider shorter titles (under 60 characters) for better mobile display")
                break
        
        # Check for power words
        power_words_used = any(word in ' '.join(titles).lower() for word in ['ultimate', 'complete', 'secret', 'amazing', 'how to'])
        if not power_words_used:
            recommendations.append("Add power words like 'Ultimate', 'Complete', or 'Secret' to increase engagement")
        
        # Check for numbers
        has_numbers = any(char.isdigit() for char in ' '.join(titles))
        if not has_numbers:
            recommendations.append("Include specific numbers (e.g., '5 Tips', '10 Ways') to improve click-through rates")
        
        # Check for emotional triggers
        emotional_words = ['amazing', 'incredible', 'shocking', 'life-changing', 'revolutionary']
        has_emotional = any(word in ' '.join(titles).lower() for word in emotional_words)
        if not has_emotional:
            recommendations.append("Consider adding emotional trigger words to create stronger viewer connection")
        
        # Topic-specific recommendations
        if analysis.get('primary_topic') == 'technology':
            recommendations.append("For tech content, include version numbers or specific tool names in titles")
        elif analysis.get('primary_topic') == 'education':
            recommendations.append("Educational content performs well with 'Learn', 'Master', or 'Course' in titles")
        
        return recommendations[:4]  # Return top 4 recommendations
        
    except Exception as e:
        return [f"Error generating recommendations: {str(e)}"]

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

def assign_playlist(transcription, options=None):
    """Enhanced playlist assignment with SEO optimization and content analysis"""
    try:
        if options is None:
            options = {}
        
        # Enhanced playlist categories with SEO considerations
        playlist_definitions = {
            "Technology & Programming": {
                "keywords": ["technology", "coding", "programming", "software", "development", "tech", "computer", "algorithm", "data", "AI", "machine learning", "web", "app", "digital"],
                "weight": 1.5,
                "seo_tags": ["tech", "programming", "coding", "software", "development"],
                "description": "Content focused on technology, programming, and digital innovation"
            },
            "Education & Tutorials": {
                "keywords": ["learn", "tutorial", "guide", "education", "teaching", "lesson", "course", "study", "school", "university", "training", "skill", "knowledge"],
                "weight": 1.4,
                "seo_tags": ["education", "tutorial", "learning", "guide", "howto"],
                "description": "Educational content and step-by-step tutorials"
            },
            "Business & Finance": {
                "keywords": ["business", "finance", "money", "investment", "startup", "entrepreneur", "marketing", "sales", "economics", "profit", "revenue", "strategy"],
                "weight": 1.3,
                "seo_tags": ["business", "finance", "money", "investment", "entrepreneur"],
                "description": "Business insights, financial advice, and entrepreneurship"
            },
            "Lifestyle & Personal": {
                "keywords": ["lifestyle", "personal", "life", "daily", "routine", "habit", "wellness", "health", "fitness", "motivation", "inspiration", "productivity"],
                "weight": 1.2,
                "seo_tags": ["lifestyle", "personal", "motivation", "wellness", "productivity"],
                "description": "Personal development and lifestyle content"
            },
            "Entertainment & Media": {
                "keywords": ["entertainment", "fun", "funny", "comedy", "movie", "music", "game", "gaming", "review", "reaction", "vlog", "story"],
                "weight": 1.1,
                "seo_tags": ["entertainment", "fun", "gaming", "review", "vlog"],
                "description": "Entertainment content and media reviews"
            },
            "Science & Research": {
                "keywords": ["science", "research", "experiment", "study", "analysis", "theory", "discovery", "innovation", "physics", "chemistry", "biology"],
                "weight": 1.3,
                "seo_tags": ["science", "research", "experiment", "innovation", "discovery"],
                "description": "Scientific content and research discussions"
            },
            "Creative & Arts": {
                "keywords": ["creative", "art", "design", "photography", "music", "drawing", "painting", "craft", "DIY", "artistic", "aesthetic"],
                "weight": 1.2,
                "seo_tags": ["creative", "art", "design", "DIY", "craft"],
                "description": "Creative content and artistic expressions"
            },
            "Travel & Adventure": {
                "keywords": ["travel", "adventure", "journey", "explore", "destination", "vacation", "trip", "culture", "country", "city", "experience"],
                "weight": 1.1,
                "seo_tags": ["travel", "adventure", "explore", "destination", "culture"],
                "description": "Travel experiences and adventure content"
            }
        }
        
        # Analyze content for keywords and topics
        content_analysis = analyze_content_for_playlists(transcription)
        transcription_lower = transcription.lower()
        
        # Calculate playlist scores with enhanced analysis
        playlist_scores = {}
        total_score = 0
        
        for playlist_name, playlist_info in playlist_definitions.items():
            # Basic keyword matching
            keyword_matches = sum(1 for keyword in playlist_info["keywords"] if keyword in transcription_lower)
            
            # Advanced content analysis scoring
            topic_relevance = calculate_topic_relevance(content_analysis, playlist_info["keywords"])
            
            # SEO weight application
            weighted_score = (keyword_matches + topic_relevance) * playlist_info["weight"]
            
            playlist_scores[playlist_name] = {
                "score": weighted_score,
                "keyword_matches": keyword_matches,
                "topic_relevance": topic_relevance,
                "seo_tags": playlist_info["seo_tags"],
                "description": playlist_info["description"]
            }
            total_score += weighted_score
        
        # Determine best playlist with confidence scoring
        if total_score == 0:
            return generate_default_playlist_assignment(transcription)
        
        best_playlist = max(playlist_scores, key=lambda x: playlist_scores[x]["score"])
        best_score = playlist_scores[best_playlist]["score"]
        confidence = min((best_score / total_score) * 100, 99)
        
        # Generate comprehensive playlist assignment
        assignment_result = {
            "primary_playlist": {
                "name": best_playlist,
                "confidence": round(confidence, 1),
                "score": round(best_score, 2),
                "seo_tags": playlist_scores[best_playlist]["seo_tags"],
                "description": playlist_scores[best_playlist]["description"]
            },
            "alternative_playlists": [],
            "content_analysis": content_analysis,
            "seo_insights": generate_playlist_seo_insights(playlist_scores, best_playlist),
            "recommendations": generate_playlist_recommendations(playlist_scores, best_playlist, confidence)
        }
        
        # Add alternative playlists
        sorted_playlists = sorted(playlist_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        for playlist_name, playlist_data in sorted_playlists[1:4]:  # Top 3 alternatives
            if playlist_data["score"] > 0:
                alt_confidence = (playlist_data["score"] / total_score) * 100
                assignment_result["alternative_playlists"].append({
                    "name": playlist_name,
                    "confidence": round(alt_confidence, 1),
                    "score": round(playlist_data["score"], 2),
                    "seo_tags": playlist_data["seo_tags"]
                })
        
        return assignment_result
        
    except Exception as e:
        print(f"Error in enhanced playlist assignment: {str(e)}")
        return generate_error_playlist_assignment(str(e))

def analyze_content_for_playlists(content):
    """Analyze content specifically for playlist assignment"""
    try:
        # Extract keywords and topics
        keywords = extract_advanced_keywords(content, max_keywords=15)
        entities = extract_named_entities(content)
        topics = categorize_content(content)
        
        # Calculate content characteristics
        word_count = len(content.split())
        complexity_score = calculate_content_complexity(content)
        
        return {
            "keywords": keywords,
            "entities": entities,
            "topics": topics,
            "word_count": word_count,
            "complexity_score": complexity_score,
            "primary_topic": topics[0] if topics else "general"
        }
    except Exception as e:
        print(f"Error analyzing content for playlists: {str(e)}")
        return {"keywords": [], "entities": [], "topics": ["general"], "word_count": 0, "complexity_score": 0, "primary_topic": "general"}

def calculate_topic_relevance(content_analysis, playlist_keywords):
    """Calculate how relevant content is to playlist keywords"""
    try:
        relevance_score = 0
        content_keywords = content_analysis.get("keywords", [])
        content_topics = content_analysis.get("topics", [])
        
        # Keyword overlap scoring
        for keyword in content_keywords:
            if any(playlist_keyword in keyword.lower() or keyword.lower() in playlist_keyword for playlist_keyword in playlist_keywords):
                relevance_score += 1
        
        # Topic alignment scoring
        for topic in content_topics:
            if any(playlist_keyword in topic.lower() or topic.lower() in playlist_keyword for playlist_keyword in playlist_keywords):
                relevance_score += 0.5
        
        return relevance_score
    except Exception as e:
        print(f"Error calculating topic relevance: {str(e)}")
        return 0

def calculate_content_complexity(content):
    """Calculate content complexity score"""
    try:
        words = content.split()
        if not words:
            return 0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        sentence_count = len([s for s in content.split('.') if s.strip()])
        avg_sentence_length = len(words) / max(sentence_count, 1)
        
        complexity = (avg_word_length * 0.3) + (avg_sentence_length * 0.7)
        return min(complexity / 10, 1)  # Normalize to 0-1
    except Exception as e:
        print(f"Error calculating content complexity: {str(e)}")
        return 0

def generate_playlist_seo_insights(playlist_scores, best_playlist):
    """Generate SEO insights for playlist assignment"""
    try:
        insights = []
        best_data = playlist_scores[best_playlist]
        
        # Confidence analysis
        if best_data["score"] > 5:
            insights.append("🎯 Strong content alignment with target playlist")
        elif best_data["score"] > 2:
            insights.append("📊 Moderate content alignment - consider keyword optimization")
        else:
            insights.append("⚠️ Weak content alignment - review playlist targeting")
        
        # SEO tag recommendations
        seo_tags = best_data["seo_tags"]
        insights.append(f"🏷️ Recommended SEO tags: {', '.join(seo_tags[:3])}")
        
        # Content optimization suggestions
        if best_data["keyword_matches"] < 3:
            insights.append("💡 Add more relevant keywords to improve playlist targeting")
        
        return " • ".join(insights)
    except Exception as e:
        print(f"Error generating playlist SEO insights: {str(e)}")
        return "📈 Basic playlist assignment completed"

def generate_playlist_recommendations(playlist_scores, best_playlist, confidence):
    """Generate actionable playlist recommendations"""
    try:
        recommendations = []
        
        if confidence > 80:
            recommendations.append("✅ Excellent playlist match - proceed with confidence")
        elif confidence > 60:
            recommendations.append("📝 Good match - consider adding more specific keywords")
        else:
            recommendations.append("🔄 Consider content revision for better playlist alignment")
        
        # SEO optimization recommendations
        best_data = playlist_scores[best_playlist]
        if len(best_data["seo_tags"]) > 3:
            recommendations.append(f"🎯 Focus on primary tags: {', '.join(best_data['seo_tags'][:3])}")
        
        # Cross-playlist opportunities
        high_scoring_playlists = [name for name, data in playlist_scores.items() if data["score"] > 1 and name != best_playlist]
        if len(high_scoring_playlists) > 1:
            recommendations.append(f"🔗 Consider series spanning: {', '.join(high_scoring_playlists[:2])}")
        
        return recommendations
    except Exception as e:
        print(f"Error generating playlist recommendations: {str(e)}")
        return ["📋 Standard playlist assignment completed"]

def generate_default_playlist_assignment(content):
    """Generate default assignment when no clear match is found"""
    try:
        return {
            "primary_playlist": {
                "name": "General Content",
                "confidence": 50.0,
                "score": 1.0,
                "seo_tags": ["general", "content", "video"],
                "description": "General content that doesn't fit specific categories"
            },
            "alternative_playlists": [
                {
                    "name": "Miscellaneous",
                    "confidence": 30.0,
                    "score": 0.6,
                    "seo_tags": ["misc", "various", "content"]
                }
            ],
            "content_analysis": {"keywords": [], "topics": ["general"], "primary_topic": "general"},
            "seo_insights": "⚠️ No clear playlist match found - consider adding more specific keywords to improve categorization",
            "recommendations": ["📝 Add specific topic keywords", "🎯 Define clear content focus", "🔄 Consider content restructuring"]
        }
    except Exception as e:
        print(f"Error generating default playlist assignment: {str(e)}")
        return {"error": "Could not generate playlist assignment"}

def generate_error_playlist_assignment(error_message):
    """Generate error response for playlist assignment"""
    return {
        "error": f"Playlist assignment failed: {error_message}",
        "primary_playlist": None,
        "alternative_playlists": [],
        "content_analysis": {},
        "seo_insights": "❌ Unable to analyze content for playlist assignment",
        "recommendations": ["🔧 Check content format", "📞 Contact support if issue persists"]
    }

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