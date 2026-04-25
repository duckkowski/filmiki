import os
import yt_dlp
import subprocess
from flask import Flask, request, render_template_string, Response

app = Flask(__name__)

HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>SCALACZ_V15://FINAL</title>
    <style>
        body { background: #000; color: #ff0000; font-family: monospace; text-align: center; padding: 50px; }
        .box { border: 2px solid #ff0000; padding: 20px; display: inline-block; background: #111; }
        input { background: #000; border: 1px solid #ff0000; color: #fff; padding: 10px; width: 300px; }
        code { display: block; background: #222; padding: 10px; margin-top: 10px; color: #00ff00; word-break: break-all; }
    </style>
</head>
<body>
    <div class="box">
        <h2>> CORE_MUXER_V15 (FFMPEG_LIVE)</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="LINK CDA..." required>
            <button type="submit">GENERUJ SCALONY LINK</button>
        </form>
        {% if link %}
            <p>LINK DLA WATERFRAMES:</p>
            <code>{{ link }}</code>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    link = None
    if request.method == 'POST':
        u = request.form.get('url')
        link = f"https://{request.host}/merged.mp4?url={u}"
    return render_template_string(HTML_LAYOUT, link=link)

@app.route('/merged.mp4')
def merged_stream():
    video_url = request.args.get('url')
    
    try:
        # 1. Pobieramy linki do czystego wideo i czystego audio
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            v_url = None
            a_url = None
            
            # Szukamy najlepszego wideo i audio
            for f in info['formats']:
                if f.get('vcodec') != 'none' and f.get('acodec') == 'none':
                    v_url = f['url']
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    a_url = f['url']

        # 2. Jeśli nie znaleźliśmy rozdzielonych, bierzemy co jest
        if not v_url or not a_url:
            return Response("Błąd: Nie można rozdzielić strumieni", status=400)

        # 3. Uruchamiamy FFmpeg, który łączy oba linki i wysyła wynik do "stdout"
        # Używamy formatu 'matroska' lub 'mp4' z flagą frag_keyframe dla streamingu
        cmd = [
            'ffmpeg',
            '-i', v_url,
            '-i', a_url,
            '-c:v', 'copy',  # Nie reenkodujemy wideo (oszczędza CPU)
            '-c:a', 'aac',   # Enkodujemy audio do AAC (bezpieczne dla MC)
            '-f', 'mp4',
            '-movflags', 'frag_keyframe+empty_moov+default_base_moof', # Ważne dla streamingu w locie
            'pipe:1'
        ]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        def generate():
            try:
                while True:
                    data = process.stdout.read(1024*1024) # 1MB chunks
                    if not data:
                        break
                    yield data
            finally:
                process.kill()

        return Response(generate(), content_type="video/mp4")

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
