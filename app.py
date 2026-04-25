import os
import yt_dlp
from flask import Flask, request, render_template_string, Response, stream_with_context
import requests

app = Flask(__name__)

HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>TERMINAL://LIVE_STREAM_SYNC</title>
    <style>
        body { background: #050505; color: #00ff41; font-family: monospace; text-align: center; padding-top: 50px; }
        .terminal { border: 1px solid #00ff41; padding: 20px; background: #000; display: inline-block; width: 90%; max-width: 600px; }
        input { background: #000; border: 1px solid #00ff41; color: #00ff41; padding: 10px; width: 80%; margin-bottom: 20px; outline: none; }
        button { background: #00ff41; color: #000; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; }
        .info { margin-top: 20px; color: #ff3333; font-size: 12px; }
    </style>
</head>
<body>
    <div class="terminal">
        <h2>> ROOT@CORE: LIVE_PROXY_V8</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="ENTERURL_FOR_SYNC_LINK..." required>
            <button type="submit">GENERATE_SINGLE_SYNC_LINK</button>
        </form>
        {% if link %}
            <div style="margin-top:20px;">
                <p>[+] SYNC_LINK_GENERATED:</p>
                <a href="{{ link }}" style="color:#000; background:#00ff41; padding:10px; text-decoration:none; font-weight:bold;">POBIERZ FILMIK Z DŹWIĘKIEM</a>
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    link = None
    if request.method == 'POST':
        video_url = request.form.get('url')
        # Link do naszej wewnętrznej trasy streamującej
        link = f"/stream?url={video_url}"
    return render_template_string(HTML_LAYOUT, link=link)

@app.route('/stream')
def stream_video():
    video_url = request.args.get('url')
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best', # Próbujemy wymusić gotowy plik z dźwiękiem
        'quiet': True,
        'user_agent': 'Mozilla/5.0'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        real_url = info.get('url')

    # Funkcja generująca dane kawałek po kawałku (Proxy)
    def generate():
        r = requests.get(real_url, stream=True)
        for chunk in r.iter_content(chunk_size=1024*1024): # 1MB chunks
            yield chunk

    return Response(stream_with_context(generate()), content_type="video/mp4")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
