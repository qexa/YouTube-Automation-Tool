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
        const formData = new FormData();
        formData.append('audio', document.getElementById('audio-file').files[0]);
        const response = await fetch('/transcribe', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        document.getElementById('transcription').textContent = data.transcription;
        document.getElementById('summary').textContent = data.summary;
    });

    descriptionForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const content = document.getElementById('description-content').value;
        const videoContent = document.getElementById('video-content').value;
        const response = await fetch('/enhance_description', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({content: content, video_content: videoContent})
        });
        const data = await response.json();
        document.getElementById('enhanced-description').textContent = data.description;
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