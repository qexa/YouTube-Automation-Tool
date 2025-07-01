# YouTube Video Automation Tool

## Overview

This is a YouTube video automation tool built with Flask that streamlines the process of preparing and uploading YouTube videos. The application automates tasks such as title generation, audio transcription, description enhancement, playlist assignment, and hierarchical numbering for content organization.

## System Architecture

### Frontend Architecture
- **Framework**: HTML/CSS/JavaScript with Bootstrap 5 (dark theme)
- **UI Pattern**: Server-side rendered templates with AJAX for dynamic interactions
- **Styling**: Bootstrap CSS framework with custom CSS overrides
- **JavaScript**: Vanilla JavaScript for form handling and API calls

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **API Design**: RESTful endpoints for different automation features
- **File Structure**: Modular design with separate files for models, utilities, and routes

### Data Storage
- **Primary Database**: SQLite for development/testing
- **ORM**: SQLAlchemy with declarative base model
- **Schema**: Single Video model with fields for title, description, transcription, summary, playlist, and hierarchical numbering

## Key Components

### Core Models
- **Video Model**: Stores video metadata including title, description, transcription, summary, playlist assignment, and hierarchical number

### Utility Functions
- **Title Generation**: Uses NLTK for natural language processing to extract keywords and generate catchy titles
- **Audio Transcription**: Advanced speech recognition with multi-language support, confidence scoring, and intelligent summarization
- **Description Enhancement**: Adds fixed social media links and generates content-based descriptions
- **Playlist Assignment**: Analyzes transcription to determine appropriate playlist with certainty levels
- **Hierarchical Numbering**: Implements a structured numbering system (#001, #002.1, #002.2A, etc.)
- **Thumbnail Generation**: Creates custom thumbnails and extracts frames from videos with text overlays

### API Endpoints
- `/generate_title` - POST endpoint for automatic title generation
- `/transcribe` - POST endpoint for enhanced audio transcription with language detection and confidence scoring
- `/detect_language` - POST endpoint for automatic language detection from audio
- `/enhance_description` - POST endpoint for description enhancement
- `/assign_playlist` - POST endpoint for playlist assignment
- `/generate_thumbnail_from_video` - POST endpoint for creating thumbnails from video frames
- `/generate_custom_thumbnail` - POST endpoint for creating custom thumbnails with text overlays

### External Integrations
- **YouTube API**: For video uploads and metadata management
- **Google Speech Recognition**: For audio transcription
- **NLTK**: For natural language processing tasks

## Data Flow

1. **Video Upload**: User uploads video file through web interface
2. **Audio Extraction**: System extracts audio from video for transcription
3. **Content Analysis**: NLTK processes content for title generation and description enhancement
4. **Playlist Assignment**: Machine learning algorithm analyzes transcription to determine playlist with confidence levels
5. **Hierarchical Numbering**: System assigns structured numbers based on content classification
6. **YouTube Upload**: Automated upload to YouTube with all generated metadata

## External Dependencies

### Python Libraries
- Flask - Web framework
- SQLAlchemy - Database ORM
- NLTK - Natural language processing
- speech_recognition - Audio transcription
- google-auth-oauthlib - YouTube API authentication
- googleapiclient - YouTube API client
- pydub - Audio processing
- OpenCV - Video processing
- Pillow - Image processing

### Third-party Services
- Google YouTube Data API v3
- Google Speech-to-Text API

### Authentication Requirements
- OAuth 2.0 client credentials for YouTube API access
- Client secret JSON file required in project root

## Deployment Strategy

### Development Environment
- Local Flask development server on port 5000
- SQLite database for local development
- Environment variables for configuration

### Production Considerations
- Database migration to PostgreSQL recommended for production
- Environment-specific configuration for API keys and secrets
- WSGI server deployment (Gunicorn recommended)
- SSL/HTTPS configuration for OAuth flows

### Configuration Management
- Flask secret key via environment variables
- Database URI configurable via environment
- OAuth credentials stored securely

## Recent Changes

- **July 01, 2025**: Enhanced Audio Transcription and Summary section with advanced features:
  - Multi-language support (10+ languages including English, Spanish, French, German, etc.)
  - Automatic language detection from audio content
  - Confidence scoring for transcription accuracy
  - Intelligent summarization using sentence scoring algorithms
  - Audio file analysis (duration, format, quality assessment)
  - Copy/export functionality for transcriptions and summaries
  - Professional UI with loading states and error handling
  - Enhanced API endpoints with detailed metadata

- **July 01, 2025**: Added comprehensive Thumbnail Generator feature:
  - Custom thumbnail creation with text overlays and background templates
  - Video frame extraction for thumbnail generation
  - Multiple template options (gradient, solid, pattern backgrounds)
  - Download functionality for generated thumbnails
  - Professional thumbnail sizing (1280x720 YouTube standard)

## Changelog

- July 01, 2025: Initial setup and core features implementation

## User Preferences

Preferred communication style: Simple, everyday language.