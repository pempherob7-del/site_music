
import os
import sqlite3
import requests

from flask import (
    Flask,
    send_from_directory,
    send_file,
    render_template,
    request,
    redirect,
    abort
)
from werkzeug.utils import secure_filename

app = Flask(__name__)

DATABASE = "music.db"

UPLOAD_FOLDER = "uploads"
MUSIC_FOLDER = os.path.join(UPLOAD_FOLDER, "music")
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, "images")

os.makedirs(MUSIC_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Add your YouTube API key here.
# Keep your real key private. 
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")


def init_db():
    database = sqlite3.connect(DATABASE)
    cursor = database.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY,
            title TEXT,
            artist TEXT,
            audio TEXT,
            cover TEXT
        )
    """)

    database.commit()
    database.close()


init_db()


@app.route("/")
def home():
    database = sqlite3.connect(DATABASE)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM songs ORDER BY id DESC")
    songs = cursor.fetchall()

    database.close()

    return render_template("index.html", songs=songs)


@app.route("/add-song", methods=["GET", "POST"])
def add_song():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        artist = request.form.get("artist", "").strip()

        audio_file = request.files.get("audio")
        cover_file = request.files.get("cover")

        if (
            not title
            or not artist
            or not audio_file
            or not cover_file
            or not audio_file.filename
            or not cover_file.filename
        ):
            return "Please provide the song title, artist, audio and cover."

        audio_name = secure_filename(audio_file.filename)
        cover_name = secure_filename(cover_file.filename)

        if not audio_name or not cover_name:
            return "Invalid filename."

        audio_path = os.path.join(MUSIC_FOLDER, audio_name)
        cover_path = os.path.join(IMAGE_FOLDER, cover_name)

        audio_file.save(audio_path)

        try:
            cover_file.save(cover_path)

            database = sqlite3.connect(DATABASE)
            cursor = database.cursor()

            cursor.execute("""
                INSERT INTO songs (title, artist, audio, cover)
                VALUES (?, ?, ?, ?)
            """, (title, artist, audio_name, cover_name))

            database.commit()
            database.close()

        except Exception:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(cover_path):
                os.remove(cover_path)
            raise

        return redirect("/")

    return render_template("add_song.html")


@app.route("/search")
def search_music():
    query = request.args.get("q", "").strip()

    if not query:
        return render_template(
            "search.html",
            results=[],
            query=""
        )

    if not YOUTUBE_API_KEY:
        return (
            "YouTube search is not configured yet. "
            "Set the YOUTUBE_API_KEY environment variable."
        ), 503

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 10,
        "key": YOUTUBE_API_KEY
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

    except requests.RequestException:
        return "YouTube search is temporarily unavailable.", 502

    results = data.get("items", [])

    return render_template(
        "search.html",
        results=results,
        query=query
    )


@app.route("/music/<filename>")
def music(filename):
    return send_from_directory(MUSIC_FOLDER, filename)


@app.route("/images/<filename>")
def images(filename):
    return send_from_directory(IMAGE_FOLDER, filename)


@app.route("/download/<filename>")
def download_song(filename):
    database = sqlite3.connect(DATABASE)
    cursor = database.cursor()

    cursor.execute(
        "SELECT title FROM songs WHERE audio = ?",
        (filename,)
    )
    song = cursor.fetchone()

    database.close()

    if not song:
        abort(404)

    return send_file(
        os.path.join(MUSIC_FOLDER, filename),
        as_attachment=True,
        download_name=os.path.basename(filename)
    )


if __name__ == "__main__":
    app.run(debug=True)
