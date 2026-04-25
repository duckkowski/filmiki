import os
import yt_dlp
import requests
from flask import Flask, request, render_template_string, Response, stream_with_context

app = Flask(__name__)

HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>TERMINAL://MINECRAFT_LINKER</title>
    <style>
        body { background: #0a0a0a; color: #00ff41; font-family: 'Courier New', monospace; text-align: center; padding: 50px; }
        .terminal { border: 2px solid #00ff41; padding: 30px; background: #000; display: inline-block; width: 90%; max-width: 650px; box-shadow: 0 0 20px #00ff4133; }
        input { background: #000; border: 1px solid #00ff41; color: #00ff41; padding: 12px; width: 85%; margin-bottom: 20px; outline: none; }
        .success-box { border: 1px dashed #00ff41; padding: 15px; margin-top: 20px; background: #001100; }
        code { background: #111; padding: 5px; color: #fff; display: block; margin-top: 10px; word-break: break-all; }
        button { background: #00ff41; color: #000; border: none; padding: 10px 20px; font-weight: bold; cursor: pointer; text-transform: uppercase; }
    </style>
</head>
<body>
    <div class="terminal">
        <h2>> GENERATOR_LINKOW_MC_V14</h2>
        <p style="font-size: 12px;">Wklej link, aby otrzymać adres do WaterFrames</p>
        <form method="POST">
            <input type="text" name="url" placeholder="URL Z CDA (np. https://www.cda.pl/video/...)" required>
            <br>
            <button type="submit">GENERUJ LINK DO GRY</button>
        </form>

        {% if mc_link %}
            <div class="success-box">
                <p>[+] LINK_WYGENEROWANY:</p>
                <code>{{ mc_link }}</code>
                <p style="font-size: 10px; color: #888; margin-top: 10px;">Skopiuj i wklej w Minecraft.</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    mc_link = None
    if request.method == 'POST':
        source_url = request.form.get('url')
        # Tworzymy adres "wirtualnego wideo"
        # Uzywamy hosta z prosby, zeby link byl zawsze poprawny (np. filmiki.onrender.com)
        mc_link = f"https://{request.host}/play.mp4?url={source_url}"
    return render_template_string(HTML_LAYOUT, mc_link=mc_link)

@app.route('/play.mp4')
def play_video():
    video_url = request.args.get('url')
    
    # Szukamy najlepszego formatu, ktory ma i video i audio (best)
    # To jest kluczowe dla Minecrafta - on nie polaczy sam 2 linkow.
    ydl_opts = {
        'format': 'best', 
        'quiet': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            direct_url = info.get('url')

        # Streamowanie "w locie" z CDA do Minecrafta
        def generate():
            r = requests.get(direct_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
            for chunk in r.iter_content(chunk_size=1024*1024): # 1MB bufor
                yield chunk

        return Response(stream_with_context(generate()), content_type="video/mp4")
    
    except Exception as e:
        return f"ERROR_STREAMING: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
