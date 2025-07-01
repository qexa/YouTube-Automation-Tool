document.addEventListener('DOMContentLoaded', function() {
    const titleForm = document.getElementById('title-form');
    const transcriptionForm = document.getElementById('transcription-form');
    const descriptionForm = document.getElementById('description-form');
    const playlistForm = document.getElementById('playlist-form');
    const numberForm = document.getElementById('number-form');
    const uploadForm = document.getElementById('upload-form');
    const customThumbnailForm = document.getElementById('custom-thumbnail-form');
    const videoThumbnailForm = document.getElementById('video-thumbnail-form');

    titleForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const content = document.getElementById('title-content').value;
        try {
            const response = await fetch('/generate_title', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content: content})
            });
            const data = await response.json();
            document.getElementById('generated-title').textContent = data.title;
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('generated-title').textContent = 'Error generating title. Please try again.';
        }
    });

    transcriptionForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const audioFile = document.getElementById('audio-file').files[0];
        const language = document.getElementById('transcription-language').value;
        const autoDetect = document.getElementById('auto-detect-language').checked;
        
        if (!audioFile) {
            showTranscriptionError('Please select an audio file');
            return;
        }
        
        // Show loading state
        showTranscriptionLoading(true);
        hideTranscriptionResults();
        
        const formData = new FormData();
        formData.append('audio', audioFile);
        formData.append('language', language);
        formData.append('auto_detect', autoDetect.toString());
        
        try {
            const response = await fetch('/transcribe', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (data.error) {
                showTranscriptionError(data.error);
            } else {
                showTranscriptionResults(data);
                showAudioInfo(data.audio_features);
            }
        } catch (error) {
            console.error('Error:', error);
            showTranscriptionError('Error during transcription. Please try again.');
        } finally {
            showTranscriptionLoading(false);
        }
    });

    // Language detection button handler
    document.getElementById('detect-language-btn').addEventListener('click', async function() {
        const audioFile = document.getElementById('audio-file').files[0];
        
        if (!audioFile) {
            alert('Please select an audio file first');
            return;
        }
        
        this.disabled = true;
        this.textContent = 'Detecting...';
        
        const formData = new FormData();
        formData.append('audio', audioFile);
        
        try {
            const response = await fetch('/detect_language', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (data.detected_language) {
                document.getElementById('transcription-language').value = data.detected_language;
                document.getElementById('auto-detect-language').checked = false;
            }
        } catch (error) {
            console.error('Error detecting language:', error);
        } finally {
            this.disabled = false;
            this.textContent = 'Detect Language';
        }
    });

    // Copy and export handlers
    document.getElementById('copy-transcription').addEventListener('click', function() {
        const text = document.getElementById('transcription').textContent;
        copyToClipboard(text, 'Transcription copied to clipboard!');
    });

    document.getElementById('copy-summary').addEventListener('click', function() {
        const text = document.getElementById('summary').textContent;
        copyToClipboard(text, 'Summary copied to clipboard!');
    });

    document.getElementById('export-transcript').addEventListener('click', function() {
        const transcription = document.getElementById('transcription').textContent;
        const summary = document.getElementById('summary').textContent;
        
        const content = `TRANSCRIPTION:\n${transcription}\n\nSUMMARY:\n${summary}`;
        downloadAsFile(content, 'transcription.txt', 'text/plain');
    });

    descriptionForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const content = document.getElementById('description-content').value;
        const videoContent = document.getElementById('video-content').value;
        
        if (!content.trim() || !videoContent.trim()) {
            showDescriptionError('Please fill in both the original description and video content');
            return;
        }
        
        // Get enhancement options
        const enhancementOptions = {
            content: content,
            video_content: videoContent,
            include_seo: document.getElementById('include-seo').checked,
            include_hashtags: document.getElementById('include-hashtags').checked,
            include_call_to_action: document.getElementById('include-cta').checked,
            include_social_links: document.getElementById('include-social').checked,
            target_audience: document.getElementById('target-audience').value,
            video_category: document.getElementById('video-category').value
        };
        
        showDescriptionLoading(true);
        hideDescriptionResults();
        
        try {
            const response = await fetch('/enhance_description', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(enhancementOptions)
            });
            const data = await response.json();
            
            if (data.error) {
                showDescriptionError(data.error);
            } else {
                showDescriptionResults(data);
            }
        } catch (error) {
            console.error('Error:', error);
            showDescriptionError('Error enhancing description. Please try again.');
        } finally {
            showDescriptionLoading(false);
        }
    });

    // Content analysis button handler
    document.getElementById('analyze-content-btn').addEventListener('click', async function() {
        const content = document.getElementById('video-content').value;
        
        if (!content.trim()) {
            alert('Please enter video content to analyze');
            return;
        }
        
        this.disabled = true;
        this.textContent = 'Analyzing...';
        
        try {
            const response = await fetch('/analyze_content', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content: content})
            });
            const data = await response.json();
            
            showContentAnalysis(data);
        } catch (error) {
            console.error('Error analyzing content:', error);
        } finally {
            this.disabled = false;
            this.textContent = 'Analyze Content';
        }
    });

    // Copy, export, and use handlers for descriptions
    document.getElementById('copy-description').addEventListener('click', function() {
        const text = document.getElementById('enhanced-description').textContent;
        copyToClipboard(text, 'Description copied to clipboard!');
    });

    document.getElementById('export-description').addEventListener('click', function() {
        const description = document.getElementById('enhanced-description').textContent;
        downloadAsFile(description, 'enhanced-description.txt', 'text/plain');
    });

    document.getElementById('use-for-upload').addEventListener('click', function() {
        const description = document.getElementById('enhanced-description').textContent;
        const uploadDescriptionField = document.getElementById('upload-description');
        if (uploadDescriptionField) {
            uploadDescriptionField.value = description;
            uploadDescriptionField.scrollIntoView({ behavior: 'smooth' });
            
            // Highlight the field briefly
            uploadDescriptionField.classList.add('border-success');
            setTimeout(() => {
                uploadDescriptionField.classList.remove('border-success');
            }, 2000);
        }
    });

    playlistForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const transcription = document.getElementById('playlist-transcription').value;
        const response = await fetch('/assign_playlist', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({transcription: transcription})
        });
        const data = await response.json();
        document.getElementById('assigned-playlist').textContent = `Assigned Playlist: ${data.playlist || 'None'}`;
        document.getElementById('playlist-certainty').textContent = `Certainty: ${data.certainty.toFixed(2)}%`;
        
        if (data.certainty >= 50 && data.certainty < 95) {
            const confirmAssignment = confirm(`Playlist "${data.playlist}" assigned with ${data.certainty.toFixed(2)}% certainty. Do you want to confirm this assignment?`);
            if (confirmAssignment) {
                document.getElementById('assigned-playlist').textContent += " (Confirmed)";
            } else {
                document.getElementById('assigned-playlist').textContent = "Playlist assignment rejected";
            }
        }
    });

    numberForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const videoType = document.getElementById('video-type').value;
        const parentNumber = document.getElementById('parent-number').value;
        const response = await fetch('/generate_number', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({video_type: videoType, parent_number: parentNumber})
        });
        const data = await response.json();
        document.getElementById('generated-number').textContent = data.number;
        updateHierarchyVisualization(data.number);
    });

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData();
        formData.append('title', document.getElementById('upload-title').value);
        formData.append('description', document.getElementById('upload-description').value);
        formData.append('tags', document.getElementById('upload-tags').value);
        formData.append('category_id', document.getElementById('upload-category').value);
        formData.append('privacy_status', document.getElementById('upload-privacy').value);
        formData.append('video', document.getElementById('upload-file').files[0]);

        const response = await fetch('/upload_video', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.success) {
            document.getElementById('upload-result').textContent = `Video uploaded successfully. Video ID: ${data.video_id}`;
        } else {
            document.getElementById('upload-result').textContent = `Failed to upload video: ${data.error}`;
        }
    });

    // Video Tags and Category Management handlers
    const tagsForm = document.getElementById('tags-form');
    const tagsCountSlider = document.getElementById('tags-count');
    const tagsCountDisplay = document.getElementById('tags-count-display');

    // Update tag count display
    if (tagsCountSlider && tagsCountDisplay) {
        tagsCountSlider.addEventListener('input', function() {
            tagsCountDisplay.textContent = this.value;
        });
    }

    // Tags form submission
    if (tagsForm) {
        tagsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const content = document.getElementById('tags-content').value;
            
            if (!content.trim()) {
                showTagsError('Please enter video content to generate tags');
                return;
            }
            
            const options = {
                content: content,
                max_tags: parseInt(document.getElementById('tags-count').value),
                include_keywords: document.getElementById('include-keywords').checked,
                include_trending: document.getElementById('include-trending').checked,
                include_long_tail: document.getElementById('include-long-tail').checked,
                include_branded: document.getElementById('include-branded').checked,
                language: document.getElementById('tags-language').value,
                category: document.getElementById('tags-category').value
            };
            
            showTagsLoading(true);
            hideTagsResults();
            
            try {
                const response = await fetch('/generate_tags', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(options)
                });
                const data = await response.json();
                
                if (data.error) {
                    showTagsError(data.error);
                } else {
                    showTagsResults(data);
                }
            } catch (error) {
                console.error('Error:', error);
                showTagsError('Error generating tags. Please try again.');
            } finally {
                showTagsLoading(false);
            }
        });
    }

    // Content analysis button
    document.getElementById('analyze-tags-btn').addEventListener('click', async function() {
        const content = document.getElementById('tags-content').value;
        
        if (!content.trim()) {
            alert('Please enter video content to analyze');
            return;
        }
        
        this.disabled = true;
        this.textContent = 'Analyzing...';
        
        try {
            const response = await fetch('/analyze_tags_content', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content: content})
            });
            const data = await response.json();
            
            showTagsAnalysis(data.analysis);
        } catch (error) {
            console.error('Error analyzing content:', error);
        } finally {
            this.disabled = false;
            this.textContent = 'Analyze Content First';
        }
    });

    // Category suggestion button
    document.getElementById('suggest-category-btn').addEventListener('click', async function() {
        const content = document.getElementById('tags-content').value;
        
        if (!content.trim()) {
            alert('Please enter video content to suggest category');
            return;
        }
        
        this.disabled = true;
        this.textContent = 'Suggesting...';
        
        try {
            const response = await fetch('/suggest_category', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content: content})
            });
            const data = await response.json();
            
            if (data.category) {
                // Update the category dropdown
                const categorySelect = document.getElementById('tags-category');
                categorySelect.value = data.category.category_id;
                
                // Show category suggestion info
                alert(`Suggested Category: ${data.category.category_name}\nConfidence: ${data.category.confidence}\nReason: ${data.category.reason}`);
            }
        } catch (error) {
            console.error('Error suggesting category:', error);
        } finally {
            this.disabled = false;
            this.textContent = 'Suggest Category';
        }
    });

    // Copy, export, and use handlers for tags
    document.getElementById('copy-tags').addEventListener('click', function() {
        const tags = Array.from(document.querySelectorAll('#generated-tags .badge'))
            .map(badge => badge.textContent)
            .join(', ');
        copyToClipboard(tags, 'Tags copied to clipboard!');
    });

    document.getElementById('copy-category').addEventListener('click', function() {
        const categoryText = document.getElementById('recommended-category').textContent;
        copyToClipboard(categoryText, 'Category info copied to clipboard!');
    });

    document.getElementById('export-tags').addEventListener('click', function() {
        const tags = Array.from(document.querySelectorAll('#generated-tags .badge'))
            .map(badge => badge.textContent);
        const csvContent = 'Tag,Type\n' + tags.map(tag => `"${tag}","YouTube Tag"`).join('\n');
        downloadAsFile(csvContent, 'video-tags.csv', 'text/csv');
    });

    document.getElementById('use-tags-upload').addEventListener('click', function() {
        const tags = Array.from(document.querySelectorAll('#generated-tags .badge'))
            .map(badge => badge.textContent)
            .join(', ');
        
        // If upload form exists, populate the tags field
        const uploadTagsField = document.getElementById('upload-tags');
        if (uploadTagsField) {
            uploadTagsField.value = tags;
            uploadTagsField.scrollIntoView({ behavior: 'smooth' });
            
            // Highlight the field briefly
            uploadTagsField.classList.add('border-success');
            setTimeout(() => {
                uploadTagsField.classList.remove('border-success');
            }, 2000);
        } else {
            // Copy to clipboard as fallback
            copyToClipboard(tags, 'Tags copied to clipboard for upload!');
        }
    });

    // Custom thumbnail form handler
    customThumbnailForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const title = document.getElementById('thumbnail-title').value;
        const subtitle = document.getElementById('thumbnail-subtitle').value;
        const template = document.getElementById('thumbnail-template').value;
        
        hideThumbnailElements();
        
        try {
            const response = await fetch('/generate_custom_thumbnail', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title: title, subtitle: subtitle, template: template})
            });
            const data = await response.json();
            
            if (data.success) {
                showThumbnail(data.thumbnail);
            } else {
                showThumbnailError(data.error || 'Failed to generate custom thumbnail');
            }
        } catch (error) {
            console.error('Error:', error);
            showThumbnailError('Error generating custom thumbnail. Please try again.');
        }
    });

    // Video thumbnail form handler
    videoThumbnailForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const videoFile = document.getElementById('video-file').files[0];
        const title = document.getElementById('frame-title').value;
        const timestamp = document.getElementById('timestamp').value;
        
        if (!videoFile) {
            showThumbnailError('Please select a video file');
            return;
        }
        
        hideThumbnailElements();
        
        const formData = new FormData();
        formData.append('video', videoFile);
        formData.append('title', title);
        if (timestamp) {
            formData.append('timestamp', timestamp);
        }
        
        try {
            const response = await fetch('/generate_thumbnail_from_video', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (data.success) {
                showThumbnail(data.thumbnail);
            } else {
                showThumbnailError(data.error || 'Failed to generate thumbnail from video');
            }
        } catch (error) {
            console.error('Error:', error);
            showThumbnailError('Error generating thumbnail from video. Please try again.');
        }
    });

    // Download thumbnail button handler
    document.getElementById('download-thumbnail').addEventListener('click', function() {
        const img = document.getElementById('thumbnail-image');
        const link = document.createElement('a');
        link.href = img.src;
        link.download = 'youtube-thumbnail.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
});

