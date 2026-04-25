from flask import Flask, request, render_template_string
import yt_dlp

# 1. NAJPIERW tworzymy obiekt aplikacji
app = Flask(__name__)

# Prosty interfejs użytkownika
HTML_FORM = '''
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Video Link Generator</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding-top: 50px; background: #f0f2f5; }
        .box { background: white; padding: 30px; border-radius: 10px; display: inline-block; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input { width: 300px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="box">
        <h2>🎥 Video Link Extractor</h2>
        <form method="POST" action="/get-link">
            <input type="text" name="url" placeholder="Wklej link z YouTube, CDA, itp." required>
            <button type="submit">Generuj link</button>
        </form>
    </div>
</body>
</html>
'''

# 2. POTEM definiujemy trasy (routes)
@app.route('/')
def index():
    return HTML_FORM

@app.route('/get-link', methods=['POST'])
def get_link():
    video_url = request.form.get('url')
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            direct_url = info.get('url') or info.get('requested_formats', [{}])[0].get('url')
            
            if direct_url:
                return f'''
                <div style="text-align:center; margin-top:50px; font-family:sans-serif;">
                    <h3>Sukces!</h3>
                    <p>Tytuł: <b>{info.get('title', 'Wideo')}</b></p>
                    <a href="{direct_url}" target="_blank" style="padding: 15px 25px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        KLIKNIJ, ABY POBRAĆ / OTWORZYĆ WIDEO
                    </a>
                    <br><br>
                    <a href="/">Wróć do strony głównej</a>
                </div>
                '''
            else:
                return "Błąd: Nie znaleziono bezpośredniego linku do pliku."
        except Exception as e:
            return f"Wystąpił błąd podczas przetwarzania: {str(e)}"

# 3. NA KOŃCU uruchamiamy (Render użyje Gunicorna, więc to jest dla testów lokalnych)
if __name__ == "__main__":
    app.run()
