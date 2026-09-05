# Setup MySQL Database untuk XAMPP

## Langkah-langkah Setup:

### 1. Pastikan XAMPP sudah terinstall dan berjalan
- Buka XAMPP Control Panel
- Start Apache dan MySQL

### 2. Buat Database
- Buka phpMyAdmin di browser: `http://localhost/phpmyadmin`
- Klik "New" untuk membuat database baru
- Nama database: `wedding_invitation_db`
- Collation: `utf8mb4_unicode_ci`
- Klik "Create"

### 3. Install MySQL Client untuk Python
```bash
pip install mysqlclient
```

### 4. Jalankan Migrasi Django
```bash
# Buat migrasi baru
python manage.py makemigrations

# Jalankan migrasi
python manage.py migrate

# Buat superuser (opsional)
python manage.py createsuperuser
```

### 5. Konfigurasi Database (sudah dilakukan)
- Database engine: `django.db.backends.mysql`
- Database name: `wedding_invitation_db`
- User: `root`
- Password: `` (kosong - default XAMPP)
- Host: `localhost`
- Port: `3306`

### 6. Troubleshooting

#### Jika ada error "No module named 'MySQLdb'":
```bash
pip install mysqlclient
```

#### Jika ada error saat install mysqlclient di Windows:
1. Download Microsoft C++ Build Tools
2. Atau gunakan alternatif:
```bash
pip install PyMySQL
```
Lalu tambahkan di `__init__.py` di folder project:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

#### Jika MySQL tidak bisa connect:
- Pastikan MySQL service di XAMPP sudah running
- Cek port 3306 tidak digunakan aplikasi lain
- Restart XAMPP jika perlu

### 7. Verifikasi Setup
```bash
# Test koneksi database
python manage.py dbshell

# Atau jalankan server
python manage.py runserver
```

## Perubahan yang Dilakukan:

1. **settings.py**: 
   - SQLite dikomentar
   - MySQL dikonfigurasi untuk XAMPP

2. **requirements.txt**:
   - psycopg2-binary dikomentar
   - mysqlclient ditambahkan

3. **template_editor/views.py**:
   - Import sqlite3 dikomentar
   - Fungsi SQLite dikomentar

4. **migrate_templates.py**:
   - Fungsi SQLite check dikomentar
   - Diganti dengan MySQL check

## Catatan Penting:
- Backup data SQLite sebelum migrasi jika diperlukan
- Pastikan XAMPP MySQL berjalan sebelum menjalankan Django
- Database `wedding_invitation_db` harus dibuat manual di phpMyAdmin