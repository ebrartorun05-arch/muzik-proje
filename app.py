from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)

# =========================
# VERİTABANI
# =========================
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()

# =========================
# CSV YÜKLE
# =========================
df = pd.read_csv("dataset.csv", sep=";", encoding="utf-8")

feature_cols = [
    'danceability',
    'energy',
    'key',
    'loudness',
    'speechiness',
    'acousticness',
    'instrumentalness',
    'liveness',
    'valence',
    'tempo'
]

for col in feature_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=feature_cols)

scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df[feature_cols])

# =========================
# GİRİŞ SAYFASI
# =========================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        if user:
            return redirect("/home")

        return "Email veya sifre hatali"

    return render_template("login.html")

# =========================
# KAYIT OL
# =========================
@app.route("/register", methods=["POST"])
def register():

    email = request.form["email"]
    password = request.form["password"]

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        return "Bu email zaten kayitli"

    cursor.execute(
        "INSERT INTO users(email, password) VALUES(?, ?)",
        (email, password)
    )

    conn.commit()

    return redirect("/")

# =========================
# KULLANICILARI GÖR
# =========================
@app.route("/users")
def users():

    cursor.execute(
        "SELECT id, email FROM users"
    )

    users = cursor.fetchall()

    html = """
    <h1>Kayitli Kullanicilar</h1>
    <hr>
    """

    for user in users:

        html += f"""
        <p>
        ID: {user[0]} <br>
        Email: {user[1]}
        </p>
        <hr>
        """

    return html

# =========================
# ANA SAYFA
# =========================
@app.route("/home")
def home():

    songs = sorted(
        df['track_name'].astype(str).unique()
    )

    return render_template(
        "index.html",
        songs=songs
    )

# =========================
# ÖNERİ SİSTEMİ
# =========================
@app.route("/recommend", methods=["POST"])
def recommend():

    selected_song = request.json["song"]

    idx = df[
        df['track_name'] == selected_song
    ].index[0]

    selected_vector = df_scaled[idx].reshape(1, -1)

    similarities = cosine_similarity(
        selected_vector,
        df_scaled
    )

    df['similarity'] = similarities[0]

    recommendations = df[
        df['track_name'] != selected_song
    ].sort_values(
        "similarity",
        ascending=False
    ).head(5)

    result = []

    for _, row in recommendations.iterrows():

        result.append({
            "track_name": row["track_name"],
            "artist": row["artists"]
        })

    return jsonify(result)

# =========================
# ÇALIŞTIR
# =========================
if __name__ == "__main__":
    app.run(debug=True)