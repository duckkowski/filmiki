@app.route('/get-link', methods=['POST'])
def get_link():
    video_url = request.form.get('url')
    
    # Nowe, lepsze ustawienia dla yt-dlp
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best', # Próbuj najlepsze, jak nie to cokolwiek co działa
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            
            # Niektóre serwisy (jak CDA) mogą zwracać linki w różnych polach
            direct_url = info.get('url') or info.get('requested_formats', [{}])[0].get('url')
            
            if direct_url:
                return f'''
                <h3>Sukces!</h3>
                <p>Tytuł: {info.get('title', 'Wideo')}</p>
                <a href="{direct_url}" target="_blank" style="padding: 10px; background: green; color: white; text-decoration: none; border-radius: 5px;">
                    KLIKNIJ TUTAJ, ABY POBRAĆ / OTWORZYĆ
                </a>
                <br><br>
                <small>Jeśli wideo się otworzy w przeglądarce, kliknij PRAWYM przyciskiem i wybierz "Zapisz wideo jako...".</small>
                '''
            else:
                return "Nie udało się wyciągnąć bezpośredniego linku."
        except Exception as e:
            return f"Błąd: {str(e)}"
