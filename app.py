from flask import Flask, request, render_template_string
import yt_dlp

app = Flask(__name__)

# Terminalowy wygląd (Cyberpunk/Hacker style)
HTML_FORM = '''
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
            position: relative;
        }
        .terminal::before {
            content: "SYSTEM STATUS: READY";
            display: block;
            font-size: 10px;
            margin-bottom: 20px;
            border-bottom: 1px solid #00ff41;
            padding-bottom: 5px;
        }
        h2 { font-size: 1.5rem; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px; }
        input { 
            background: #000; 
            border: 1px solid #00ff41; 
            color: #00ff41; 
            padding: 10px; 
            width: 100%; 
            box-sizing: border-box;
            margin-bottom: 20px;
            outline: none;
        }
        input::placeholder { color: rgba(0, 255, 65, 0.4); }
        button { 
            background: #00ff41; 
            color: #000; 
            border: none; 
            padding: 10px 20px; 
            font-weight: bold; 
            cursor: pointer; 
            text-transform: uppercase;
            width: 100%;
            transition: 0.3s;
        }
        button:hover { 
            background: #000; 
            color: #00ff41; 
            border: 1px solid #00ff41;
            box-shadow: 0 0 10px #00ff41;
        }
        .cursor { display: inline-block; width: 10px; height: 18px; background: #00ff41; animation: blink 1s infinite; vertical-align: middle; }
        @keyframes blink { 0% { opacity: 0; } 50% { opacity: 1; } 100% { opacity: 0; } }
    </style>
</head>
<body>
    <div class="terminal">
        <h2>> ROOT@EXTRACTOR: access_video_<span class="cursor"></span></h2>
        <form method="POST" action="/get-link">
            <input type="text" name="url" placeholder="ENTER_URL_HERE..." required>
            <button type="submit">EXECUTE_EXTRACTION</button>
        </form>
    </div>
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
                <style>
                    body {{ background: #0a0a0a; color: #00ff41; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
                    .terminal {{ border: 2px solid #00ff41; padding: 30px; background: #000; text-align: center; box-shadow: 0 0 20px #00ff4133; }}
                    a {{ color: #000; background: #00ff41; padding: 10px 20px; text-decoration: none; display: inline-block; margin-top: 20px; font-weight: bold; }}
                    .home-link {{ background: transparent; color: #00ff41; border: 1px dashed #00ff41; font-size: 12px; margin-top: 30px; }}
                </style>
                <div class="terminal">
                    <h2>[+] INJECTION_SUCCESSFUL</h2>
                    <p>TARGET: {info.get('title', 'UNKNOWN_OBJECT')}</p>
                    <a href="{direct_url}" target="_blank">DOWNLOAD_STREAM_V.01</a>
                    <br>
                    <a href="/" class="home-link">RETURN_TO_CONSOLE</a>
                </div>
                '''
            else:
                return "<body style='background:#000;color:red;font-family:monospace;padding:50px;'>[-] ERROR: DIRECT_LINK_NOT_FOUND. <a href='/' style='color:white;'>BACK</a></body>"
        except Exception as e:
            return f"<body style='background:#000;color:red;font-family:monospace;padding:50px;'>[-] SYSTEM_CRITICAL_FAILURE: {str(e)} <a href='/' style='color:white;'>BACK</a></body>"

if __name__ == "__main__":
    app.run()
