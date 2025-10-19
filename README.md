Tes Uji:
https://drive.google.com/file/d/1If-aHNbweb1ONROHusrNuOGHLBkuepuI/view?usp=sharing

Proyek API Sederhana dengan JWT (Tugas 1)
Proyek ini adalah implementasi API sederhana menggunakan Flask (Python) dengan autentikasi JWT (JSON Web Token)-

1. Setup & Instalasi
Clone repositori ini (atau salin folder).

Masuk ke direktori backend/:
cd backend

Buat Python virtual environment:
python -m venv venv

Aktifkan environment:
Windows (PowerShell): .\venv\Scripts\Activate.ps1
Windows (CMD): .\venv\Scripts\activate.bat
Mac/Linux: source venv/bin/activate

Install library yang dibutuhkan:
pip install -r requirements.txt

2. Konfigurasi Environment
Di dalam folder backend/, buat file .env.

Salin isi dari .env.example:

JWT_SECRET=your_super_secret_key_here
PORT=5000

Ganti JWT_SECRET dengan secret key acak yang kuat.

3. Menjalankan Server
Pastikan Anda berada di folder backend/ dan virtual env aktif.

python app.py

Server akan berjalan di http://localhost:5000.

4. Pengujian Endpoint (cURL)
Buka terminal baru (CMD atau PowerShell) untuk menjalankan tes ini. Perintah ini menggunakan curl.exe agar kompatibel dengan Windows.

4.1 Login (Dapatkan Token)
Jalankan ini untuk login dan mendapatkan token.

curl.exe -s -X POST http://localhost:5000/auth/login -H "Content-Type: application/json" -d "{\"email\":\"user1@example.com\",\"password\":\"pass123\"}"

Respon:
{"access_token":"<JWT_PANJANG_ANDA>"}
(PENTING: Salin token yang panjang ini untuk langkah 4.3)

4.2 Cek Items (Publik)
curl.exe -s http://localhost:5000/items

Respon:
{"items":[{"id":1,"name":"Laptop Canggih",...}]}

4.3 Update Profile (Terproteksi)
Ganti PASTE_TOKEN_ANDA_DI_SINI dengan token yang Anda salin dari langkah 4.1.

curl.exe -s -X PUT http://localhost:5000/profile -H "Authorization: Bearer PASTE_TOKEN_ANDA_DI_SINI" -H "Content-Type: application/json" -d "{\"name\":\"User Satu Baru\"}"

Respon (Sukses):
{
  "message": "Profile updated",
  "profile": {
    "email": "user1@example.com",
    "id": "user1",
    "name": "User Satu Baru"
  }
}

4.4 Tes Gagal (Tanpa Token)
Ini untuk membuktikan endpoint aman dan akan mengembalikan error 401.

curl.exe -s -X PUT http://localhost:5000/profile -H "Content-Type: application/json" -d "{\"name\":\"Nama Gagal\"}"

Respon (Gagal 401):
{"error":"Missing or invalid Authorization header"}
