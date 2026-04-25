from flask import Flask, request, render_template_string
import yt_dlp
import os

app = Flask(__name__)

# --- HAKERSKI LAYOUT TERMINALA ---
HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>TERMINAL://VIDEO_EXTRACTOR_V4</title>
    <style>
        body { 
            background-color: #050505; 
            color: #00ff41; 
            font-family: 'Courier New', Courier, monospace; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0;
            text-shadow: 0 0 3px #00ff41;
        }
        .terminal { 
            background: #000; 
            border: 1px solid #00ff41; 
            padding: 30px; 
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
            width: 90%;
            max-width: 650px;
        }
        h2 { font-size: 1.2rem; margin-bottom: 20px; border-bottom: 1px solid #00ff41; padding-bottom: 10px; }
        input { 
            background: #000; 
            border: 1px solid #00ff41; 
            color: #00ff41; 
            padding: 12px; 
            width: 100%; 
            box-sizing: border-box;
            margin-bottom: 20px;
            outline: none;
            font-family: monospace;
        }
        button { 
            background: #00ff41; 
            color: #000; 
            border: none; 
            padding: 12px 20px; 
            font-weight: bold; 
            cursor: pointer; 
            width: 100%;
            text-transform: uppercase;
        }
        button:hover { background: #008f11; }
        .result-box { margin-top: 25px; padding: 15px; border: 1px dashed #00ff41; background: rgba(0,255,65,0.05); }
        .download-btn { 
            color: #000; 
            background: #00ff41; 
            padding: 12px 20px; 
            text-decoration: none; 
            font-weight: bold; 
            display: inline-block; 
            margin-top: 15px; 
        }
        .error { color: #ff3333; font-weight: bold; font-size: 12px; }
    </style>
</head>
<body>
    <div class="terminal">
        <h2>> SYSTEM: EXTRACTOR_V4.0_PATCHED</h2>
        <form method="POST" action="/get-link">
            <input type="text" name="url" placeholder="PASTE_SOURCE_URL_HERE..." required>
            <button type="submit">RUN_DECRYPTION</button>
        </form>
        {% if content %}
            <div class="result-box">
                {{ content | safe }}
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_LAYOUT)

@app.route('/get-link', methods=['POST'])
def get_link():
    video_url = request.form.get('url')
    
    ydl_opts = {
        # ZMIANA: Szukamy najlepszego formatu, który ma i wideo i audio (b), 
        # bez wymuszania konkretnie rozszerzenia mp4, co często blokuje CDA.
        'format': 'b/best', 
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            
            # Próbujemy wyciągnąć URL z różnych możliwych miejsc w danych
            direct_url = info.get('url') or info.get('requested_formats', [{}])[0].get('url')
            
            if direct_url:
                res_html = f'''
                <p>[!] DATA_FOUND: {info.get('title', 'OBJECT_UNKNOWN')[:50]}</p>
                <p>[!] STATUS: STREAM_DECRYPTED_V4</p>
                <a href="{direct_url}" target="_blank" class="download-btn">DOWNLOAD_FULL_STREAM</a>
                <br><br>
                <a href="/" style="color:#00ff41; font-size:11px;">REBOOT_SYSTEM</a>
                '''
                return render_template_string(HTML_LAYOUT, content=res_html)
            else:
                return render_template_string(HTML_LAYOUT, content='<p class="error">[-] FAIL: NO_INTEGRATED_STREAM_AVAILABLE</p>')
                
        except Exception as e:
            # Wyświetlamy błąd, ale w wersji terminalowej
            return render_template_string(HTML_LAYOUT, content=f'<p class="error">[-] EXCEPTION: {str(e)}</p>')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
