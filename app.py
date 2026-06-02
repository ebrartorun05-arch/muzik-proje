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
    email TEXT,
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

# Sayısal veriye çevir
for col in feature_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=feature_cols)

# Ölçekleme
scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df[feature_cols])

# =========================
# GİRİŞ (LOGIN) SAYFASI
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Veritabanına kaydet
        cursor.execute(
            "INSERT INTO users(email, password) VALUES(?,?)",
            (email, password)
        )
        conn.commit()

        return redirect("/home")

    return render_template("login.html")

# =========================
# ANA SAYFA (MÜZİK PANELİ)
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
        'similarity',
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
    




from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(_name_)

# Veritabanı dosyasının kaydedileceği yolu belirliyoruz
# Proje klasörünün içinde 'veritabanı.db' adında bir dosya oluşturur
BASE_DIR = os.path.abspath(os.path.dirname(_file_))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'veritabanı.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Veritabanı nesnesini başlatıyoruz
db = SQLAlchemy(app)

# Örnek bir Veritabanı Tablosu (Modeli)
class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(50), nullable=False)
    eposta = db.Column(db.String(100), unique=True, nullable=False)

    def _repr_(self):
        return f'<Kullanici {self.isim}>'

@app.route('/')
def ana_sayfa():
    # Test amaçlı veritabanından tüm kullanıcıları çekelim
    # (İlk başta boş dönecektir)
    kullanicilar = Kullanici.query.all()
    return f"Veritabanı bağlantısı başarılı! Toplam kullanıcı sayısı: {len(kullanicilar)}"

if _name_ == '_main_':
    # Veritabanı tabloları eğer yoksa otomatik olarak oluşturulur
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)