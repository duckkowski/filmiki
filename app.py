import os
import yt_dlp
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>TERMINAL://DUAL_SYNC_V12</title>
    <style>
        body { background: #050505; color: #00ff41; font-family: monospace; text-align: center; padding: 20px; }
        .terminal { border: 1px solid #00ff41; padding: 20px; background: #000; display: inline-block; width: 95%; max-width: 800px; box-shadow: 0 0 20px #00ff4144; }
        input { background: #000; border: 1px solid #00ff41; color: #00ff41; padding: 12px; width: 80%; margin-bottom: 10px; outline: none; }
        button { background: #00ff41; color: #000; border: none; padding: 12px 25px; cursor: pointer; font-weight: bold; text-transform: uppercase; }
        .player-box { margin-top: 20px; border: 1px solid #333; background: #000; position: relative; padding-bottom: 56.25%; height: 0; }
        video { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
        .controls-info { margin-top: 15px; font-size: 11px; color: #888; border: 1px dashed #333; padding: 10px; }
        .link-row { margin-top: 15px; }
        .btn-raw { color: #00ff41; text-decoration: none; border: 1px solid #00ff41; padding: 5px 10px; margin: 5px; display: inline-block; font-size: 12px; }
        .btn-raw:hover { background: #00ff41; color: #000; }
    </style>
</head>
<body>
    <div class="terminal">
        <h2>> ROOT@CORE: V12.0_DUAL_SYNC</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="ENTER_SOURCE_URL..." required>
            <button type="submit">EXTRACT_&_SYNC</button>
        </form>

        {% if v_url and a_url %}
            <div class="player-box">
                <video id="vPlayer" controls>
                    <source src="{{ v_url }}" type="video/mp4">
                </video>
                <audio id="aPlayer">
                    <source src="{{ a_url }}" type="audio/mp4">
                </audio>
            </div>

            <div class="controls-info">
                <p>[+] SYSTEM_STATUS: DUAL_STREAM_ESTABLISHED</p>
                <p>Synchronizacja JS aktywna: Play/Pause/Seek działają na obu ścieżkach jednocześnie.</p>
            </div>

            <div class="link-row">
                <a href="{{ v_url }}" target="_blank" class="btn-raw">DOWNLOAD_VIDEO_RAW</a>
                <a href="{{ a_url }}" target="_blank" class="btn-raw">DOWNLOAD_AUDIO_RAW</a>
            </div>

            <script>
                const v = document.getElementById('vPlayer');
                const a = document.getElementById('aPlayer');

                v.onplay = () => a.play();
                v.onpause = () => a.pause();
                v.onseeking = () => a.currentTime = v.currentTime;
                v.onseeked = () => a.currentTime = v.currentTime;
                v.onvolumechange = () => a.volume = v.volume;
                
                // Zapobieganie desynchronizacji przy lagach
                setInterval(() => {
                    if (!v.paused && Math.abs(v.currentTime - a.currentTime) > 0.3) {
                        a.currentTime = v.currentTime;
                    }
                }, 1000);
            </script>
        {% elif error %}
            <p style="color:red; margin-top:20px;">[-] {{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    v_url = None
    a_url = None
    error = None
    
    if request.method == 'POST':
        url = request.form.get('url')
        
        # Osobne opcje dla wideo i audio, aby wymusic linki DASH/MP4
        ydl_v = {'format': 'bestvideo', 'quiet': True, 'nocheckcertificate': True}
        ydl_a = {'format': 'bestaudio', 'quiet': True, 'nocheckcertificate': True}
        
        try:
            with yt_dlp.YoutubeDL(ydl_v) as ydl:
                info_v = ydl.extract_info(url, download=False)
                v_url = info_v.get('url')
            
            with yt_dlp.YoutubeDL(ydl_a) as ydl:
                info_a = ydl.extract_info(url, download=False)
                a_url = info_a.get('url')
                
            if not v_url or not a_url:
                error = "COULD_NOT_RESOLVE_DUAL_STREAMS"
        except Exception as e:
            error = f"EXTRACTION_FAILED: {str(e)[:100]}"
            
    return render_template_string(HTML_LAYOUT, v_url=v_url, a_url=a_url, error=error)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
