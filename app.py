import os
import yt_dlp
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>TERMINAL://EXTRACTOR_V11</title>
    <style>
        body { background: #050505; color: #00ff41; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .terminal { border: 1px solid #00ff41; padding: 25px; background: #000; width: 90%; max-width: 600px; box-shadow: 0 0 20px #00ff4144; }
        input { background: #000; border: 1px solid #00ff41; color: #00ff41; padding: 12px; width: 100%; box-sizing: border-box; margin-bottom: 15px; outline: none; }
        button { background: #00ff41; color: #000; border: none; padding: 12px; width: 100%; cursor: pointer; font-weight: bold; text-transform: uppercase; }
        .result { margin-top: 20px; border-top: 1px dashed #00ff41; padding-top: 15px; font-size: 13px; }
        .btn-link { background: #00ff41; color: #000; padding: 10px; text-decoration: none; display: inline-block; font-weight: bold; margin-top: 10px; }
        .error { color: #ff3333; }
    </style>
</head>
<body>
    <div class="terminal">
        <h2>> ROOT@CORE: V11.0_STABLE_EXTRACT</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="PASTE_URL_HERE..." required>
            <button type="submit">EXTRACT_STREAMS</button>
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
        
        # ZMIANA: Usuwamy 'format': 'best' z ydl_opts, aby uniknąć błędu 
        # "Requested format is not available". Pobieramy wszystkie info.
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Szukamy linku w sposób hierarchiczny
                final_link = None
                
                # 1. Sprawdźmy, czy CDA wystawiło gotowy link (często 720p/480p)
                if info.get('url'):
                    final_link = info.get('url')
                
                # 2. Jeśli nie, przeszukajmy listę wszystkich dostępnych formatów
                if not final_link or "manifest" in final_link:
                    formats = info.get('formats', [])
                    # Szukamy od najlepszego (od tyłu listy)
                    for f in reversed(formats):
                        # Szukamy formatu, który NIE jest samym audio ani samym wideo
                        if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                            # Pomijamy manifesty m3u8/mpd, bo nie pobierzesz ich jednym klikiem
                            if not f.get('url', '').endswith(('.m3u8', '.mpd')):
                                final_link = f.get('url')
                                break
                
                if final_link:
                    content = f'''
                    <p>[+] OBJ: {info.get('title', 'Unknown')[:50]}</p>
                    <p>[+] STATUS: READY_TO_OPEN</p>
                    <a href="{final_link}" target="_blank" class="btn-link">POBIERZ FILMIK (MP4)</a>
                    <p style="font-size:10px; margin-top:10px; color:#666;">Prawym Przyciskiem Myszy -> Zapisz jako.</p>
                    '''
                else:
                    content = '<p class="error">[-] FAIL: NO_DIRECT_MP4_FOUND</p>'
                    
        except Exception as e:
            content = f'<p class="error">[-] ERR: {str(e)[:150]}</p>'
            
    return render_template_string(HTML_LAYOUT, content=content)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
