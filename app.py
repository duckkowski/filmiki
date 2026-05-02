import os
import uuid
import tempfile
import subprocess
import yt_dlp

from flask import Flask, request, render_template_string, send_file, url_for

app = Flask(__name__)

# folder na gotowe pliki
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<title>MP4 MUXER</title>
<style>
body{
    background:#050505;
    color:#00ff41;
    font-family:Courier New, monospace;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
    margin:0;
}
.box{
    border:1px solid #00ff41;
    padding:30px;
    width:700px;
    background:#001100;
}
input{
    width:75%;
    padding:10px;
    background:#000;
    color:#00ff41;
    border:1px solid #00ff41;
}
button,a.btn{
    padding:10px 18px;
    background:#00ff41;
    color:#000;
    border:none;
    text-decoration:none;
    font-weight:bold;
    cursor:pointer;
}
.result{
    margin-top:25px;
    padding-top:20px;
    border-top:1px dashed #00ff41;
}
</style>
</head>
<body>
<div class="box">
<h2>[ MP4 FULL DOWNLOAD ]</h2>

<form method="POST">
<input type="text" name="url" placeholder="wklej link..." required>
<button type="submit">GENERUJ</button>
</form>

{% if ready %}
<div class="result">
<p>Plik gotowy.</p>
<a class="btn" href="{{ file_url }}">POBIERZ CAŁE MP4</a>
</div>
{% endif %}

{% if error %}
<div class="result">
<p>{{ error }}</p>
</div>
{% endif %}

</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video_url = request.form.get("url")

        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(video_url, download=False)

                v_url = None
                a_url = None

                for f in info["formats"]:
                    # najlepszy video only
                    if f.get("vcodec") != "none" and f.get("acodec") == "none":
                        v_url = f["url"]

                for f in info["formats"]:
                    # audio only
                    if f.get("acodec") != "none" and f.get("vcodec") == "none":
                        a_url = f["url"]
                        break

                # jeśli jest normalny mp4 z audio
                if not v_url:
                    for f in info["formats"]:
                        if f.get("ext") == "mp4" and f.get("acodec") != "none":
                            v_url = f["url"]
                            a_url = None
                            break

            if not v_url:
                return render_template_string(HTML, error="Nie znaleziono video.")

            filename = f"{uuid.uuid4().hex}.mp4"
            filepath = os.path.join(DOWNLOAD_DIR, filename)

            if a_url:
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i", v_url,
                    "-i", a_url,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-movflags", "+faststart",
                    filepath
                ]
            else:
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i", v_url,
                    "-c", "copy",
                    "-movflags", "+faststart",
                    filepath
                ]

            subprocess.run(cmd, check=True)

            file_url = url_for("download_file", name=filename)

            return render_template_string(
                HTML,
                ready=True,
                file_url=file_url
            )

        except Exception as e:
            return render_template_string(
                HTML,
                error=f"Błąd: {str(e)}"
            )

    return render_template_string(HTML)


@app.route("/download/<name>")
def download_file(name):
    path = os.path.join(DOWNLOAD_DIR, name)

    return send_file(
        path,
        mimetype="video/mp4",
        as_attachment=True,
        download_name="film.mp4"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
