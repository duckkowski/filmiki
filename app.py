import os
import yt_dlp
from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)

HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>TERMINAL://VIDEO_EXTRACTOR_FINAL</title>
    <style>
        body { background: #050505; color: #00ff41; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .terminal { border: 1px solid #00ff41; padding: 25px; background: #000; width: 90%; max-width: 600px; box-shadow: 0 0 15px #00ff4144; }
        input { background: #000; border: 1px solid #00ff41; color: #00ff41; padding: 12px; width: 100%; box-sizing: border-box; margin-bottom: 15px; outline: none; font-family: monospace; }
        button { background: #00ff41; color: #000; border: none; padding: 12px; width: 100%; cursor: pointer; font-weight: bold; text-transform: uppercase; }
        .result { margin-top: 20px; border-top: 1px dashed #00ff41; padding-top: 15px; }
        .btn-link { background: #00ff41; color: #000; padding: 10px; text-decoration: none; display: inline-block; font-weight: bold; margin-top: 10px; }
        .error { color: #ff3333; }
    </style>
</head>
<body>
    <div class="terminal">
        <h2>> ROOT@CORE: EXTRACTOR_V9_STABLE</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="WKLEJ LINK Z CDA LUB YT..." required>
            <button type="submit">ROZPOCZNIJ DESZYFROWANIE</button>
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
        
        # Całkowicie luźne opcje, żeby nie blokować żadnego formatu
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Wyciągamy surowe dane bez pobierania
                info = ydl.extract_info(url, download=False)
                
                # Szukamy formatu, który ma i wideo i audio w jednym (acodec != none i vcodec != none)
                formats = info.get('formats', [])
                best_combined = None
                
                # Przeszukujemy listę od końca (zazwyczaj najlepsza jakość na końcu)
                for f in reversed(formats):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        best_combined = f.get('url')
                        break
                
                # Jeśli nie znaleźliśmy idealnego, bierzemy główny URL (często 720p/480p)
                final_url = best_combined or info.get('url')
                
                if final_url:
                    content = f'''
                    <p>[+] OBIEKT: {info.get('title', 'Nieznany')[:50]}...</p>
                    <p>[+] STATUS: LINK_STABILNY_Z_DZWIĘKIEM</p>
                    <a href="{final_url}" target="_blank" class="btn-link">OTWÓRZ FILMIK</a>
                    <p style="font-size:10px; margin-top:10px; color:#666;">* Link prowadzi bezpośrednio do streamu. Możesz kliknąć Prawym Przyciskiem -> Zapisz jako.</p>
                    '''
                else:
                    content = '<p class="error">[-] BŁĄD: NIE ZNALEZIONO KOMPATYBILNEGO STRUMIENIA</p>'
        except Exception as e:
            content = f'<p class="error">[-] AWARIA SYSTEMU: {str(e)[:150]}</p>'
            
    return render_template_string(HTML_LAYOUT, content=content)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
