#!/usr/bin/env python
"""
Management command untuk menambahkan template Elegant Wedding ke database
Jalankan dengan: python manage.py add_elegant_wedding_template
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from template_editor.models import InvitationTemplate, TemplateCategory

class Command(BaseCommand):
    help = 'Add Elegant Wedding template to database'
    
    def handle(self, *args, **options):
        # Path ke file template
        template_path = os.path.join(
            settings.BASE_DIR, 
            'template_editor', 
            'templates', 
            'wedding', 
            'elegant_wedding.html'
        )
        
        try:
            # Baca konten HTML dari file
            with open(template_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            # Cek apakah template sudah ada
            existing_template = InvitationTemplate.objects.filter(
                name='Elegant Wedding'
            ).first()
            
            if existing_template:
                self.stdout.write(
                    self.style.WARNING('Template "Elegant Wedding" sudah ada di database.')
                )
                # Update konten HTML jika berbeda
                if existing_template.html_content != html_content:
                    existing_template.html_content = html_content
                    existing_template.save()
                    self.stdout.write(
                        self.style.SUCCESS('Konten template berhasil diperbarui!')
                    )
                return
            
            # Cari atau buat kategori Wedding
            wedding_category, created = TemplateCategory.objects.get_or_create(
                name='Wedding',
                defaults={
                    'slug': 'wedding',
                    'description': 'Template undangan pernikahan',
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS('Kategori "Wedding" berhasil dibuat.')
                )
            
            # Buat template baru
            template = InvitationTemplate.objects.create(
                name='Elegant Wedding',
                description='Template undangan pernikahan yang elegan dengan desain modern, gradient background, dan animasi yang menarik. Dilengkapi dengan section untuk foto mempelai, kisah cinta, detail acara, galeri foto, dan amplop digital.',
                category=wedding_category,
                html_content=html_content,
                is_premium=False,
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Template "Elegant Wedding" berhasil ditambahkan ke database dengan ID: {template.id}'
                )
            )
            
            # Informasi tambahan
            self.stdout.write('\nInformasi Template:')
            self.stdout.write(f'- Nama: {template.name}')
            self.stdout.write(f'- Kategori: {template.category.name}')
            self.stdout.write(f'- Status: {"Aktif" if template.is_active else "Tidak Aktif"}')
            self.stdout.write(f'- Premium: {"Ya" if template.is_premium else "Tidak"}')
            self.stdout.write(f'- Lokasi file: {template_path}')
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    f'File template tidak ditemukan di: {template_path}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error saat menambahkan template: {str(e)}'
                )
            )