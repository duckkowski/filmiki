import os
import yt_dlp
import subprocess
from flask import Flask, request, render_template_string, Response

app = Flask(__name__)

# Stylizacja na terminal hakerski
HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>TERMINAL://MUXER_V15</title>
    <style>
        :root {
            --glow-color: #00ff41;
            --bg-color: #050505;
        }
        body { 
            background: var(--bg-color); 
            color: var(--glow-color); 
            font-family: 'Courier New', Courier, monospace; 
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
            text-shadow: 0 0 5px var(--glow-color);
        }
        /* Efekt linii skanujących CRT */
        body::before {
            content: " ";
            display: block;
            position: absolute;
            top: 0; left: 0; bottom: 0; right: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
                        linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
            z-index: 2;
            background-size: 100% 2px, 3px 100%;
            pointer-events: none;
        }
        .terminal {
            border: 1px solid var(--glow-color);
            padding: 30px;
            background: rgba(0, 20, 0, 0.9);
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.2);
            width: 80%;
            max-width: 700px;
            position: relative;
            z-index: 1;
        }
        h2 { border-bottom: 1px solid var(--glow-color); padding-bottom: 10px; font-size: 1.2em; }
        input { 
            background: transparent; 
            border: none; 
            border-bottom: 1px solid var(--glow-color); 
            color: #fff; 
            padding: 10px; 
            width: 70%; 
            outline: none;
            font-family: inherit;
        }
        button {
            background: var(--glow-color);
            color: #000;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-weight: bold;
            font-family: inherit;
            transition: 0.3s;
        }
        button:hover {
            background: #fff;
            box-shadow: 0 0 15px #fff;
        }
        .output {
            margin-top: 30px;
            text-align: left;
            border-top: 1px dashed var(--glow-color);
            padding-top: 20px;
        }
        code {
            display: block;
            background: #000;
            padding: 15px;
            color: #00ff41;
            word-break: break-all;
            border: 1px solid #222;
        }
        .cursor {
            display: inline-block;
            width: 10px;
            height: 1.2em;
            background: var(--glow-color);
            vertical-align: middle;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }
    </style>
</head>
<body>
    <div class="terminal">
        <h2>[SYSTEM] CORE_MUXER_V15://FINAL</h2>
        <p>> PODAJ LINK DO STRUMIENIA:<span class="cursor"></span></p>
        <form method="POST">
            <input type="text" name="url" placeholder="https://cda.pl/video/..." required autocomplete="off">
            <button type="submit">EXECUTE</button>
        </form>

        {% if link %}
        <div class="output">
            <p>[SUCCESS] GENEROWANIE LINKU ZAKOŃCZONE...</p>
            <p>> TARGET_URL:</p>
            <code>{{ link }}</code>
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
        u = request.form.get('url')
        link = f"https://{request.host}/merged.mp4?url={u}"
    return render_template_string(HTML_LAYOUT, link=link)

@app.route('/merged.mp4')
def merged_stream():
    video_url = request.args.get('url')
    
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            v_url = None
            a_url = None
            
            for f in info['formats']:
                if f.get('vcodec') != 'none' and f.get('acodec') == 'none':
                    v_url = f['url']
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    a_url = f['url']

        if not v_url or not a_url:
            return Response("ERROR: Stream separation failed", status=400)

        cmd = [
            'ffmpeg',
            '-i', v_url,
            '-i', a_url,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-f', 'mp4',
            '-movflags', 'frag_keyframe+empty_moov+default_base_moof',
            'pipe:1'
        ]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        def generate():
            try:
                while True:
                    data = process.stdout.read(1024*1024)
                    if not data:
                        break
                    yield data
            finally:
                process.kill()

        return Response(generate(), content_type="video/mp4")

    except Exception as e:
        return f"[FATAL_ERROR]: {str(e)}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
