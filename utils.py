import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import random
import speech_recognition as sr
from pydub import AudioSegment
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os

nltk.download('punkt')
nltk.download('stopwords')

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

def transcribe_audio(audio_file):
    try:
        audio = AudioSegment.from_file(audio_file)
        audio.export("temp.wav", format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile("temp.wav") as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_data)

        words = transcription.split()
        summary = " ".join(words[:100])

        return transcription, summary
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        return "Unable to transcribe audio", "No summary available"

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