document.addEventListener('DOMContentLoaded', function() {
    const titleForm = document.getElementById('title-form');
    const transcriptionForm = document.getElementById('transcription-form');
    const descriptionForm = document.getElementById('description-form');
    const playlistForm = document.getElementById('playlist-form');
    const numberForm = document.getElementById('number-form');
    const uploadForm = document.getElementById('upload-form');
    const customThumbnailForm = document.getElementById('custom-thumbnail-form');
    const videoThumbnailForm = document.getElementById('video-thumbnail-form');
    
    // Initialize enhanced description features
    initializeDescriptionEnhancements();

    titleForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const content = document.getElementById('title-content').value;
        
        // Show loading state
        showTitleLoading(true);
        hideTitleResults();
        
        try {
            const response = await fetch('/generate_title', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content: content})
            });
            const data = await response.json();
            
            if (data.success) {
                showTitleResults(data);
            } else {
                showTitleError(data.error || 'Error generating titles');
            }
        } catch (error) {
            console.error('Error:', error);
            showTitleError('Error generating titles. Please try again.');
        } finally {
            showTitleLoading(false);
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

    // Comprehensive Playlist Assignment functionality
    const analyzePlaylistBtn = document.getElementById('analyze-playlist-content');
    
    // Analyze playlist content first
    analyzePlaylistBtn?.addEventListener('click', async function() {
        const content = document.getElementById('playlist-content').value;
        
        if (!content.trim()) {
            showPlaylistError('Please enter content to analyze');
            return;
        }
        
        try {
            showPlaylistAnalysisLoading(true);
            hidePlaylistResults();
            
            const response = await fetch('/analyze_playlist_content', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content: content})
            });
            
            const data = await response.json();
            
            if (data.success) {
                showPlaylistAnalysisResults(data.analysis);
            } else {
                showPlaylistError(data.error || 'Failed to analyze content');
            }
        } catch (error) {
            showPlaylistError('Network error occurred while analyzing content');
        } finally {
            showPlaylistAnalysisLoading(false);
        }
    });

    // Playlist form submission with comprehensive analysis
    playlistForm?.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const content = document.getElementById('playlist-content').value;
        const language = document.getElementById('playlist-language').value;
        const enableSeoInsights = document.getElementById('enable-seo-insights').checked;
        const enableAlternatives = document.getElementById('enable-alternatives').checked;
        const enableRecommendations = document.getElementById('enable-recommendations').checked;
        
        if (!content.trim()) {
            showPlaylistError('Please enter content for playlist assignment');
            return;
        }
        
        try {
            showPlaylistLoading(true);
            hidePlaylistResults();
            
            const response = await fetch('/assign_playlist', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    content: content,
                    options: {
                        language: language,
                        enable_seo_insights: enableSeoInsights,
                        enable_alternatives: enableAlternatives,
                        enable_recommendations: enableRecommendations
                    }
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showPlaylistResults(data.assignment);
            } else {
                showPlaylistError(data.error || 'Failed to assign playlist');
            }
        } catch (error) {
            showPlaylistError('Network error occurred while assigning playlist');
        } finally {
            showPlaylistLoading(false);
        }
    });

    // Export functionality for playlist data
    document.getElementById('copy-playlist-data')?.addEventListener('click', function() {
        const playlistData = getPlaylistDataForExport();
        copyToClipboard(playlistData, 'Playlist data copied to clipboard!');
    });

    document.getElementById('export-playlist-json')?.addEventListener('click', function() {
        const playlistData = getPlaylistDataForExport();
        downloadAsFile(playlistData, 'playlist-assignment.json', 'application/json');
    });

    document.getElementById('use-playlist-for-upload')?.addEventListener('click', function() {
        // This would integrate with video upload functionality
        alert('Playlist data prepared for video upload integration!');
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

// Title Generation helper functions
function showTitleLoading(isLoading) {
    const submitBtn = document.querySelector('#title-form button[type="submit"]');
    
    if (isLoading) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating Titles...';
    } else {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" id="title-spinner" style="display: none;"></span>Generate Titles';
    }
}

function showTitleResults(data) {
    const resultsDiv = document.getElementById('generated-title');
    
    let html = '<div class="mt-3">';
    html += '<h4 class="text-success mb-3"><i class="bi bi-lightbulb"></i> Generated Title Variations</h4>';
    
    // Display title variations
    html += '<div class="row">';
    data.titles.forEach((title, index) => {
        html += `
            <div class="col-12 mb-3">
                <div class="card border-info">
                    <div class="card-body">
                        <h6 class="card-subtitle mb-2 text-muted">Title Option ${index + 1}</h6>
                        <h5 class="card-title">${title}</h5>
                        <small class="text-muted">${title.length} characters</small>
                        <div class="mt-2">
                            <button class="btn btn-sm btn-outline-primary me-2" onclick="copyToClipboard(\`${title}\`, 'Title copied!')">
                                <i class="bi bi-clipboard"></i> Copy
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    // Display content analysis
    if (data.analysis && Object.keys(data.analysis).length > 0) {
        html += '<div class="mt-4">';
        html += '<h5 class="text-info mb-3"><i class="bi bi-graph-up"></i> Content Analysis</h5>';
        html += '<div class="row">';
        
        // Keywords
        if (data.analysis.keywords && data.analysis.keywords.length > 0) {
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card h-100">
                        <div class="card-body">
                            <h6 class="card-title">Key Terms</h6>
                            <div class="d-flex flex-wrap gap-1">
                                ${data.analysis.keywords.slice(0, 5).map(keyword => 
                                    `<span class="badge bg-primary">${keyword}</span>`
                                ).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Content metrics
        html += `
            <div class="col-md-6 mb-3">
                <div class="card h-100">
                    <div class="card-body">
                        <h6 class="card-title">Content Metrics</h6>
                        <small class="text-muted">
                            Words: ${data.analysis.word_count || 0} | 
                            Topic: ${data.analysis.primary_topic || 'General'} | 
                            Type: ${data.analysis.content_type || 'Unknown'}
                        </small>
                    </div>
                </div>
            </div>
        `;
        
        html += '</div></div>';
    }
    
    // Display engagement insights
    if (data.engagement_insights && data.engagement_insights.length > 0) {
        html += '<div class="mt-4">';
        html += '<h5 class="text-success mb-3"><i class="bi bi-graph-up-arrow"></i> Engagement Insights</h5>';
        html += '<div class="row">';
        data.engagement_insights.forEach(insight => {
            html += `
                <div class="col-12 mb-2">
                    <div class="alert alert-success d-flex align-items-center" role="alert">
                        <i class="bi bi-check-circle-fill me-2"></i>
                        <div>${insight}</div>
                    </div>
                </div>
            `;
        });
        html += '</div></div>';
    }
    
    // Display optimization recommendations
    if (data.recommendations && data.recommendations.length > 0) {
        html += '<div class="mt-4">';
        html += '<h5 class="text-warning mb-3"><i class="bi bi-lightbulb"></i> Optimization Tips</h5>';
        html += '<ul class="list-group list-group-flush">';
        data.recommendations.forEach(rec => {
            html += `<li class="list-group-item"><i class="bi bi-arrow-right text-warning me-2"></i>${rec}</li>`;
        });
        html += '</ul></div>';
    }
    
    // Action buttons
    html += `
        <div class="mt-4 d-flex gap-2 flex-wrap">
            <button class="btn btn-success" onclick="copyAllTitles()">
                <i class="bi bi-clipboard-check"></i> Copy All Titles
            </button>
            <button class="btn btn-info" onclick="exportTitleData()">
                <i class="bi bi-download"></i> Export as Text
            </button>
        </div>
    `;
    
    html += '</div>';
    resultsDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
}

function showTitleError(errorMessage) {
    const resultsDiv = document.getElementById('generated-title');
    resultsDiv.innerHTML = `
        <div class="alert alert-danger mt-3">
            <i class="bi bi-exclamation-triangle"></i> Error: ${errorMessage}
        </div>
    `;
    resultsDiv.style.display = 'block';
}

function hideTitleResults() {
    const resultsDiv = document.getElementById('generated-title');
    resultsDiv.style.display = 'none';
    resultsDiv.innerHTML = '';
}

function copyAllTitles() {
    const titles = Array.from(document.querySelectorAll('#generated-title .card-title'))
        .map(el => el.textContent)
        .join('\n\n');
    
    copyToClipboard(titles, 'All titles copied to clipboard!');
}

function exportTitleData() {
    const titleElements = document.querySelectorAll('#generated-title .card-title');
    const analysisText = document.querySelector('#generated-title .text-info')?.textContent || '';
    const recommendations = Array.from(document.querySelectorAll('#generated-title .list-group-item'))
        .map(el => el.textContent.replace('→', '•'))
        .join('\n');
    
    let content = 'GENERATED YOUTUBE TITLES\n';
    content += '========================\n\n';
    
    titleElements.forEach((titleEl, index) => {
        content += `${index + 1}. ${titleEl.textContent}\n`;
    });
    
    if (analysisText) {
        content += '\nCONTENT ANALYSIS\n';
        content += '================\n';
        content += analysisText + '\n';
    }
    
    if (recommendations) {
        content += '\nOPTIMIZATION RECOMMENDATIONS\n';
        content += '============================\n';
        content += recommendations + '\n';
    }
    
    content += '\nGenerated by YouTube Video Automation Tool\n';
    
    downloadAsFile(content, 'youtube_titles.txt', 'text/plain');
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

// Tags and Category Management helper functions
function showTagsLoading(isLoading) {
    const spinner = document.getElementById('tags-spinner');
    const submitBtn = document.querySelector('#tags-form button[type="submit"]');
    
    if (isLoading) {
        spinner.classList.remove('d-none');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Generating Tags...';
    } else {
        spinner.classList.add('d-none');
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Generate Tags';
    }
}

function showTagsResults(data) {
    const resultsDiv = document.getElementById('tags-results');
    const errorDiv = document.getElementById('tags-error');
    
    // Hide error and show results
    errorDiv.style.display = 'none';
    resultsDiv.style.display = 'block';
    
    // Update tags display
    const tagsDiv = document.getElementById('generated-tags');
    tagsDiv.innerHTML = data.tags.map(tag => 
        `<span class="badge bg-primary me-1 mb-1">${tag}</span>`
    ).join('');
    
    // Update badges
    document.getElementById('tags-count-badge').textContent = `${data.tags.length} tags`;
    document.getElementById('category-badge').textContent = data.category.category_name;
    
    // Update metrics
    document.getElementById('tags-character-count').textContent = data.character_count;
    document.getElementById('tags-seo-score').textContent = `${data.seo_score}/100`;
    
    // Update category recommendation
    const categoryDiv = document.getElementById('recommended-category');
    categoryDiv.innerHTML = `
        <strong>${data.category.category_name}</strong> (ID: ${data.category.category_id})<br>
        <small class="text-muted">Confidence: ${data.category.confidence} - ${data.category.reason}</small>
    `;
    
    // Update insights
    document.getElementById('tags-insights').textContent = data.insights;
}

function showTagsAnalysis(analysis) {
    const analysisDiv = document.getElementById('tags-analysis');
    analysisDiv.style.display = 'block';
    
    // Update analysis content
    const topicsDiv = document.getElementById('analysis-topics-tags');
    const entitiesDiv = document.getElementById('analysis-entities-tags');
    const scoreDiv = document.getElementById('analysis-score-tags');
    
    // Topics as badges
    topicsDiv.innerHTML = analysis.topics.map(topic => 
        `<span class="badge bg-info me-1">${topic}</span>`
    ).join('');
    
    // Entities as badges
    entitiesDiv.innerHTML = analysis.entities.map(entity => 
        `<span class="badge bg-secondary me-1">${entity}</span>`
    ).join('');
    
    // Quality score
    const scoreColor = analysis.quality_score >= 80 ? 'success' : 
                      analysis.quality_score >= 60 ? 'warning' : 'danger';
    scoreDiv.innerHTML = `
        <div class="progress">
            <div class="progress-bar bg-${scoreColor}" style="width: ${analysis.quality_score}%">
                ${analysis.quality_score}/100
            </div>
        </div>
        <small class="text-muted">${analysis.content_type} content • ${analysis.tag_potential} tag potential</small>
    `;
}

function showTagsError(errorMessage) {
    const resultsDiv = document.getElementById('tags-results');
    const errorDiv = document.getElementById('tags-error');
    
    resultsDiv.style.display = 'none';
    errorDiv.style.display = 'block';
    errorDiv.textContent = errorMessage;
}

function hideTagsResults() {
    const resultsDiv = document.getElementById('tags-results');
    const errorDiv = document.getElementById('tags-error');
    const analysisDiv = document.getElementById('tags-analysis');
    
    resultsDiv.style.display = 'none';
    errorDiv.style.display = 'none';
    analysisDiv.style.display = 'none';
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

// Playlist Assignment helper functions
function showPlaylistLoading(isLoading) {
    const spinner = document.getElementById('playlist-spinner');
    const submitBtn = document.querySelector('#playlist-form button[type="submit"]');
    
    if (isLoading) {
        spinner.style.display = 'inline-block';
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Assigning Playlist...';
    } else {
        spinner.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" id="playlist-spinner" style="display: none;"></span>Assign Playlist';
    }
}

function showPlaylistAnalysisLoading(isLoading) {
    const spinner = document.getElementById('playlist-analysis-spinner');
    const analyzeBtn = document.getElementById('analyze-playlist-content');
    
    if (isLoading) {
        spinner.style.display = 'inline-block';
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';
    } else {
        spinner.style.display = 'none';
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" id="playlist-analysis-spinner" style="display: none;"></span>Analyze Content First';
    }
}

function showPlaylistAnalysisResults(analysis) {
    const analysisDiv = document.getElementById('playlist-analysis-results');
    const contentDiv = document.getElementById('playlist-analysis-content');
    
    analysisDiv.style.display = 'block';
    
    contentDiv.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Content Keywords:</h6>
                <div class="mb-2">
                    ${analysis.keywords.map(keyword => `<span class="badge bg-primary me-1">${keyword}</span>`).join('')}
                </div>
                <h6>Content Topics:</h6>
                <div class="mb-2">
                    ${analysis.topics.map(topic => `<span class="badge bg-info me-1">${topic}</span>`).join('')}
                </div>
            </div>
            <div class="col-md-6">
                <h6>Content Statistics:</h6>
                <ul class="list-unstyled">
                    <li><strong>Word Count:</strong> ${analysis.word_count}</li>
                    <li><strong>Complexity Score:</strong> ${(analysis.complexity_score * 100).toFixed(1)}%</li>
                    <li><strong>Primary Topic:</strong> ${analysis.primary_topic}</li>
                </ul>
            </div>
        </div>
    `;
}

function showPlaylistResults(assignment) {
    const resultsDiv = document.getElementById('playlist-results');
    const errorDiv = document.getElementById('playlist-error');
    
    // Hide error and show results
    errorDiv.style.display = 'none';
    resultsDiv.style.display = 'block';
    
    // Update primary playlist
    const primaryDiv = document.getElementById('primary-playlist-content');
    const primary = assignment.primary_playlist;
    
    primaryDiv.innerHTML = `
        <div class="d-flex justify-content-between align-items-start mb-2">
            <h5 class="mb-0">${primary.name}</h5>
            <span class="badge bg-success">${primary.confidence}% confidence</span>
        </div>
        <p class="text-muted mb-2">${primary.description}</p>
        <div class="mb-2">
            <strong>SEO Tags:</strong>
            ${primary.seo_tags.map(tag => `<span class="badge bg-secondary me-1">${tag}</span>`).join('')}
        </div>
        <div class="text-muted">
            <small>Score: ${primary.score}</small>
        </div>
    `;
    
    // Update alternative playlists
    const alternativesDiv = document.getElementById('alternative-playlists');
    const alternativesContentDiv = document.getElementById('alternative-playlists-content');
    
    if (assignment.alternative_playlists && assignment.alternative_playlists.length > 0) {
        alternativesDiv.style.display = 'block';
        alternativesContentDiv.innerHTML = assignment.alternative_playlists.map(alt => `
            <div class="border rounded p-2 mb-2">
                <div class="d-flex justify-content-between">
                    <strong>${alt.name}</strong>
                    <span class="badge bg-outline-primary">${alt.confidence}% confidence</span>
                </div>
                <div class="mt-1">
                    ${alt.seo_tags.map(tag => `<span class="badge bg-light text-dark me-1">${tag}</span>`).join('')}
                </div>
            </div>
        `).join('');
    } else {
        alternativesDiv.style.display = 'none';
    }
    
    // Update SEO insights
    const insightsDiv = document.getElementById('playlist-insights-content');
    insightsDiv.innerHTML = `<p>${assignment.seo_insights}</p>`;
    
    // Update recommendations
    const recommendationsDiv = document.getElementById('playlist-recommendations-content');
    recommendationsDiv.innerHTML = `
        <ul class="list-unstyled">
            ${assignment.recommendations.map(rec => `<li>• ${rec}</li>`).join('')}
        </ul>
    `;
}

function showPlaylistError(errorMessage) {
    const resultsDiv = document.getElementById('playlist-results');
    const errorDiv = document.getElementById('playlist-error');
    const analysisDiv = document.getElementById('playlist-analysis-results');
    
    resultsDiv.style.display = 'none';
    analysisDiv.style.display = 'none';
    errorDiv.style.display = 'block';
    errorDiv.textContent = errorMessage;
}

function hidePlaylistResults() {
    const resultsDiv = document.getElementById('playlist-results');
    const errorDiv = document.getElementById('playlist-error');
    
    resultsDiv.style.display = 'none';
    errorDiv.style.display = 'none';
}

function getPlaylistDataForExport() {
    const resultsDiv = document.getElementById('playlist-results');
    if (resultsDiv.style.display === 'none') {
        return 'No playlist data available for export';
    }
    
    // Extract playlist data from the displayed results
    const primaryPlaylist = document.getElementById('primary-playlist-content').textContent;
    const seoInsights = document.getElementById('playlist-insights-content').textContent;
    const recommendations = document.getElementById('playlist-recommendations-content').textContent;
    
    const exportData = {
        primary_playlist: primaryPlaylist.trim(),
        seo_insights: seoInsights.trim(),
        recommendations: recommendations.trim(),
        exported_at: new Date().toISOString()
    };
    
    return JSON.stringify(exportData, null, 2);
}
// Enhanced Description Features (Added July 14, 2025)
function initializeDescriptionEnhancements() {
    const descriptionContent = document.getElementById('description-content');
    const videoContent = document.getElementById('video-content');
    
    if (descriptionContent) {
        descriptionContent.addEventListener('input', updateDescriptionStats);
        descriptionContent.addEventListener('input', updateLivePreview);
    }
    
    if (videoContent) {
        videoContent.addEventListener('input', updateVideoContentStats);
    }
    
    // Template functionality
    const templateBtn = document.getElementById('template-btn');
    const templateDropdown = document.getElementById('template-dropdown');
    
    if (templateBtn && templateDropdown) {
        templateBtn.addEventListener('click', () => {
            templateDropdown.style.display = templateDropdown.style.display === 'none' ? 'block' : 'none';
        });
    }
    
    document.querySelectorAll('.template-option').forEach(btn => {
        btn.addEventListener('click', function() {
            const template = this.dataset.template;
            applyDescriptionTemplate(template);
            templateDropdown.style.display = 'none';
        });
    });
    
    // Import transcript functionality
    const importTranscriptBtn = document.getElementById('import-transcript-btn');
    if (importTranscriptBtn) {
        importTranscriptBtn.addEventListener('click', importFromTranscript);
    }
    
    // SEO suggestions
    const seoSuggestionsBtn = document.getElementById('seo-suggestions-btn');
    const seoSuggestionsPanel = document.getElementById('seo-suggestions-panel');
    if (seoSuggestionsBtn && seoSuggestionsPanel) {
        seoSuggestionsBtn.addEventListener('click', () => {
            seoSuggestionsPanel.style.display = seoSuggestionsPanel.style.display === 'none' ? 'block' : 'none';
        });
    }
    
    // Live preview
    const previewBtn = document.getElementById('preview-description-btn');
    const previewPanel = document.getElementById('live-preview-panel');
    if (previewBtn && previewPanel) {
        previewBtn.addEventListener('click', () => {
            previewPanel.style.display = previewPanel.style.display === 'none' ? 'block' : 'none';
            if (previewPanel.style.display !== 'none') {
                updateLivePreview();
            }
        });
    }
    
    // Keyword suggestions
    const keywordSuggestBtn = document.getElementById('keyword-suggest-btn');
    const keywordPanel = document.getElementById('keyword-suggestions-panel');
    if (keywordSuggestBtn && keywordPanel) {
        keywordSuggestBtn.addEventListener('click', () => {
            keywordPanel.style.display = keywordPanel.style.display === 'none' ? 'block' : 'none';
            if (keywordPanel.style.display !== 'none') {
                generateKeywordSuggestions();
            }
        });
    }
    
    // SEO Check
    const seoCheckBtn = document.getElementById('seo-check-btn');
    if (seoCheckBtn) {
        seoCheckBtn.addEventListener('click', performSEOCheck);
    }
    
    // Reset options
    const resetBtn = document.getElementById('reset-options');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetEnhancementOptions);
    }
}

function updateDescriptionStats() {
    const descriptionContent = document.getElementById('description-content');
    const charCount = document.getElementById('char-count');
    const wordCount = document.getElementById('word-count');
    const readabilityScore = document.getElementById('readability-score');
    
    if (descriptionContent && charCount && wordCount) {
        const content = descriptionContent.value;
        const chars = content.length;
        const words = content.trim() ? content.trim().split(/\s+/).length : 0;
        
        charCount.textContent = chars;
        wordCount.textContent = words;
        
        if (chars > 4500) {
            charCount.className = 'text-danger fw-bold';
        } else if (chars > 4000) {
            charCount.className = 'text-warning fw-bold';
        } else {
            charCount.className = '';
        }
        
        if (readabilityScore) {
            const score = calculateReadabilityScore(content);
            readabilityScore.textContent = `Readability: ${score}`;
            readabilityScore.className = `badge ${getReadabilityClass(score)}`;
        }
    }
}

function updateLivePreview() {
    const descriptionContent = document.getElementById('description-content');
    const previewContent = document.getElementById('preview-description-content');
    const previewCharCount = document.getElementById('preview-char-count');
    const previewWordCount = document.getElementById('preview-word-count');
    const previewSeoScore = document.getElementById('preview-seo-score');
    
    if (descriptionContent && previewContent) {
        const content = descriptionContent.value;
        const chars = content.length;
        const words = content.trim() ? content.trim().split(/\s+/).length : 0;
        
        if (content.trim()) {
            previewContent.innerHTML = content.replace(/\n/g, '<br>');
            previewContent.className = '';
        } else {
            previewContent.innerHTML = '<em>Type in the description field above to see live preview...</em>';
            previewContent.className = 'text-muted';
        }
        
        if (previewCharCount) previewCharCount.textContent = `${chars}/5000`;
        if (previewWordCount) previewWordCount.textContent = `${words} words`;
        
        if (previewSeoScore && content.trim()) {
            const seoScore = calculateSEOScore(content);
            previewSeoScore.textContent = `SEO: ${seoScore}%`;
            previewSeoScore.className = `badge ${getSEOScoreClass(seoScore)}`;
        } else if (previewSeoScore) {
            previewSeoScore.textContent = 'SEO: Not analyzed';
            previewSeoScore.className = 'badge bg-secondary';
        }
    }
}

function applyDescriptionTemplate(templateType) {
    const descriptionContent = document.getElementById('description-content');
    if (!descriptionContent) return;
    
    const templates = {
        tutorial: `📚 In this tutorial, you'll learn [MAIN TOPIC]

🎯 What you'll discover:
• [Key point 1]
• [Key point 2] 
• [Key point 3]

⏱️ Timestamps:
00:00 - Introduction
[XX:XX] - [Chapter 1]
[XX:XX] - [Chapter 2]

🔗 Resources mentioned:
• [Resource 1]: [Link]

💡 Don't forget to subscribe for more tutorials!

#Tutorial #HowTo #Learning`,

        review: `⭐ Honest review of [PRODUCT NAME]

📋 What I tested:
✅ [Feature 1] - Rating: X/10
✅ [Feature 2] - Rating: X/10

💰 Price: $[PRICE]
🏆 Overall rating: X/10

👍 Pros: • [Pro 1] • [Pro 2]
👎 Cons: • [Con 1] • [Con 2]

🛒 Where to buy: [Link]

#Review #ProductReview #Honest`,

        gaming: `🎮 [GAME NAME] - [VIDEO DESCRIPTION]

🏆 Highlights:
• [Achievement 1]
• [Achievement 2]

⏱️ Timestamps:
00:00 - Intro
[XX:XX] - [Gameplay moment]

Like and subscribe for more gaming content!

#Gaming #[GameName] #Gameplay`,

        educational: `🎓 [TOPIC] Explained Simply

📚 What we cover:
1. [Concept 1] - The basics
2. [Concept 2] - Advanced techniques
3. [Concept 3] - Applications

📖 Additional resources:
• [Resource 1]: [Link]

Subscribe for more educational content!

#Education #Learning #[Topic]`,

        business: `💼 [BUSINESS TOPIC] - [DESCRIPTION]

📈 What you'll learn:
• [Business concept 1]
• [Business concept 2]

🎯 Key strategies:
1. [Strategy 1]
2. [Strategy 2]

🔗 Tools mentioned:
• [Tool 1]: [Link]

Share your business wins in the comments!

#Business #Entrepreneur #Success`,

        tech: `💻 [TECHNOLOGY/CODING TOPIC]

🚀 What we build:
• [Feature 1]
• [Feature 2]

⚙️ Technologies:
• [Tech 1] • [Tech 2]

📝 Code: [GitHub link]

🤝 Connect: GitHub: [Link]

#Programming #Tech #Development`,

        vlog: `✨ [VLOG TITLE]

🌟 Today's adventure:
• [Activity 1]
• [Activity 2]

📸 Favorite moments:
• [Moment 1] • [Moment 2]

💕 Thanks for following my journey!

Like and let me know what you want to see next!

#Vlog #Life #Adventure`,

        entertainment: `🎬 [ENTERTAINMENT CONTENT]

😂 What's in this video:
• [Funny element 1]
• [Funny element 2]

⭐ Best moments:
• [Timestamp] - [Description]

Share with friends who need a laugh!

#Entertainment #Funny #Content`,

        fitness: `💪 [WORKOUT/FITNESS TOPIC]

🏋️ Today's workout:
• [Exercise 1] - [Sets/reps]
• [Exercise 2] - [Sets/reps]

⏱️ Duration: [X] minutes
🎯 Target: [Muscle group]

💪 Share your results in the comments!

#Fitness #Workout #Health`
    };
    
    if (templates[templateType]) {
        descriptionContent.value = templates[templateType];
        updateDescriptionStats();
        updateLivePreview();
        showToast(`Applied ${templateType} template successfully!`, 'success');
    }
}

function importFromTranscript() {
    const transcriptionText = document.getElementById('transcription');
    const videoContent = document.getElementById('video-content');
    
    if (transcriptionText && videoContent && transcriptionText.textContent.trim()) {
        videoContent.value = transcriptionText.textContent.trim();
        updateVideoContentStats();
        showToast('Transcript imported successfully!', 'success');
    } else {
        showToast('No transcription available. Please transcribe audio first.', 'warning');
    }
}

function generateKeywordSuggestions() {
    const content = document.getElementById('description-content').value + ' ' + document.getElementById('video-content').value;
    
    if (!content.trim()) {
        showToast('Please enter content first to generate suggestions.', 'warning');
        return;
    }
    
    const keywords = extractKeywordsFromContent(content);
    const tags = generateTagsFromKeywords(keywords);
    
    const trendingKeywordsDiv = document.getElementById('trending-keywords');
    const relatedTagsDiv = document.getElementById('related-tags');
    const seoRecommendationsDiv = document.getElementById('seo-recommendations');
    
    if (trendingKeywordsDiv) {
        trendingKeywordsDiv.innerHTML = keywords.map(keyword => 
            `<span class="badge bg-primary me-1 mb-1" style="cursor: pointer;" onclick="addToDescription('${keyword}')">${keyword}</span>`
        ).join('');
    }
    
    if (relatedTagsDiv) {
        relatedTagsDiv.innerHTML = tags.map(tag => 
            `<span class="badge bg-secondary me-1 mb-1" style="cursor: pointer;" onclick="addToDescription('#${tag}')">#${tag}</span>`
        ).join('');
    }
    
    if (seoRecommendationsDiv) {
        const recommendations = generateSEORecommendations(content);
        seoRecommendationsDiv.innerHTML = recommendations.map(rec => `<li>${rec}</li>`).join('');
    }
}

function performSEOCheck() {
    const content = document.getElementById('description-content').value;
    
    if (!content.trim()) {
        showToast('Please enter a description first.', 'warning');
        return;
    }
    
    const seoScore = calculateSEOScore(content);
    const recommendations = generateSEORecommendations(content);
    
    showToast(`SEO Score: ${seoScore}%. Check recommendations for improvements.`, 'info');
    
    const recommendationText = recommendations.join('\n• ');
    alert(`SEO Analysis Results:\n\nScore: ${seoScore}%\n\nRecommendations:\n• ${recommendationText}`);
}

function resetEnhancementOptions() {
    document.getElementById('target-audience').value = 'general';
    document.getElementById('video-category').value = 'general';
    document.getElementById('description-length').value = 'medium';
    document.getElementById('writing-tone').value = 'friendly';
    
    const checkboxes = ['include-seo', 'include-hashtags', 'include-cta', 'include-social'];
    checkboxes.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) checkbox.checked = true;
    });
    
    const advancedCheckboxes = ['include-timestamps', 'include-chapters', 'include-resources', 'include-emojis'];
    advancedCheckboxes.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) checkbox.checked = false;
    });
    
    showToast('Options reset to defaults.', 'success');
}

