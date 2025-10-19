# Data dummy (in-memory)
# Data user untuk login
USERS = {
    "user1@example.com": {
        "id": "user1",
        "email": "user1@example.com",
        "password": "pass123", 
        "name": "User Satu"
    },
    "user2@example.com": {
        "id": "user2",
        "email": "user2@example.com",
        "password": "password",
        "name": "User Dua"
    }
}

# Data item marketplace
ITEMS = [
    { "id": 1, "name": "Laptop Canggih", "price": 15000000 },
    { "id": 2, "name": "Mouse Gaming", "price": 750000 }
]

# backend/app.py

import os
import datetime
from functools import wraps
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import jwt # Library PyJWT
from dotenv import load_dotenv

# Muat variabel dari .env
load_dotenv()

# --- Setup Aplikasi Flask ---
app = Flask(__name__)
# Ambil konfigurasi dari .env
app.config["JWT_SECRET"] = os.environ.get('JWT_SECRET')
app.config["PORT"] = int(os.environ.get('PORT', 5000))
# Aktifkan CORS (sesuai instruksi)
CORS(app)


# --- "Database" Sederhana (In-Memory) ---
USERS = {
    "user1@example.com": {
        "id": "user1",
        "email": "user1@example.com",
        "password": "pass123", 
        "name": "User Satu"
    }
}

ITEMS = [
    { "id": 1, "name": "Laptop Canggih", "price": 15000000 },
    { "id": 2, "name": "Mouse Gaming", "price": 750000 }
]

# --- Helper: JWT Decorator ---
# Ini adalah "Middleware" untuk memproteksi endpoint
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Cek apakah header 'Authorization' ada
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Ambil token dari header "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Format token buruk"}), 401

        if not token:
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        try:
            # Decode token menggunakan SECRET kita
            # Ini akan memvalidasi signature DAN expiry (exp)
            data = jwt.decode(token, app.config['JWT_SECRET'], algorithms=["HS256"])
            
            # Cari user berdasarkan 'sub' (subject) dari token
            current_user = USERS.get(data['sub'])
            if current_user is None:
                 return jsonify({"error": "User tidak ditemukan"}), 404
            
            # Simpan data user di 'g' (global context) Flask
            # agar bisa diakses oleh endpoint yang diproteksi
            g.current_user = current_user

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        # Lanjutkan ke fungsi endpoint aslinya
        return f(*args, **kwargs)
    return decorated


# --- Endpoint 1: Login ---
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email dan password diperlukan"}), 400

    # Cek kredensial
    user = USERS.get(email)
    if not user or user['password'] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    # Kredensial valid, buat token
    payload = {
        'sub': user['email'],  # Subject (siapa pemilik token)
        'email': user['email'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15) # Expired dalam 15 menit
    }

    # Buat JWT
    token = jwt.encode(
        payload,
        app.config['JWT_SECRET'],
        algorithm="HS256"
    )

    return jsonify({"access_token": token}), 200


# --- Endpoint 2: Items (Publik) ---
@app.route('/items', methods=['GET'])
def get_items():
    # Endpoint ini publik, siapa saja bisa akses
    return jsonify({"items": ITEMS}), 200


# --- Endpoint 3: Profile (Terproteksi) ---
@app.route('/profile', methods=['PUT'])
@token_required  # <-- KUNCI-nya di sini!
def update_profile():
    # Karena ada @token_required, kita bisa akses g.current_user
    # 'g.current_user' sudah di-set oleh decorator
    user_email = g.current_user['email']
    user_data = USERS[user_email]

    data = request.json
    
    # Validasi input sederhana
    if 'name' in data and data['name']:
        user_data['name'] = data['name']
    
    # (Catatan: Mengubah email biasanya butuh verifikasi ulang)
    if 'email' in data and data['email']:
        new_email = data['email']
        # Logika update email (harus unik, dll)
        # Untuk demo ini, kita update saja
        user_data['email'] = new_email
        # Update key di dictionary USERS jika email berubah
        if new_email != user_email:
            USERS[new_email] = USERS.pop(user_email)

    
    # Siapkan data profil untuk respon (tanpa password)
    profile_response = {
        "id": user_data['id'],
        "name": user_data['name'],
        "email": user_data['email']
    }

    return jsonify({
        "message": "Profile updated",
        "profile": profile_response
    }), 200


# --- Menjalankan Server ---
if __name__ == '__main__':
    # Setting host='0.0.0.0' agar bisa diakses dari luar (Postman)
    app.run(host='0.0.0.0', port=app.config["PORT"], debug=True)