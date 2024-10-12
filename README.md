# YouTube Video Automation Tool

This tool streamlines the process of preparing and uploading YouTube videos by automating various tasks such as title generation, audio transcription, description enhancement, playlist assignment, and video uploading.

## Features

1. Automatic Title Generation
2. Audio Transcription and Summary
3. Description Enhancement
4. YouTube Fields Automation
5. Enhanced Playlist Assignment
6. Hierarchical Numbering System
7. Visualization Interface for Content Hierarchy

## Setup and Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up YouTube API credentials:
   - Go to the [Google Developers Console](https://console.developers.google.com/)
   - Create a new project and enable the YouTube Data API v3
   - Create credentials (OAuth 2.0 client ID)
   - Download the client configuration and save it as `client_secret.json` in the project root

## Usage

1. Run the Flask application:
   ```
   python main.py
   ```
2. Open a web browser and navigate to `http://localhost:5000`
3. Use the web interface to access the various features of the tool

## Compliance with YouTube Policies and Guidelines

To ensure compliance with YouTube's policies and guidelines, please consider the following:

1. Content Policy: Ensure that all uploaded content complies with YouTube's Community Guidelines and Terms of Service.
2. Copyright: Only upload content that you have the rights to use and distribute.
3. Metadata: Provide accurate and non-misleading titles, descriptions, and tags for your videos.
4. Privacy: Respect the privacy of individuals featured in your videos and obtain necessary permissions.
5. Age Restrictions: Properly age-restrict content that may not be suitable for all audiences.
6. Advertising: Follow YouTube's advertiser-friendly content guidelines if you plan to monetize your videos.
7. Spam and Deceptive Practices: Avoid using the tool for spam, scams, or artificially inflating view counts.

For a comprehensive understanding of YouTube's policies, please refer to the [YouTube Policies and Safety](https://www.youtube.com/about/policies/) page.

## Limitations and Disclaimer

This tool is designed to assist content creators in automating certain aspects of video uploading and management. However, it should not be used as a replacement for human judgment and oversight. Always review and verify the output of the tool before publishing content to ensure accuracy and compliance with YouTube's policies.

The developers of this tool are not responsible for any violations of YouTube's terms of service or community guidelines resulting from the use of this software. Use at your own discretion and responsibility.