// Description enhancement helper functions
function showDescriptionLoading(isLoading) {
    const spinner = document.getElementById('description-spinner');
    const submitBtn = document.querySelector('#description-form button[type="submit"]');
    
    if (isLoading) {
        spinner.classList.remove('d-none');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Enhancing...';
    } else {
        spinner.classList.add('d-none');
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Enhance Description';
    }
}

function showDescriptionResults(data) {
    const resultsDiv = document.getElementById('description-results');
    const errorDiv = document.getElementById('description-error');
    
    // Hide error and show results
    errorDiv.style.display = 'none';
    resultsDiv.style.display = 'block';
    
    // Update description content with proper formatting
    const descriptionDiv = document.getElementById('enhanced-description');
    descriptionDiv.innerHTML = data.description.replace(/\n/g, '<br>');
    
    // Update badges
    if (data.analysis) {
        const wordCountBadge = document.getElementById('description-word-count');
        const readTimeBadge = document.getElementById('description-read-time');
        
        wordCountBadge.textContent = `${data.analysis.word_count} words`;
        readTimeBadge.textContent = `${data.analysis.estimated_read_time} min read`;
        
        // Show insights
        showDescriptionInsights(data.analysis);
    }
}

function showDescriptionInsights(analysis) {
    const insightsDiv = document.getElementById('description-insights');
    insightsDiv.style.display = 'block';
    
    // Update insights content
    const keywordsDiv = document.getElementById('insights-keywords');
    const topicsDiv = document.getElementById('insights-topics');
    const entitiesDiv = document.getElementById('insights-entities');
    const statsDiv = document.getElementById('insights-stats');
    
    // Keywords as badges
    keywordsDiv.innerHTML = analysis.keywords.map(keyword => 
        `<span class="badge bg-primary me-1">${keyword}</span>`
    ).join('');
    
    // Topics as badges
    topicsDiv.innerHTML = analysis.topics.map(topic => 
        `<span class="badge bg-info me-1">${topic}</span>`
    ).join('');
    
    // Entities as badges
    entitiesDiv.innerHTML = analysis.entities.map(entity => 
        `<span class="badge bg-secondary me-1">${entity}</span>`
    ).join('');
    
    // Statistics
    statsDiv.innerHTML = `
        <small>Words: ${analysis.word_count}</small><br>
        <small>Read time: ${analysis.estimated_read_time} minutes</small>
    `;
}

