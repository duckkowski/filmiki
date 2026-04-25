from flask import Flask, request, render_template_string
import yt_dlp
import os

app = Flask(__name__)

# --- STYLISTYKA TERMINALA ---
HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>TERMINAL://VIDEO_EXTRACTOR</title>
    <style>
        body { 
            background-color: #0a0a0a; 
            color: #00ff41; 
            font-family: 'Courier New', Courier, monospace; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0;
            text-shadow: 0 0 5px #00ff41;
        }
        .terminal { 
            background: #000; 
            border: 2px solid #00ff41; 
            padding: 30px; 
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.2);
            width: 90%;
            max-width: 600px;
        }
        h2 { font-size: 1.5rem; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px; }
        input { 
            background: #000; 
            border: 1px solid #00ff41; 
            color: #00ff41; 
            padding: 12px; 
            width: 100%; 
            box-sizing: border-box;
            margin-bottom: 20px;
            outline: none;
        }
        button { 
            background: #00ff41; 
            color: #000; 
            border: none; 
            padding: 12px 20px; 
            font-weight: bold; 
            cursor: pointer; 
            text-transform: uppercase;
            width: 100%;
        }
        button:hover { 
            background: #000; 
            color: #00ff41; 
            border: 1px solid #00ff41;
        }
        .result-box { border-top: 1px solid #00ff41; margin-top: 20px; padding-top: 20px; }
        a { color: #000; background: #00ff41; padding: 10px 15px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px; }
        .error { color: #ff003c; border: 1px solid #ff003c; padding: 10px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="terminal">
        <h2>> ROOT@EXTRACTOR: v.2.0_FFMPEG</h2>
        <form method="POST" action="/get-link">
            <input type="text" name="url" placeholder="ENTER_TARGET_URL..." required>
            <button type="submit">EXECUTE_EXTRACTION</button>
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
    
    # Konfiguracja yt-dlp pod FFmpeg (wymaga zainstalowanego FFmpeg na serwerze)
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best', # Pobierz najlepsze wideo i audio
        'merge_output_format': 'mp4',        # Połącz w MP4
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Wyciągamy informacje bez pobierania pliku na dysk
            info = ydl.extract_info(video_url, download=False)
            
            # Próbujemy znaleźć URL do już zmergowanego strumienia lub najlepszego dostępnego
            # W przypadku CDA/YouTube yt-dlp z download=False zwróci najlepszy bezpośredni link
            # Jeśli FFmpeg jest na serwerze, yt-dlp lepiej dobierze formaty.
            direct_url = info.get('url') or info.get('requested_formats', [{}])[0].get('url')
            
            if direct_url:
                res_html = f'''
                <p>[+] TARGET_ID: {info.get('title', 'UNKNOWN')[:40]}...</p>
                <p>[+] STATUS: LINK_DECRYPTED</p>
                <a href="{direct_url}" target="_blank">DOWNLOAD_STREAM_V.02</a>
                <br><br>
                <a href="/" style="background:transparent; color:#00ff41; font-size:12px; border:1px solid;">BACK_TO_CONSOLE</a>
                '''
                return render_template_string(HTML_LAYOUT, content=res_html)
            else:
                error_html = '<p class="error">[-] FAILED: COULD_NOT_LOCATE_STREAM</p>'
                return render_template_string(HTML_LAYOUT, content=error_html)
                
        except Exception as e:
            error_html = f'<p class="error">[-] CRITICAL_ERROR: {str(e)[:100]}</p>'
            return render_template_string(HTML_LAYOUT, content=error_html)

if __name__ == "__main__":
    # Port wymagany przez Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
