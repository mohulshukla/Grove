let currentSimilarVideos = [];
let isLoadingSimilarVideos = false;  // Prevents multiple simultaneous requests
let currentVideoId = document.getElementById("videoSource").src.split("/").pop();  // Track the currently active video ID

const videoPlayer = document.getElementById('videoPlayer');
const videoSource = document.getElementById('videoSource');

// Helper function to load and play a video
function loadVideo(videoId) {
    currentVideoId = videoId;  // Update the current video ID
    videoSource.src = `/video/${videoId}`;
    videoPlayer.load();
    videoPlayer.play();
}

// Prefetch similar videos based on the current video ID
function loadMoreSimilarVideos() {
    if (isLoadingSimilarVideos) return;
    isLoadingSimilarVideos = true;
    
    fetch('/get_similar_videos', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({video_id: currentVideoId})
    })
    .then(response => response.json())
    .then(data => {
        currentSimilarVideos = data;  // Replace with new similar videos for the current video ID
        isLoadingSimilarVideos = false;
    })
    .catch(error => {
        console.error("Error fetching similar videos:", error);
        isLoadingSimilarVideos = false;
    });
}

// Fetch and play a random video when Left or Right button is clicked
function loadRandomVideo() {
    fetch('/get_random_videos', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({video_id: currentVideoId})
    })
    .then(response => response.json())
    .then(data => {
        const randomVideo = data[0];  // Select the first random video from the response
        loadVideo(randomVideo);  // Play the random video
        
        // Clear and reload similar videos based on the new random video
        currentSimilarVideos = [];  // Clear the old similar videos
        loadMoreSimilarVideos();  // Prefetch similar videos for the new random video
    });
}

// Button event listeners
document.getElementById('downBtn').addEventListener('click', () => {
    if (currentSimilarVideos.length > 0) {
        loadVideo(currentSimilarVideos.shift());
        
        if (currentSimilarVideos.length < 2) {
            loadMoreSimilarVideos();
        }
    } else {
        loadMoreSimilarVideos();
    }
});

document.getElementById('leftBtn').addEventListener('click', () => {
    loadRandomVideo();  // Load a new random video on each Left button click
});

document.getElementById('rightBtn').addEventListener('click', () => {
    loadRandomVideo();  // Load a different random video on each Right button click
});

// Initial prefetch of similar videos for the first Down button click
loadMoreSimilarVideos();