function showDescriptionError(errorMessage) {
    const resultsDiv = document.getElementById('description-results');
    const errorDiv = document.getElementById('description-error');
    
    resultsDiv.style.display = 'none';
    errorDiv.style.display = 'block';
    errorDiv.textContent = errorMessage;
}

function hideDescriptionResults() {
    const resultsDiv = document.getElementById('description-results');
    const errorDiv = document.getElementById('description-error');
    const analysisDiv = document.getElementById('content-analysis');
    
    resultsDiv.style.display = 'none';
    errorDiv.style.display = 'none';
    analysisDiv.style.display = 'none';
}

function showContentAnalysis(data) {
    const analysisDiv = document.getElementById('content-analysis');
    analysisDiv.style.display = 'block';
    
    // Update analysis content
    const keywordsDiv = document.getElementById('analysis-keywords');
    const topicsDiv = document.getElementById('analysis-topics');
    const entitiesDiv = document.getElementById('analysis-entities');
    
    keywordsDiv.textContent = data.keywords.length > 0 ? data.keywords.join(', ') : 'None detected';
    topicsDiv.textContent = data.topics.length > 0 ? data.topics.join(', ') : 'None detected';
    entitiesDiv.textContent = data.entities.length > 0 ? data.entities.join(', ') : 'None detected';
}

