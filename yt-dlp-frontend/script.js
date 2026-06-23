// ⚠️ YAHAN APNE RENDER BACKEND KA URL DALEIN
const API_URL = "https://your-backend-app.onrender.com/get_download_link";

async function fetchVideo() {
    const url = document.getElementById('videoUrl').value.trim();
    const resultDiv = document.getElementById('result');
    const loader = document.getElementById('loader');
    
    if (!url) {
        resultDiv.innerHTML = `<div class="error">❌ Please enter a URL!</div>`;
        return;
    }

    loader.style.display = "block";
    resultDiv.innerHTML = "";

    try {
        const response = await fetch(`${API_URL}?url=${encodeURIComponent(url)}`);
        const data = await response.json();

        if (data.status === "success") {
            resultDiv.innerHTML = `
                <div class="video-card">
                    ${data.thumbnail ? `<img src="${data.thumbnail}" alt="thumbnail">` : ''}
                    <h3>${data.title}</h3>
                    <a href="${data.download_url}" class="download-btn" target="_blank">
                        ⬇️ Download Video
                    </a>
                </div>
            `;
        } else {
            resultDiv.innerHTML = `<div class="error">❌ Error: ${data.detail}</div>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<div class="error">❌ Backend se connect nahi ho paya. URL check karein.</div>`;
    } finally {
        loader.style.display = "none";
    }
}

// Enter key se bhi submit ho
document.getElementById('videoUrl').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') fetchVideo();
});
