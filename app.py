import os
import yt_dlp
import uuid
from flask import Flask, request, render_template_string, send_file, after_this_request

app = Flask(__name__)

# Katalog tymczasowy (Render pozwala na zapis w /tmp)
DOWNLOAD_FOLDER = '/tmp'

# --- INTERFEJS TERMINALOWY ---
HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>TERMINAL://HEAVY_MERGER_V6</title>
    <style>
        body { background: #050505; color: #00ff41; font-family: 'Courier New', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .terminal { border: 1px solid #00ff41; padding: 30px; background: #000; box-shadow: 0 0 20px #00ff4144; width: 90%; max-width: 600px; }
        h2 { font-size: 1.2rem; border-bottom: 1px solid #00ff41; padding-bottom: 10px; margin-bottom: 20px; text-transform: uppercase; }
        input { background: #000; border: 1px solid #00ff41; color: #00ff41; padding: 12px; width: 100%; box-sizing: border-box; margin-bottom: 20px; outline: none; }
        button { background: #00ff41; color: #000; border: none; padding: 15px; width: 100%; cursor: pointer; font-weight: bold; text-transform: uppercase; transition: 0.3s; }
        button:hover { background: #008f11; box-shadow: 0 0 10px #00ff41; }
        .log { margin-top: 20px; font-size: 11px; color: #00ff41; border-top: 1px dashed #00ff41; padding-top: 15px; line-height: 1.5; }
        .warning { color: #ffaa00; font-size: 10px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="terminal">
        <h2>> ROOT@MERGER: EXECUTE_FULL_SYNC</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="ENTER_TARGET_URL_FOR_PROCESSING..." required>
            <button type="submit">START_EXTRACTION_&_MERGE</button>
        </form>
        <p class="warning">UWAGA: Łączenie Audio+Video zajmuje dużo RAM i czasu. <br>System może przerwać połączenie przy dużych plikach.</p>
        {% if msg %}
            <div class="log">
                <p>> STATUS: {{ msg }}</p>
                <a href="/" style="color:#00ff41;">[ POWRÓT_DO_KONSOLI ]</a>
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form.get('url')
        
        # Generujemy unikalną nazwę pliku, żeby wielu użytkowników sobie nie przeszkadzało
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f"merged_{unique_id}.mp4"
        output_path = os.path.join(DOWNLOAD_FOLDER, output_filename)

        # Opcje pobierania i mergowania
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best', # Pobierz najlepsze osobno
            'merge_output_format': 'mp4',        # Sklej do MP4 za pomocą FFmpeg
            'outtmpl': output_path,              # Gdzie zapisać plik
            'quiet': False,                      # Pokazuj logi w konsoli Rendera
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # To jest moment, w którym serwer pobiera i skleja (FFmpeg startuje)
                ydl.download([video_url])
            
            # Sprawdzamy czy plik faktycznie powstał
            if os.path.exists(output_path):
                
                # Funkcja do usunięcia pliku po wysłaniu go użytkownikowi (czyszczenie dysku)
                @after_this_request
                def cleanup(response):
                    try:
                        if os.path.exists(output_path):
                            os.remove(output_path)
                    except Exception as e:
                        app.logger.error(f"Błąd podczas usuwania pliku: {e}")
                    return response

                # Wysyłamy gotowy plik do przeglądarki
                return send_file(output_path, as_attachment=True)
            else:
                return render_template_string(HTML_LAYOUT, msg="FAILED: MERGED_FILE_NOT_CREATED")

        except Exception as e:
            # Wyświetlamy błąd w konsoli terminalowej
            return render_template_string(HTML_LAYOUT, msg=f"CRITICAL_SYSTEM_FAILURE: {str(e)[:200]}")
            
    return render_template_string(HTML_LAYOUT)

if __name__ == "__main__":
    # Render używa zmiennej środowiskowej PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