// Transcription helper functions
function showTranscriptionLoading(isLoading) {
    const spinner = document.getElementById('transcription-spinner');
    const submitBtn = document.querySelector('#transcription-form button[type="submit"]');
    
    if (isLoading) {
        spinner.classList.remove('d-none');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing...';
    } else {
        spinner.classList.add('d-none');
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Transcribe Audio';
    }
}

function showTranscriptionResults(data) {
    const resultsDiv = document.getElementById('transcription-results');
    const errorDiv = document.getElementById('transcription-error');
    
    // Hide error and show results
    errorDiv.style.display = 'none';
    resultsDiv.style.display = 'block';
    
    // Update content
    document.getElementById('transcription').textContent = data.transcription;
    document.getElementById('summary').textContent = data.summary;
    
    // Update badges and metadata
    const confidenceBadge = document.getElementById('confidence-badge');
    const languageBadge = document.getElementById('language-badge');
    const wordCount = document.getElementById('word-count');
    const duration = document.getElementById('transcription-duration');
    
    confidenceBadge.textContent = `${Math.round(data.confidence * 100)}% confidence`;
    languageBadge.textContent = data.detected_language || 'Unknown';
    wordCount.textContent = data.word_count || 0;
    duration.textContent = Math.round(data.duration_seconds || 0);
    
    // Color code confidence
    confidenceBadge.className = 'badge';
    if (data.confidence >= 0.8) {
        confidenceBadge.classList.add('bg-success');
    } else if (data.confidence >= 0.6) {
        confidenceBadge.classList.add('bg-warning');
    } else {
        confidenceBadge.classList.add('bg-danger');
    }
}