// Helper functions
function updateVideoContentStats() {}

function calculateReadabilityScore(text) {
    if (!text.trim()) return 'Good';
    
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const words = text.trim().split(/\s+/);
    const avgWordsPerSentence = words.length / sentences.length;
    
    if (avgWordsPerSentence < 15) return 'Excellent';
    if (avgWordsPerSentence < 20) return 'Good';
    if (avgWordsPerSentence < 25) return 'Fair';
    return 'Complex';
}

function getReadabilityClass(score) {
    const classes = {'Excellent': 'bg-success', 'Good': 'bg-info', 'Fair': 'bg-warning', 'Complex': 'bg-danger'};
    return classes[score] || 'bg-secondary';
}

function calculateSEOScore(content) {
    let score = 0;
    
    const words = content.trim().split(/\s+/).length;
    if (words >= 200 && words <= 300) score += 25;
    else if (words >= 150) score += 15;
    
    const hashtags = (content.match(/#\w+/g) || []).length;
    if (hashtags >= 3 && hashtags <= 5) score += 20;
    else if (hashtags > 0) score += 10;
    
    const ctaWords = ['subscribe', 'like', 'comment', 'share', 'click', 'watch', 'follow'];
    const hasCTA = ctaWords.some(word => content.toLowerCase().includes(word));
    if (hasCTA) score += 20;
    
    const hasTimestamps = /\d{1,2}:\d{2}/.test(content);
    if (hasTimestamps) score += 15;
    
    const hasLinks = /https?:\/\//.test(content);
    if (hasLinks) score += 10;
    
    const emojiCount = (content.match(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F700}-\u{1F77F}]|[\u{1F780}-\u{1F7FF}]|[\u{1F800}-\u{1F8FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu) || []).length;
    if (emojiCount >= 3 && emojiCount <= 10) score += 10;
    
    return Math.min(score, 100);
}

function getSEOScoreClass(score) {
    if (score >= 80) return 'bg-success';
    if (score >= 60) return 'bg-warning';
    if (score >= 40) return 'bg-orange';
    return 'bg-danger';
}

function extractKeywordsFromContent(content) {
    const words = content.toLowerCase().replace(/[^\w\s]/g, '').split(/\s+/);
    const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'this', 'that', 'these', 'those']);
    
    const filtered = words.filter(word => word.length > 3 && !stopWords.has(word));
    const frequency = {};
    
    filtered.forEach(word => {
        frequency[word] = (frequency[word] || 0) + 1;
    });
    
    return Object.entries(frequency)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 8)
        .map(([word]) => word);
}

