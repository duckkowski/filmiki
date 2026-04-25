import os
import yt_dlp
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>TERMINAL://EXTRACTOR_V10</title>
    <style>
        body { background: #050505; color: #00ff41; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .terminal { border: 1px solid #00ff41; padding: 25px; background: #000; width: 90%; max-width: 600px; box-shadow: 0 0 20px #00ff41; }
        input { background: #000; border: 1px solid #00ff41; color: #00ff41; padding: 12px; width: 100%; box-sizing: border-box; margin-bottom: 15px; outline: none; }
        button { background: #00ff41; color: #000; border: none; padding: 12px; width: 100%; cursor: pointer; font-weight: bold; text-transform: uppercase; }
        .result { margin-top: 20px; border-top: 1px dashed #00ff41; padding-top: 15px; font-size: 13px; }
        .btn-link { background: #00ff41; color: #000; padding: 10px; text-decoration: none; display: inline-block; font-weight: bold; margin-top: 10px; }
        .error { color: #ff3333; }
    </style>
</head>
<body>
    <div class="terminal">
        <h2>> ROOT@CORE: V10.0_GHOST_MODE</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="PASTE_SOURCE_URL..." required>
            <button type="submit">BYPASS_AND_EXTRACT</button>
        </form>
        {% if content %}
            <div class="result">{{ content | safe }}</div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    content = None
    if request.method == 'POST':
        url = request.form.get('url')
        
        ydl_opts = {
            # Wybieramy najlepszy format z audio i wideo (b) lub po prostu najlepszy (best)
            'format': 'best', 
            'quiet': True,
            'no_warnings': True,
            # Kluczowe dla YouTube: udajemy zwykłego użytkownika
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'addheaders': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.google.com/',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Próbujemy znaleźć link w kilku miejscach
                final_url = None
                
                # 1. Sprawdzamy czy główny URL ma wideo+audio
                if info.get('acodec') != 'none' and info.get('vcodec') != 'none':
                    final_url = info.get('url')
                
                # 2. Jeśli nie, szukamy w formatach
                if not final_url:
                    formats = info.get('formats', [])
                    for f in reversed(formats):
                        # Szukamy formatu 'combined' (v+a)
                        if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                            final_url = f.get('url')
                            break
                
                # 3. Ostateczna deska ratunku - weź cokolwiek co daje YoutubeDL
                if not final_url:
                    final_url = info.get('url')

                if final_url:
                    content = f'''
                    <p>[+] OBJ: {info.get('title', 'Target')[:50]}</p>
                    <p>[+] STATUS: BYPASS_SUCCESSFUL</p>
                    <a href="{final_url}" target="_blank" class="btn-link">OPEN_STREAM_WITH_AUDIO</a>
                    '''
                else:
                    content = '<p class="error">[-] FAIL: NO_STREAM_FOUND</p>'
        except Exception as e:
            msg = str(e)
            if "Sign in to confirm" in msg:
                msg = "YouTube zablokował IP serwera (BOT_DETECTION). Spróbuj za chwilę lub użyj linku z CDA."
            content = f'<p class="error">[-] ERR: {msg[:100]}</p>'
            
    return render_template_string(HTML_LAYOUT, content=content)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