function showTranscriptionError(errorMessage) {
    const resultsDiv = document.getElementById('transcription-results');
    const errorDiv = document.getElementById('transcription-error');
    
    resultsDiv.style.display = 'none';
    errorDiv.style.display = 'block';
    errorDiv.textContent = errorMessage;
}

function hideTranscriptionResults() {
    const resultsDiv = document.getElementById('transcription-results');
    const errorDiv = document.getElementById('transcription-error');
    
    resultsDiv.style.display = 'none';
    errorDiv.style.display = 'none';
}

function showAudioInfo(features) {
    const audioInfoDiv = document.getElementById('audio-info');
    
    if (!features || Object.keys(features).length === 0) {
        audioInfoDiv.style.display = 'none';
        return;
    }
    
    audioInfoDiv.style.display = 'block';
    
    // Update audio information
    document.getElementById('audio-duration').textContent = 
        features.duration_seconds ? `${Math.round(features.duration_seconds)}s` : 'Unknown';
    document.getElementById('audio-format').textContent = 
        features.format || 'Unknown';
    document.getElementById('audio-sample-rate').textContent = 
        features.sample_rate ? `${features.sample_rate} Hz` : 'Unknown';
    document.getElementById('audio-channels').textContent = 
        features.channels || 'Unknown';
    document.getElementById('audio-size').textContent = 
        features.file_size_mb ? `${features.file_size_mb.toFixed(1)} MB` : 'Unknown';
    
    // Quality assessment
    const quality = document.getElementById('audio-quality');
    if (features.sample_rate >= 44100 && features.channels >= 1) {
        quality.textContent = 'High Quality';
        quality.className = 'text-success';
    } else if (features.sample_rate >= 16000) {
        quality.textContent = 'Good Quality';
        quality.className = 'text-info';
    } else {
        quality.textContent = 'Low Quality';
        quality.className = 'text-warning';
    }
}

