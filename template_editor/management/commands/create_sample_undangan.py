from django.core.management.base import BaseCommand
from template_editor.models import Undangan, InvitationTemplate
from datetime import datetime, time

class Command(BaseCommand):
    help = 'Create sample undangan for testing'

    def handle(self, *args, **options):
        # Create sample undangan
        undangan, created = Undangan.objects.get_or_create(
            slug='sample-undangan-test',
            defaults={
                'judul': 'Undangan Pernikahan Ahmad & Siti',
                'nama_panggilan_pria': 'Ahmad',
                'nama_panggilan_wanita': 'Siti',
                'nama_lengkap_pria': 'Ahmad Fauzi',
                'nama_lengkap_wanita': 'Siti Nurhaliza',
                'info_orang_tua_pria': 'Putra dari Bapak Hasan & Ibu Fatimah',
                'info_orang_tua_wanita': 'Putri dari Bapak Ali & Ibu Khadijah',
                'kutipan_pembuka': 'Dan di antara tanda-tanda kekuasaan-Nya ialah Dia menciptakan untukmu isteri-isteri dari jenismu sendiri, supaya kamu cenderung dan merasa tenteram kepadanya, dan dijadikan-Nya diantaramu rasa kasih dan sayang.',
                'sumber_kutipan': 'QS. Ar-Rum: 21',
                'judul_acara_1': 'Akad Nikah',
                'tanggal_waktu_acara_1': datetime(2024, 12, 31, 8, 0),
                'waktu_selesai_acara_1': time(10, 0),
                'nama_lokasi_acara_1': 'Masjid Al-Ikhlas',
                'alamat_lokasi_acara_1': 'Jl. Masjid No. 123, Jakarta Selatan',
                'judul_acara_2': 'Resepsi Pernikahan',
                'tanggal_waktu_acara_2': datetime(2024, 12, 31, 19, 0),
                'waktu_selesai_acara_2': time(22, 0),
                'nama_lokasi_acara_2': 'Gedung Serbaguna',
                'alamat_lokasi_acara_2': 'Jl. Gedung No. 456, Jakarta Selatan',
                'teks_pengantar_acara': 'Dengan memohon rahmat dan ridho Allah SWT, kami mengundang Bapak/Ibu/Saudara/i untuk hadir dalam acara pernikahan kami.',
                'is_published': False,  # Set to False for testing preview
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created sample undangan with ID: {undangan.id}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Sample undangan already exists with ID: {undangan.id}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Preview URL: http://127.0.0.1:8000/undangan/{undangan.id}/')
        )