function generateTagsFromKeywords(keywords) {
    const tags = [];
    keywords.forEach(keyword => {
        tags.push(keyword);
        if (keyword.includes('ing')) {
            tags.push(keyword.replace('ing', ''));
        }
    });
    return [...new Set(tags)].slice(0, 10);
}

function generateSEORecommendations(content) {
    const recommendations = [];
    const words = content.trim().split(/\s+/).length;
    const hashtags = (content.match(/#\w+/g) || []).length;
    
    if (words < 150) recommendations.push('Add more detail to reach 150-300 words for better SEO');
    if (words > 400) recommendations.push('Consider shortening to under 400 words for better readability');
    if (hashtags < 3) recommendations.push('Add 3-5 relevant hashtags to improve discoverability');
    if (hashtags > 5) recommendations.push('Reduce hashtags to 3-5 to avoid spam appearance');
    if (!content.toLowerCase().includes('subscribe')) recommendations.push('Include a call-to-action like "subscribe"');
    if (!/\d{1,2}:\d{2}/.test(content)) recommendations.push('Add timestamps for longer videos');
    
    return recommendations.length > 0 ? recommendations : ['Your description looks good!'];
}

function addToDescription(text) {
    const descriptionContent = document.getElementById('description-content');
    if (descriptionContent) {
        const currentValue = descriptionContent.value;
        const newValue = currentValue + (currentValue ? ' ' : '') + text;
        descriptionContent.value = newValue;
        updateDescriptionStats();
        updateLivePreview();
        showToast(`Added "${text}" to description`, 'success');
    }
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}
