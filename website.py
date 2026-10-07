import os
import sqlite3
from flask import Flask, send_from_directory, render_template, request, redirect

app = Flask(__name__)

DATABASE = "music.db"

UPLOAD_FOLDER = "uploads"
MUSIC_FOLDER = os.path.join(UPLOAD_FOLDER, "music")
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, "images")

os.makedirs(MUSIC_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)


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

    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()

    database.close()

    return render_template("index.html", songs=songs)


@app.route("/add-song", methods=["GET", "POST"])
def add_song():

    if request.method == "POST":

        title = request.form["title"]
        artist = request.form["artist"]

        audio_file = request.files["audio"]
        cover_file = request.files["cover"]

        audio = audio_file.filename
        cover = cover_file.filename

        audio_file.save(os.path.join(MUSIC_FOLDER, audio))
        cover_file.save(os.path.join(IMAGE_FOLDER, cover))

        database = sqlite3.connect(DATABASE)
        cursor = database.cursor()

        cursor.execute("""
        INSERT INTO songs (title, artist, audio, cover)
        VALUES (?, ?, ?, ?)
        """, (title, artist, audio, cover))

        database.commit()
        database.close()

        return redirect("/")

    return render_template("add_song.html")


@app.route("/music/<filename>")
def music(filename):
    return send_from_directory(MUSIC_FOLDER, filename)


@app.route("/images/<filename>")
def images(filename):
    return send_from_directory(IMAGE_FOLDER, filename)


if __name__ == "__main__":
    app.run()
