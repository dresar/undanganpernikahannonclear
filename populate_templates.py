#!/usr/bin/env python
"""
Script untuk mengisi database dengan template undangan awal
Jalankan dengan: python populate_templates.py
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wedding_invitation_platform.settings')
django.setup()

from template_editor.models import (
    TemplateCategory, InvitationTemplate, Undangan, 
    StoryItem, GalleryPhoto, GiftAccount, GuestComment, SocialLink
)

def create_template_categories():
    """Membuat kategori template"""
    categories = [
        {'name': 'Wedding', 'description': 'Template untuk undangan pernikahan'},
        {'name': 'Birthday', 'description': 'Template untuk undangan ulang tahun'},
        {'name': 'Graduation', 'description': 'Template untuk undangan wisuda'},
        {'name': 'Anniversary', 'description': 'Template untuk undangan anniversary'},
        {'name': 'Baby Shower', 'description': 'Template untuk undangan baby shower'},
        {'name': 'Engagement', 'description': 'Template untuk undangan pertunangan'},
    ]
    
    for cat_data in categories:
        category, created = TemplateCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"✓ Kategori '{category.name}' berhasil dibuat")
        else:
            print(f"- Kategori '{category.name}' sudah ada")

def create_wedding_template():
    """Membuat template undangan pernikahan romantis"""
    wedding_category = TemplateCategory.objects.get(name='Wedding')
    
    html_content = '''<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ undangan.nama_panggilan_pria }} & {{ undangan.nama_panggilan_wanita }} - Wedding Invitation</title>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .invitation-container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .header {
            text-align: center;
            padding: 60px 40px;
            background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(254,207,239,0.3));
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="2" fill="%23ff9a9e" opacity="0.1"/></svg>') repeat;
            animation: float 20s infinite linear;
        }
        
        @keyframes float {
            0% { transform: translateY(0px) rotate(0deg); }
            100% { transform: translateY(-100px) rotate(360deg); }
        }
        
        .couple-names {
            font-family: 'Dancing Script', cursive;
            font-size: 3.5em;
            color: #d63384;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            position: relative;
            z-index: 2;
        }
        
        .wedding-date {
            font-size: 1.2em;
            color: #6c757d;
            margin-bottom: 30px;
            position: relative;
            z-index: 2;
        }
        
        .ornament {
            width: 100px;
            height: 2px;
            background: linear-gradient(90deg, transparent, #d63384, transparent);
            margin: 20px auto;
            position: relative;
        }
        
        .ornament::before,
        .ornament::after {
            content: '♥';
            position: absolute;
            top: -8px;
            color: #d63384;
            font-size: 1.2em;
        }
        
        .ornament::before {
            left: -15px;
        }
        
        .ornament::after {
            right: -15px;
        }
        
        .quote-section {
            padding: 40px;
            text-align: center;
            background: rgba(255,255,255,0.8);
        }
        
        .quote {
            font-style: italic;
            font-size: 1.1em;
            color: #495057;
            margin-bottom: 10px;
            line-height: 1.6;
        }
        
        .quote-source {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .event-details {
            padding: 50px 40px;
            background: linear-gradient(135deg, rgba(254,207,239,0.3), rgba(255,255,255,0.9));
        }
        
        .event-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .event-card:hover {
            transform: translateY(-5px);
        }
        
        .event-title {
            font-size: 1.5em;
            color: #d63384;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .event-date {
            font-size: 1.2em;
            color: #495057;
            margin-bottom: 10px;
            font-weight: 500;
        }
        
        .event-venue {
            color: #6c757d;
            margin-bottom: 15px;
            line-height: 1.5;
        }
        
        .map-btn {
            background: linear-gradient(45deg, #d63384, #ff6b9d);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            font-size: 0.9em;
        }
        
        .map-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(214,51,132,0.3);
        }
        
        .rsvp-section {
            padding: 50px 40px;
            text-align: center;
            background: rgba(255,255,255,0.9);
        }
        
        .rsvp-title {
            font-size: 2em;
            color: #d63384;
            margin-bottom: 20px;
            font-family: 'Dancing Script', cursive;
        }
        
        .rsvp-form {
            max-width: 400px;
            margin: 0 auto;
        }
        
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #495057;
            font-weight: 500;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s ease;
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #d63384;
        }
        
        .submit-btn {
            background: linear-gradient(45deg, #d63384, #ff6b9d);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(214,51,132,0.3);
        }
        
        .footer {
            padding: 40px;
            text-align: center;
            background: linear-gradient(135deg, #d63384, #ff6b9d);
            color: white;
        }
        
        .footer-text {
            font-size: 1.1em;
            margin-bottom: 20px;
        }
        
        .social-links {
            display: flex;
            justify-content: center;
            gap: 20px;
        }
        
        .social-link {
            color: white;
            font-size: 1.5em;
            transition: transform 0.3s ease;
        }
        
        .social-link:hover {
            transform: scale(1.2);
        }
        
        .music-control {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #d63384;
            color: white;
            border: none;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            font-size: 1.5em;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(214,51,132,0.3);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .music-control:hover {
            transform: scale(1.1);
        }
        
        @media (max-width: 768px) {
            .invitation-container {
                margin: 0;
            }
            
            .header {
                padding: 40px 20px;
            }
            
            .couple-names {
                font-size: 2.5em;
            }
            
            .event-details,
            .rsvp-section {
                padding: 30px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="invitation-container">
        <!-- Header Section -->
        <div class="header">
            <h1 class="couple-names">{{ undangan.nama_panggilan_pria }} & {{ undangan.nama_panggilan_wanita }}</h1>
            <div class="ornament"></div>
            <p class="wedding-date">{% if undangan.tanggal_waktu_acara_2 %}{{ undangan.tanggal_waktu_acara_2|date:"d F Y" }}{% endif %}</p>
        </div>
        
        <!-- Quote Section -->
        <div class="quote-section">
            <p class="quote">"{{ undangan.kutipan_pembuka|default:"Dan di antara tanda-tanda kekuasaan-Nya ialah Dia menciptakan untukmu isteri-isteri dari jenismu sendiri, supaya kamu cenderung dan merasa tenteram kepadanya, dan dijadikan-Nya diantaramu rasa kasih dan sayang." }}"</p>
            <p class="quote-source">{{ undangan.sumber_kutipan|default:"QS. Ar-Rum: 21" }}</p>
        </div>
        
        <!-- Event Details -->
        <div class="event-details">
            {% if undangan.judul_acara_1 %}
            <div class="event-card">
                <h3 class="event-title">{{ undangan.judul_acara_1 }}</h3>
                {% if undangan.tanggal_waktu_acara_1 %}
                <p class="event-date">{{ undangan.tanggal_waktu_acara_1|date:"l, d F Y" }}</p>
                <p class="event-date">{{ undangan.tanggal_waktu_acara_1|date:"H:i" }} WIB</p>
                {% endif %}
                <div class="event-venue">
                    {% if undangan.nama_lokasi_acara_1 %}<p><strong>{{ undangan.nama_lokasi_acara_1 }}</strong></p>{% endif %}
                    {% if undangan.alamat_lokasi_acara_1 %}<p>{{ undangan.alamat_lokasi_acara_1 }}</p>{% endif %}
                </div>
                {% if undangan.link_gmaps_acara_1 %}
                <a href="{{ undangan.link_gmaps_acara_1 }}" class="map-btn" target="_blank">
                    <i class="fas fa-map-marker-alt"></i> Lihat Lokasi
                </a>
                {% endif %}
            </div>
            {% endif %}
            
            {% if undangan.judul_acara_2 %}
            <div class="event-card">
                <h3 class="event-title">{{ undangan.judul_acara_2 }}</h3>
                {% if undangan.tanggal_waktu_acara_2 %}
                <p class="event-date">{{ undangan.tanggal_waktu_acara_2|date:"l, d F Y" }}</p>
                <p class="event-date">{{ undangan.tanggal_waktu_acara_2|date:"H:i" }} WIB</p>
                {% endif %}
                <div class="event-venue">
                    {% if undangan.nama_lokasi_acara_2 %}<p><strong>{{ undangan.nama_lokasi_acara_2 }}</strong></p>{% endif %}
                    {% if undangan.alamat_lokasi_acara_2 %}<p>{{ undangan.alamat_lokasi_acara_2 }}</p>{% endif %}
                </div>
                {% if undangan.link_gmaps_acara_2 %}
                <a href="{{ undangan.link_gmaps_acara_2 }}" class="map-btn" target="_blank">
                    <i class="fas fa-map-marker-alt"></i> Lihat Lokasi
                </a>
                {% endif %}
            </div>
            {% endif %}
        </div>
        
        <!-- RSVP Section -->
        <div class="rsvp-section">
            <h2 class="rsvp-title">Konfirmasi Kehadiran</h2>
            <form class="rsvp-form" id="rsvpForm">
                <div class="form-group">
                    <label for="guestName">Nama Lengkap</label>
                    <input type="text" id="guestName" name="guestName" required>
                </div>
                
                <div class="form-group">
                    <label for="attendance">Kehadiran</label>
                    <select id="attendance" name="attendance" required>
                        <option value="">Pilih kehadiran</option>
                        <option value="Hadir">Hadir</option>
                        <option value="Tidak Hadir">Tidak Hadir</option>
                        <option value="Belum Pasti">Belum Pasti</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="message">Ucapan & Doa</label>
                    <textarea id="message" name="message" rows="4" placeholder="Tuliskan ucapan dan doa untuk kedua mempelai..."></textarea>
                </div>
                
                <button type="submit" class="submit-btn">
                    <i class="fas fa-heart"></i> Kirim Konfirmasi
                </button>
            </form>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p class="footer-text">Terima kasih atas doa dan kehadiran Anda</p>
            <div class="social-links">
                {% for social in undangan.social_links.all %}
                <a href="{{ social.url_profil }}" class="social-link" target="_blank">
                    <i class="{{ social.kelas_ikon }}"></i>
                </a>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <!-- Music Control -->
    <button class="music-control" id="musicToggle">
        <i class="fas fa-music"></i>
    </button>
    
    <!-- Background Music -->
    <audio id="backgroundMusic" loop>
        {% if undangan.file_musik %}
        <source src="{{ undangan.file_musik.url }}" type="audio/mpeg">
        {% endif %}
    </audio>
    
    <script>
        // Music Control
        const musicToggle = document.getElementById('musicToggle');
        const backgroundMusic = document.getElementById('backgroundMusic');
        let isPlaying = false;
        
        musicToggle.addEventListener('click', function() {
            if (isPlaying) {
                backgroundMusic.pause();
                musicToggle.innerHTML = '<i class="fas fa-music"></i>';
                isPlaying = false;
            } else {
                backgroundMusic.play().catch(e => console.log('Audio play failed:', e));
                musicToggle.innerHTML = '<i class="fas fa-pause"></i>';
                isPlaying = true;
            }
        });
        
        // Auto-play music on first user interaction
        document.body.addEventListener('click', function() {
            if (!isPlaying) {
                backgroundMusic.play().catch(e => console.log('Audio play failed:', e));
                musicToggle.innerHTML = '<i class="fas fa-pause"></i>';
                isPlaying = true;
            }
        }, { once: true });
        
        // RSVP Form Submission
        document.getElementById('rsvpForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                nama_tamu: formData.get('guestName'),
                kehadiran: formData.get('attendance'),
                ucapan: formData.get('message')
            };
            
            // Send RSVP data to server
            fetch('/api/rsvp/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Terima kasih! Konfirmasi kehadiran Anda telah diterima.');
                    this.reset();
                } else {
                    alert('Maaf, terjadi kesalahan. Silakan coba lagi.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Maaf, terjadi kesalahan. Silakan coba lagi.');
            });
        });
        
        // Get CSRF token
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // Add entrance animation
        window.addEventListener('load', function() {
            const container = document.querySelector('.invitation-container');
            container.style.opacity = '0';
            container.style.transform = 'translateY(50px)';
            
            setTimeout(() => {
                container.style.transition = 'all 1s ease';
                container.style.opacity = '1';
                container.style.transform = 'translateY(0)';
            }, 100);
        });
    </script>
</body>
</html>'''
    
    template, created = InvitationTemplate.objects.get_or_create(
        name='Romantic Wedding',
        defaults={
            'description': 'Template undangan pernikahan dengan tema romantis dan elegan',
            'category': wedding_category,
            'html_content': html_content,
            'is_premium': False,
            'music_url': 'https://www.soundjay.com/misc/sounds/wedding-march.mp3'
        }
    )
    
    if created:
        print("✓ Template 'Romantic Wedding' berhasil dibuat")
    else:
        print("- Template 'Romantic Wedding' sudah ada")

def create_birthday_template():
    """Membuat template undangan ulang tahun"""
    birthday_category = TemplateCategory.objects.get(name='Birthday')
    
    html_content = '''<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ undangan.judul }} - Birthday Party</title>
    <link href="https://fonts.googleapis.com/css2?family=Fredoka+One:wght@400&family=Open+Sans:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Open Sans', sans-serif;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57);
            background-size: 400% 400%;
            animation: gradientShift 8s ease infinite;
            min-height: 100vh;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .party-container {
            max-width: 600px;
            margin: 20px auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .header {
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
            color: white;
            position: relative;
        }
        
        .balloons {
            position: absolute;
            top: 10px;
            left: 20px;
            font-size: 2em;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        .birthday-title {
            font-family: 'Fredoka One', cursive;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .age {
            font-size: 3em;
            font-weight: bold;
            margin: 20px 0;
        }
        
        .party-details {
            padding: 40px 30px;
            text-align: center;
        }
        
        .detail-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            border-left: 5px solid #ff6b6b;
        }
        
        .detail-title {
            font-weight: 600;
            color: #ff6b6b;
            margin-bottom: 10px;
        }
        
        .rsvp-btn {
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            transition: transform 0.3s ease;
            margin-top: 20px;
        }
        
        .rsvp-btn:hover {
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <div class="party-container">
        <div class="header">
            <div class="balloons">🎈🎈🎈</div>
            <h1 class="birthday-title">{{ undangan.judul }}</h1>
            <h2>Birthday Party!</h2>
            <div class="age">🎂</div>
        </div>
        
        <div class="party-details">
            <div class="detail-card">
                <div class="detail-title">📅 Tanggal & Waktu</div>
                {% if undangan.tanggal_waktu_acara_2 %}
                <div>{{ undangan.tanggal_waktu_acara_2|date:"l, d F Y" }}</div>
                <div>{{ undangan.tanggal_waktu_acara_2|date:"H:i" }} WIB</div>
                {% endif %}
            </div>
            
            <div class="detail-card">
                <div class="detail-title">📍 Lokasi</div>
                {% if undangan.nama_lokasi_acara_2 %}<div>{{ undangan.nama_lokasi_acara_2 }}</div>{% endif %}
                {% if undangan.alamat_lokasi_acara_2 %}<div>{{ undangan.alamat_lokasi_acara_2 }}</div>{% endif %}
            </div>
            
            <div class="detail-card">
                <div class="detail-title">🎉 Tema</div>
                <div>Fun & Colorful</div>
            </div>
            
            <button class="rsvp-btn" onclick="alert('Terima kasih! Kami tunggu kehadiran Anda!')">
                🎊 Konfirmasi Kehadiran
            </button>
        </div>
    </div>
</body>
</html>'''
    
    template, created = InvitationTemplate.objects.get_or_create(
        name='Birthday Celebration',
        defaults={
            'description': 'Template undangan ulang tahun yang ceria dan colorful',
            'category': birthday_category,
            'html_content': html_content,
            'is_premium': False
        }
    )
    
    if created:
        print("✓ Template 'Birthday Celebration' berhasil dibuat")
    else:
        print("- Template 'Birthday Celebration' sudah ada")

def create_sample_invitation():
    """Membuat contoh undangan"""
    from datetime import datetime
    
    wedding_template = InvitationTemplate.objects.get(name='Romantic Wedding')
    
    undangan, created = Undangan.objects.get_or_create(
        slug='rizky-aulia-2025',
        defaults={
            'template': wedding_template,
            'judul': 'Pernikahan Rizky & Aulia',
            'nama_panggilan_pria': 'Rizky',
            'nama_panggilan_wanita': 'Aulia',
            'nama_lengkap_pria': 'Rizky Pratama',
            'nama_lengkap_wanita': 'Aulia Putri',
            'tanggal_waktu_acara_1': datetime(2025, 6, 15, 8, 0),
            'judul_acara_1': 'Akad Nikah',
            'nama_lokasi_acara_1': 'Masjid Al-Ikhlas',
            'alamat_lokasi_acara_1': 'Jl. Contoh No. 123, Jakarta',
            'tanggal_waktu_acara_2': datetime(2025, 6, 15, 19, 0),
            'judul_acara_2': 'Resepsi Pernikahan',
            'nama_lokasi_acara_2': 'Gedung Serbaguna',
            'alamat_lokasi_acara_2': 'Jl. Contoh No. 456, Jakarta',
            'kutipan_pembuka': 'Dan di antara tanda-tanda kekuasaan-Nya ialah Dia menciptakan untukmu isteri-isteri dari jenismu sendiri, supaya kamu cenderung dan merasa tenteram kepadanya, dan dijadikan-Nya diantaramu rasa kasih dan sayang.',
            'sumber_kutipan': 'QS. Ar-Rum: 21',
            'is_published': True
        }
    )
    
    if created:
        print("✓ Contoh undangan 'Pernikahan Rizky & Aulia' berhasil dibuat")
        
        # Tambahkan story items
        story_items = [
            {
                'tanggal_kejadian': date(2022, 6, 15),
                'judul_kejadian': 'Awal Pertemuan',
                'deskripsi': 'Kami bertemu di sebuah acara komunitas dan langsung merasa cocok satu sama lain.',
                'kelas_ikon': 'fa-handshake'
            },
            {
                'tanggal_kejadian': date(2023, 2, 14),
                'judul_kejadian': 'Hari Valentine Pertama',
                'deskripsi': 'Valentine pertama kami yang tak terlupakan dengan dinner romantis.',
                'kelas_ikon': 'fa-heart'
            },
            {
                'tanggal_kejadian': date(2024, 1, 1),
                'judul_kejadian': 'Lamaran',
                'deskripsi': 'Awal tahun yang berkesan dengan lamaran di pantai saat matahari terbenam.',
                'kelas_ikon': 'fa-ring'
            }
        ]
        
        for story_data in story_items:
            StoryItem.objects.create(undangan=undangan, **story_data)
        
        print("✓ Story items berhasil ditambahkan")
        
        # Increment usage count
        wedding_template.increment_usage()
        
    else:
        print("- Contoh undangan 'Pernikahan Rizky & Aulia' sudah ada")

def main():
    """Fungsi utama untuk menjalankan semua proses"""
    print("🚀 Memulai proses populate database...\n")
    
    try:
        print("1. Membuat kategori template...")
        create_template_categories()
        print()
        
        print("2. Membuat template undangan pernikahan...")
        create_wedding_template()
        print()
        
        print("3. Membuat template undangan ulang tahun...")
        create_birthday_template()
        print()
        
        print("4. Membuat contoh undangan...")
        create_sample_invitation()
        print()
        
        print("✅ Proses populate database selesai!")
        print("\n📊 Ringkasan:")
        print(f"   - Kategori: {TemplateCategory.objects.count()}")
        print(f"   - Template: {InvitationTemplate.objects.count()}")
        print(f"   - Undangan: {Undangan.objects.count()}")
        print(f"   - Story Items: {StoryItem.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()