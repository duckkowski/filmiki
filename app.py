from flask import Flask, request, redirect, render_template_string
import yt_dlp

app = Flask(__name__)

# Prosty formularz HTML
HTML_FORM = '''
<!DOCTYPE html>
<html>
<head><title>Video Link Generator</title></head>
<body>
    <h2>Wklej link (YT, TikTok, itp.)</h2>
    <form method="POST" action="/get-link">
        <input type="text" name="url" style="width:300px;" placeholder="https://www.youtube.com/watch?v=...">
        <button type="submit">Generuj bezpośredni link</button>
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML_FORM

@app.route('/get-link', methods=['POST'])
def get_link():
    video_url = request.form.get('url')
    
    ydl_opts = {
        'format': 'best',
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            # Pobieramy bezpośredni URL do pliku wideo
            direct_url = info.get('url')
            return f'<h3>Twój link:</h3><a href="{direct_url}">Kliknij, aby otworzyć/pobrać wideo</a>'
        except Exception as e:
            return f"Błąd: {str(e)}"

if __name__ == "__main__":
    app.run()
