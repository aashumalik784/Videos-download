from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import yt_dlp
import uvicorn
from typing import Optional

app = FastAPI(title="Universal Video Downloader API")

# CORS allow karein
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>🎬 Universal Video Downloader API ✅</h1>
    <p>Support: YouTube, Instagram, Facebook, Twitter, TikTok, aur 1000+ sites</p>
    <p>Use: <code>/get_download_link?url=VIDEO_URL</code></p>
    """

@app.get("/get_download_link")
def get_download_link(url: str, quality: Optional[str] = "best"):
    """
    Universal video downloader - sabhi platforms support
    quality: best, hd, sd, audio_only
    """
    
    # Platform detection
    platform = detect_platform(url)
    
    # Quality ke according format selector
    format_selectors = {
        "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "hd": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
        "sd": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
        "audio_only": "bestaudio[ext=m4a]/bestaudio/best"
    }
    
    format_selector = format_selectors.get(quality, format_selectors["best"])
    
    # Platform-specific options
    ydl_opts = {
        'format': format_selector,
        'quiet': True,        'no_warnings': True,
        'noplaylist': True,
        'extract_flat': False,
        'merge_output_format': 'mp4',
        'socket_timeout': 30,
        'retries': 3,
        'fragment_retries': 3,
        'http_chunk_size': 10485760,  # 10MB
    }
    
    # Instagram, Facebook ke liye extra options
    if platform in ['instagram', 'facebook']:
        ydl_opts.update({
            'extractor_args': {
                'facebook': {'prefer_manifest': ['true']},
                'instagram': {'prefer_manifest': ['true']}
            }
        })
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract download URL
            download_url = extract_download_url(info)
            
            if not download_url:
                raise Exception("Download URL not found")
            
            return {
                "status": "success",
                "platform": platform,
                "title": info.get('title', 'Video'),
                "thumbnail": info.get('thumbnail', ''),
                "download_url": download_url,
                "duration": info.get('duration', 0),
                "uploader": info.get('uploader', 'Unknown'),
                "view_count": info.get('view_count', 0),
                "like_count": info.get('like_count', 0),
                "description": info.get('description', '')[:200] if info.get('description') else '',
                "formats_available": len(info.get('formats', []))
            }
            
    except Exception as e:
        # Fallback attempt with different options
        try:
            fallback_opts = {
                'format': 'best/bestvideo+bestaudio',
                'quiet': True,
                'no_warnings': True,                'noplaylist': True,
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info:
                    download_url = extract_download_url(info)
                    
                    return {
                        "status": "success",
                        "platform": platform,
                        "title": info.get('title', 'Video'),
                        "thumbnail": info.get('thumbnail', ''),
                        "download_url": download_url or info.get('webpage_url', url),
                        "duration": info.get('duration', 0),
                        "uploader": info.get('uploader', 'Unknown'),
                        "note": "Fallback method used"
                    }
        except Exception as e2:
            raise HTTPException(
                status_code=400, 
                detail=f"Download failed: {str(e2)}. Try a different video or platform."
            )

def detect_platform(url: str) -> str:
    """Detect video platform from URL"""
    url_lower = url.lower()
    
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'instagram.com' in url_lower:
        return 'instagram'
    elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
        return 'facebook'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'twitter'
    elif 'tiktok.com' in url_lower:
        return 'tiktok'
    elif 'vimeo.com' in url_lower:
        return 'vimeo'
    elif 'dailymotion.com' in url_lower:
        return 'dailymotion'
    elif 'reddit.com' in url_lower:
        return 'reddit'
    elif 'twitch.tv' in url_lower:
        return 'twitch'
    else:
        return 'unknown'
def extract_download_url(info: dict) -> str:
    """Extract best download URL from video info"""
    
    # Direct URL
    if 'url' in info:
        return info['url']
    
    # Try formats
    if 'formats' in info and info['formats']:
        # Try to find MP4 format
        for fmt in reversed(info['formats']):
            if fmt.get('ext') == 'mp4' and fmt.get('url'):
                return fmt['url']
        
        # Return last format (usually best)
        return info['formats'][-1].get('url', '')
    
    # Try requested_formats (for merged video+audio)
    if 'requested_formats' in info and info['requested_formats']:
        video_url = info['requested_formats'][0].get('url', '')
        if video_url:
            return video_url
    
    # Fallback to webpage_url
    return info.get('webpage_url', '')

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Universal Video Downloader",
        "version": "2.0",
        "supported_platforms": [
            "YouTube", "Instagram", "Facebook", "Twitter", 
            "TikTok", "Vimeo", "Dailymotion", "Reddit", "Twitch",
            "and 1000+ more sites"
        ]
    }

# Hugging Face/Render ke liye
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
