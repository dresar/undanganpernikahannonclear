from django.core.management.base import BaseCommand
from main.models import InvitationTemplate

class Command(BaseCommand):
    help = 'Populate database with sample invitation templates'

    def handle(self, *args, **options):
        # Template 1: Classic Elegant
        template1, created = InvitationTemplate.objects.get_or_create(
            name="Classic Elegant",
            defaults={
                'description': 'Template undangan klasik dengan desain elegan dan mewah',
                'html_content': '''<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ bride_name }} & {{ groom_name }}</title>
    <style>
        body { font-family: 'Georgia', serif; margin: 0; padding: 0; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        .container { max-width: 600px; margin: 0 auto; background: white; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 60px 20px; }
        .names { font-size: 2.5em; margin: 20px 0; font-weight: 300; }
        .date { font-size: 1.2em; margin: 10px 0; }
        .content { padding: 40px 20px; text-align: center; }
        .venue { margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 10px; }
        .gallery { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 30px 0; }
        .gallery img { width: 100%; height: 150px; object-fit: cover; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Wedding Invitation</h1>
            <div class="names">{{ bride_name }} & {{ groom_name }}</div>
            <div class="date">{{ wedding_date }}</div>
        </div>
        <div class="content">
            <p>Dengan penuh sukacita, kami mengundang Anda untuk hadir dalam perayaan pernikahan kami.</p>
            <div class="venue">
                <h3>Akad Nikah</h3>
                <p><strong>Tanggal:</strong> {{ wedding_date }}</p>
                <p><strong>Waktu:</strong> {{ wedding_time }}</p>
                <p><strong>Tempat:</strong> {{ wedding_venue }}</p>
            </div>
            {% if reception_venue %}
            <div class="venue">
                <h3>Resepsi</h3>
                <p><strong>Tanggal:</strong> {{ reception_date }}</p>
                <p><strong>Waktu:</strong> {{ reception_time }}</p>
                <p><strong>Tempat:</strong> {{ reception_venue }}</p>
            </div>
            {% endif %}
            {% if gallery_images %}
            <div class="gallery">
                {% for image in gallery_images %}
                <img src="{{ image }}" alt="Gallery">
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>''',
                'css_content': '',
                'js_content': '',
                'is_active': True
            }
        )
        
        # Template 2: Modern Minimalist
        template2, created = InvitationTemplate.objects.get_or_create(
            name="Modern Minimalist",
            defaults={
                'description': 'Template modern dengan desain minimalis dan clean',
                'html_content': '''<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ bride_name }} & {{ groom_name }}</title>
    <style>
        body { font-family: 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 0; background: #f8f9fa; }
        .container { max-width: 500px; margin: 0 auto; background: white; }
        .header { padding: 80px 40px; text-align: center; border-bottom: 1px solid #eee; }
        .names { font-size: 2em; margin: 20px 0; font-weight: 100; color: #333; }
        .ampersand { font-size: 1.5em; color: #999; margin: 0 10px; }
        .date { font-size: 1em; color: #666; margin: 20px 0; }
        .content { padding: 40px; }
        .event { margin: 30px 0; padding: 20px 0; border-bottom: 1px solid #f0f0f0; }
        .event:last-child { border-bottom: none; }
        .event h3 { margin: 0 0 15px 0; font-weight: 300; color: #333; }
        .event p { margin: 5px 0; color: #666; }
        .gallery { display: flex; flex-wrap: wrap; gap: 10px; margin: 30px 0; }
        .gallery img { width: calc(50% - 5px); height: 120px; object-fit: cover; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="names">
                {{ bride_name }}<span class="ampersand">&</span>{{ groom_name }}
            </div>
            <div class="date">{{ wedding_date }}</div>
        </div>
        <div class="content">
            <div class="event">
                <h3>Akad Nikah</h3>
                <p>{{ wedding_date }} • {{ wedding_time }}</p>
                <p>{{ wedding_venue }}</p>
            </div>
            {% if reception_venue %}
            <div class="event">
                <h3>Resepsi</h3>
                <p>{{ reception_date }} • {{ reception_time }}</p>
                <p>{{ reception_venue }}</p>
            </div>
            {% endif %}
            {% if gallery_images %}
            <div class="gallery">
                {% for image in gallery_images %}
                <img src="{{ image }}" alt="Gallery">
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>''',
                'css_content': '',
                'js_content': '',
                'is_active': True
            }
        )
        
        # Template 3: Floral Garden
        template3, created = InvitationTemplate.objects.get_or_create(
            name="Floral Garden",
            defaults={
                'description': 'Template dengan tema bunga dan taman yang romantis',
                'html_content': '''<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ bride_name }} & {{ groom_name }}</title>
    <style>
        body { font-family: 'Times New Roman', serif; margin: 0; padding: 0; background: linear-gradient(45deg, #ffeef8 0%, #f0f8e8 100%); }
        .container { max-width: 600px; margin: 0 auto; background: white; border: 2px solid #e8f5e8; }
        .header { background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="2" fill="%23ff69b4" opacity="0.3"/></svg>'); padding: 60px 20px; text-align: center; position: relative; }
        .header::before { content: '🌸'; position: absolute; top: 20px; left: 20px; font-size: 2em; }
        .header::after { content: '🌸'; position: absolute; top: 20px; right: 20px; font-size: 2em; }
        .names { font-size: 2.2em; margin: 20px 0; color: #2d5a27; font-style: italic; }
        .date { font-size: 1.1em; color: #5a7c76; margin: 15px 0; }
        .content { padding: 40px 30px; }
        .verse { font-style: italic; text-align: center; margin: 30px 0; color: #666; border-left: 3px solid #ff69b4; padding-left: 20px; }
        .event { margin: 30px 0; padding: 25px; background: linear-gradient(135deg, #f8fff8 0%, #fff0f8 100%); border-radius: 15px; border: 1px solid #e8f5e8; }
        .event h3 { margin: 0 0 15px 0; color: #2d5a27; }
        .gallery { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 30px 0; }
        .gallery img { width: 100%; height: 120px; object-fit: cover; border-radius: 10px; border: 2px solid #e8f5e8; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="color: #2d5a27; margin: 0;">Wedding Invitation</h1>
            <div class="names">{{ bride_name }} & {{ groom_name }}</div>
            <div class="date">{{ wedding_date }}</div>
        </div>
        <div class="content">
            <div class="verse">
                "Dan di antara tanda-tanda kekuasaan-Nya ialah Dia menciptakan untukmu isteri-isteri dari jenismu sendiri, supaya kamu cenderung dan merasa tenteram kepadanya, dan dijadikan-Nya diantaramu rasa kasih dan sayang."<br>
                <small>- QS. Ar-Rum: 21</small>
            </div>
            <div class="event">
                <h3>🌹 Akad Nikah</h3>
                <p><strong>Tanggal:</strong> {{ wedding_date }}</p>
                <p><strong>Waktu:</strong> {{ wedding_time }}</p>
                <p><strong>Tempat:</strong> {{ wedding_venue }}</p>
            </div>
            {% if reception_venue %}
            <div class="event">
                <h3>🌺 Resepsi</h3>
                <p><strong>Tanggal:</strong> {{ reception_date }}</p>
                <p><strong>Waktu:</strong> {{ reception_time }}</p>
                <p><strong>Tempat:</strong> {{ reception_venue }}</p>
            </div>
            {% endif %}
            {% if gallery_images %}
            <div class="gallery">
                {% for image in gallery_images %}
                <img src="{{ image }}" alt="Gallery">
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>''',
                'css_content': '',
                'js_content': '',
                'is_active': True
            }
        )
        
        # Template 4: Luxury Gold
        template4, created = InvitationTemplate.objects.get_or_create(
            name="Luxury Gold",
            defaults={
                'description': 'Template mewah dengan aksen emas dan desain premium',
                'html_content': '''<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ bride_name }} & {{ groom_name }}</title>
    <style>
        body { font-family: 'Playfair Display', serif; margin: 0; padding: 0; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); }
        .container { max-width: 650px; margin: 0 auto; background: linear-gradient(135deg, #000 0%, #1a1a1a 100%); color: #fff; border: 3px solid #ffd700; }
        .header { padding: 80px 40px; text-align: center; background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%); color: #000; position: relative; }
        .header::before { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><polygon points="50,10 60,40 90,40 70,60 80,90 50,75 20,90 30,60 10,40 40,40" fill="%23ffd700" opacity="0.1"/></svg>') repeat; }
        .names { font-size: 2.8em; margin: 25px 0; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); position: relative; z-index: 1; }
        .date { font-size: 1.3em; margin: 15px 0; position: relative; z-index: 1; }
        .content { padding: 50px 40px; }
        .intro { text-align: center; font-size: 1.1em; margin: 30px 0; color: #ffd700; }
        .event { margin: 40px 0; padding: 30px; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); border: 2px solid #ffd700; border-radius: 10px; }
        .event h3 { margin: 0 0 20px 0; color: #ffd700; font-size: 1.5em; text-align: center; }
        .event p { margin: 10px 0; font-size: 1.1em; }
        .gallery { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 40px 0; }
        .gallery img { width: 100%; height: 180px; object-fit: cover; border-radius: 10px; border: 3px solid #ffd700; }
        .footer { text-align: center; padding: 30px; background: #ffd700; color: #000; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0; font-size: 1.5em;">THE WEDDING OF</h1>
            <div class="names">{{ bride_name }} & {{ groom_name }}</div>
            <div class="date">{{ wedding_date }}</div>
        </div>
        <div class="content">
            <div class="intro">
                Dengan memohon rahmat dan ridho Allah SWT, kami bermaksud menyelenggarakan pernikahan putra-putri kami.
            </div>
            <div class="event">
                <h3>✨ AKAD NIKAH ✨</h3>
                <p><strong>Tanggal:</strong> {{ wedding_date }}</p>
                <p><strong>Waktu:</strong> {{ wedding_time }}</p>
                <p><strong>Tempat:</strong> {{ wedding_venue }}</p>
            </div>
            {% if reception_venue %}
            <div class="event">
                <h3>🎉 RESEPSI 🎉</h3>
                <p><strong>Tanggal:</strong> {{ reception_date }}</p>
                <p><strong>Waktu:</strong> {{ reception_time }}</p>
                <p><strong>Tempat:</strong> {{ reception_venue }}</p>
            </div>
            {% endif %}
            {% if gallery_images %}
            <div class="gallery">
                {% for image in gallery_images %}
                <img src="{{ image }}" alt="Gallery">
                {% endfor %}
            </div>
            {% endif %}
        </div>
        <div class="footer">
            Merupakan suatu kehormatan dan kebahagiaan bagi kami apabila Bapak/Ibu/Saudara/i berkenan hadir untuk memberikan doa restu.
        </div>
    </div>
</body>
</html>''',
                'css_content': '',
                'js_content': '',
                'is_active': True
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with 4 invitation templates')
        )