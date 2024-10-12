import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import random
import speech_recognition as sr
from pydub import AudioSegment

nltk.download('punkt')
nltk.download('stopwords')

def generate_title(content):
    # Simple title generation based on most common words
    words = word_tokenize(content.lower())
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    word_freq = nltk.FreqDist(filtered_words)
    common_words = word_freq.most_common(3)
    title = " ".join(word for word, _ in common_words).capitalize()
    return title

def transcribe_audio(audio_file):
    # Convert audio file to wav format
    audio = AudioSegment.from_file(audio_file)
    audio.export("temp.wav", format="wav")

    # Transcribe audio
    recognizer = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)
        transcription = recognizer.recognize_google(audio_data)

    # Generate simple summary (first 100 words)
    words = transcription.split()
    summary = " ".join(words[:100])

    return transcription, summary

def enhance_description(content):
    social_media_links = """
    Follow us on social media:
    - Twitter: https://twitter.com/our_channel
    - Instagram: https://instagram.com/our_channel
    - Facebook: https://facebook.com/our_channel
    """
    enhanced_description = f"{content}\n\n{social_media_links}"
    return enhanced_description

def assign_playlist(transcription):
    # Simple playlist assignment based on keywords
    playlists = {
        "tech": ["technology", "coding", "programming"],
        "lifestyle": ["fashion", "food", "travel"],
        "education": ["learn", "study", "school"],
    }

    transcription_lower = transcription.lower()
    for playlist, keywords in playlists.items():
        if any(keyword in transcription_lower for keyword in keywords):
            return playlist

    return "miscellaneous"

def generate_hierarchical_number(video_type, parent_number=None):
    if video_type == "main":
        return f"{random.randint(1, 999):03d}"
    elif video_type == "follow_up":
        main_number, *_ = parent_number.split('.')
        return f"{main_number}.{random.randint(1, 99):02d}"
    elif video_type == "clarification":
        main_number, sub_number = parent_number.split('.')
        return f"{main_number}.{sub_number}{chr(random.randint(65, 90))}"
