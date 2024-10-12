document.addEventListener('DOMContentLoaded', function() {
    const titleForm = document.getElementById('title-form');
    const transcriptionForm = document.getElementById('transcription-form');
    const descriptionForm = document.getElementById('description-form');
    const playlistForm = document.getElementById('playlist-form');
    const numberForm = document.getElementById('number-form');

    titleForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const content = document.getElementById('title-content').value;
        const response = await fetch('/generate_title', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({content: content})
        });
        const data = await response.json();
        document.getElementById('generated-title').textContent = data.title;
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
        const response = await fetch('/enhance_description', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({content: content})
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
        document.getElementById('assigned-playlist').textContent = data.playlist;
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
    });
});
