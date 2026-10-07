from flask import Flask, send_from_directory, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = "music.db"


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

        audio_file.save(
            r"C:\Users\User\Desktop\music website\\" + audio
        )

        cover_file.save(
            r"C:\Users\User\Desktop\music website\\" + cover
        )

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
    return send_from_directory(
        r"C:\Users\User\Desktop\music website",
        filename
    )


@app.route("/images/<filename>")
def images(filename):
    return send_from_directory(
        r"C:\Users\User\Desktop\music website",
        filename
    )


if __name__ == "__main__":
    app.run()