function copyToClipboard(text, successMessage) {
    navigator.clipboard.writeText(text).then(function() {
        // Show temporary success message
        const originalBtn = event.target;
        const originalText = originalBtn.textContent;
        originalBtn.textContent = '✓ Copied!';
        originalBtn.classList.add('btn-success');
        
        setTimeout(() => {
            originalBtn.textContent = originalText;
            originalBtn.classList.remove('btn-success');
        }, 2000);
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
        alert('Failed to copy to clipboard');
    });
}

function downloadAsFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}

// Thumbnail helper functions
function showThumbnail(base64Image) {
    const thumbnailPreview = document.getElementById('thumbnail-preview');
    const thumbnailImage = document.getElementById('thumbnail-image');
    const thumbnailError = document.getElementById('thumbnail-error');
    
    thumbnailImage.src = `data:image/png;base64,${base64Image}`;
    thumbnailPreview.style.display = 'block';
    thumbnailError.style.display = 'none';
}

function showThumbnailError(errorMessage) {
    const thumbnailPreview = document.getElementById('thumbnail-preview');
    const thumbnailError = document.getElementById('thumbnail-error');
    
    thumbnailError.textContent = errorMessage;
    thumbnailError.style.display = 'block';
    thumbnailPreview.style.display = 'none';
}

function hideThumbnailElements() {
    const thumbnailPreview = document.getElementById('thumbnail-preview');
    const thumbnailError = document.getElementById('thumbnail-error');
    
    thumbnailPreview.style.display = 'none';
    thumbnailError.style.display = 'none';
}

function updateHierarchyVisualization(number) {
    const visualization = document.getElementById('hierarchy-visualization');
    const parts = number.split('.');
    let html = '<ul class="tree">';

    for (let i = 0; i < parts.length; i++) {
        const currentNumber = parts.slice(0, i + 1).join('.');
        html += `<li>
            <span class="node">${currentNumber}</span>
            ${i < parts.length - 1 ? '<ul>' : ''}
        `;
    }

    html += '</ul>'.repeat(parts.length);
    visualization.innerHTML = html;
}

const style = document.createElement('style');
style.textContent = `
    .tree, .tree ul {
        list-style-type: none;
        padding-left: 20px;
    }
    .tree .node {
        padding: 5px 10px;
        border: 1px solid #ddd;
        display: inline-block;
        border-radius: 5px;
        margin: 5px 0;
    }
`;
document.head.appendChild(style);