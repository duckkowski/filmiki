import os
import yt_dlp
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>TERMINAL://DUAL_STREAM_PLAYER</title>
    <style>
        body { background: #050505; color: #00ff41; font-family: monospace; text-align: center; padding: 20px; }
        .terminal { border: 1px solid #00ff41; padding: 20px; background: #000; display: inline-block; width: 90%; max-width: 800px; }
        input { background: #000; border: 1px solid #00ff41; color: #00ff41; padding: 10px; width: 80%; margin-bottom: 10px; outline: none; }
        button { background: #00ff41; color: #000; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; }
        .player-container { margin-top: 20px; border: 1px solid #333; position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; }
        video { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #000; }
        .links { margin-top: 15px; font-size: 12px; }
        a { color: #00ff41; text-decoration: none; border: 1px solid #00ff41; padding: 5px; margin: 5px; display: inline-block; }
    </style>
</head>
<body>
    <div class="terminal">
        <h2>> ROOT@PLAYER: DUAL_CHANNEL_SYNC</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="PASTE_URL (CDA/YT)..." required>
            <button type="submit">SYNC & PLAY</button>
        </form>

        {% if v_url and a_url %}
            <div class="player-container">
                <video id="videoPlayer" controls>
                    <source src="{{ v_url }}" type="video/mp4">
                </video>
                <audio id="audioPlayer">
                    <source src="{{ a_url }}" type="audio/mp4">
                </audio>
            </div>

            <div class="links">
                <p>[+] SYNC_STATUS: STREAMS_LOCATED</p>
                <a href="{{ v_url }}" target="_blank">LINK_VIDEO_ONLY</a>
                <a href="{{ a_url }}" target="_blank">LINK_AUDIO_ONLY</a>
            </div>

            <script>
                const video = document.getElementById('videoPlayer');
                const audio = document.getElementById('audioPlayer');

                // Prosta synchronizacja: gdy startuje video, startuje audio
                video.onplay = () => audio.play();
                video.onpause = () => audio.pause();
                video.onseeking = () => audio.currentTime = video.currentTime;
                video.onseeked = () => audio.currentTime = video.currentTime;
                video.onvolumechange = () => audio.volume = video.volume;
            </script>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    v_url = None
    a_url = None
    if request.method == 'POST':
        video_url = request.form.get('url')
        
        # Prosimy o najlepsze wideo i najlepsze audio OSOBNO
        ydl_opts_v = {'format': 'bestvideo', 'quiet': True}
        ydl_opts_a = {'format': 'bestaudio', 'quiet': True}
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts_v) as ydl:
                info_v = ydl.extract_info(video_url, download=False)
                v_url = info_v.get('url')
            
            with yt_dlp.YoutubeDL(ydl_opts_a) as ydl:
                info_a = ydl.extract_info(video_url, download=False)
                a_url = info_a.get('url')
        except Exception as e:
            return f"SYSTEM_ERROR: {str(e)}"
            
    return render_template_string(HTML_LAYOUT, v_url=v_url, a_url=a_url)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
