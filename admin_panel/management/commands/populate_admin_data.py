from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from admin_panel.models import (
    AdminProfile, SystemSettings, TemplateCategory, TemplateTag,
    AIPromptTemplate, CustomerFeedback, EmailTemplate, PaymentMethod,
    Discount, NotificationTemplate, ContentBlock, MediaLibrary
)
from main.models import InvitationTemplate, Order
from template_editor.models import (
    TemplateCategory as EditorTemplateCategory,
    TemplateTag as EditorTemplateTag,
    ColorPalette, FontFamily, TemplateLayout, TemplateStyle
)
import json
from datetime import datetime, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate admin panel with default data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing data before populating',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting existing data...')
            self.reset_data()

        self.stdout.write('Populating admin panel data...')
        
        with transaction.atomic():
            self.create_admin_users()
            self.create_system_settings()
            self.create_template_categories()
            self.create_template_tags()
            self.create_ai_prompt_templates()
            self.create_sample_feedback()
            self.create_sample_templates()
            self.sync_with_template_editor()

        self.stdout.write(
            self.style.SUCCESS('Successfully populated admin panel data')
        )

    def reset_data(self):
        """Reset existing data"""
        models_to_reset = [
            SystemSettings, TemplateCategory, TemplateTag,
            AIPromptTemplate, CustomerFeedback, EmailTemplate,
            PaymentMethod, Discount, NotificationTemplate, ContentBlock
        ]
        
        for model in models_to_reset:
            model.objects.all().delete()
            self.stdout.write(f'Cleared {model.__name__}')

    def create_admin_users(self):
        """Create admin users and profiles"""
        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            
            AdminProfile.objects.create(
                user=admin_user,
                phone='+62812345678',
                department='IT',
                bio='System Administrator',
                is_super_admin=True
            )
            self.stdout.write('Created admin user')

        # Create staff user
        if not User.objects.filter(username='staff').exists():
            staff_user = User.objects.create_user(
                username='staff',
                email='staff@example.com',
                password='staff123',
                first_name='Staff',
                last_name='User',
                is_staff=True
            )
            
            AdminProfile.objects.create(
                user=staff_user,
                phone='+62812345679',
                department='Customer Service',
                bio='Customer Service Representative'
            )
            self.stdout.write('Created staff user')

    def create_system_settings(self):
        """Create system settings"""
        settings_data = [
            {
                'key': 'site_name',
                'value': 'Wedding Invitation Platform',
                'setting_type': 'text',
                'description': 'Name of the website',
                'category': 'general',
                'is_public': True
            },
            {
                'key': 'site_description',
                'value': 'Platform untuk membuat undangan pernikahan digital',
                'setting_type': 'text',
                'description': 'Site description for SEO',
                'category': 'general',
                'is_public': True
            },
            {
                'key': 'contact_email',
                'value': 'contact@weddingplatform.com',
                'setting_type': 'email',
                'description': 'Contact email address',
                'category': 'contact',
                'is_public': True
            },
            {
                'key': 'contact_phone',
                'value': '+62812345678',
                'setting_type': 'text',
                'description': 'Contact phone number',
                'category': 'contact',
                'is_public': True
            },
            {
                'key': 'max_upload_size',
                'value': '10485760',
                'setting_type': 'number',
                'description': 'Maximum upload size in bytes (10MB)',
                'category': 'upload'
            },
            {
                'key': 'allowed_file_types',
                'value': json.dumps(['jpg', 'jpeg', 'png', 'gif', 'pdf']),
                'setting_type': 'json',
                'description': 'Allowed file types for upload',
                'category': 'upload'
            },
            {
                'key': 'enable_ai_features',
                'value': 'true',
                'setting_type': 'boolean',
                'description': 'Enable AI content generation features',
                'category': 'ai'
            },
            {
                'key': 'default_template_price',
                'value': '50000',
                'setting_type': 'number',
                'description': 'Default price for templates in IDR',
                'category': 'pricing'
            },
            {
                'key': 'currency',
                'value': 'IDR',
                'setting_type': 'text',
                'description': 'Default currency',
                'category': 'pricing',
                'is_public': True
            },
            {
                'key': 'maintenance_mode',
                'value': 'false',
                'setting_type': 'boolean',
                'description': 'Enable maintenance mode',
                'category': 'system'
            }
        ]

        for setting_data in settings_data:
            SystemSettings.objects.get_or_create(
                key=setting_data['key'],
                defaults=setting_data
            )
        
        self.stdout.write('Created system settings')

    def create_template_categories(self):
        """Create template categories"""
        categories_data = [
            {
                'name': 'Modern',
                'slug': 'modern',
                'description': 'Template modern dengan desain minimalis',
                'icon': 'fas fa-star',
                'color': '#3B82F6',
                'sort_order': 1
            },
            {
                'name': 'Classic',
                'slug': 'classic',
                'description': 'Template klasik dengan sentuhan elegan',
                'icon': 'fas fa-crown',
                'color': '#8B5CF6',
                'sort_order': 2
            },
            {
                'name': 'Floral',
                'slug': 'floral',
                'description': 'Template dengan motif bunga dan alam',
                'icon': 'fas fa-leaf',
                'color': '#10B981',
                'sort_order': 3
            },
            {
                'name': 'Luxury',
                'slug': 'luxury',
                'description': 'Template mewah dengan detail premium',
                'icon': 'fas fa-gem',
                'color': '#F59E0B',
                'sort_order': 4
            },
            {
                'name': 'Simple',
                'slug': 'simple',
                'description': 'Template sederhana dan mudah dibaca',
                'icon': 'fas fa-circle',
                'color': '#6B7280',
                'sort_order': 5
            }
        ]

        for category_data in categories_data:
            TemplateCategory.objects.get_or_create(
                slug=category_data['slug'],
                defaults=category_data
            )
        
        self.stdout.write('Created template categories')

    def create_template_tags(self):
        """Create template tags"""
        tags_data = [
            {'name': 'Popular', 'slug': 'popular', 'color': '#EF4444'},
            {'name': 'New', 'slug': 'new', 'color': '#10B981'},
            {'name': 'Premium', 'slug': 'premium', 'color': '#F59E0B'},
            {'name': 'Free', 'slug': 'free', 'color': '#3B82F6'},
            {'name': 'Animated', 'slug': 'animated', 'color': '#8B5CF6'},
            {'name': 'Interactive', 'slug': 'interactive', 'color': '#EC4899'},
            {'name': 'Responsive', 'slug': 'responsive', 'color': '#06B6D4'},
            {'name': 'Customizable', 'slug': 'customizable', 'color': '#84CC16'}
        ]

        for tag_data in tags_data:
            TemplateTag.objects.get_or_create(
                slug=tag_data['slug'],
                defaults=tag_data
            )
        
        self.stdout.write('Created template tags')

    def create_ai_prompt_templates(self):
        """Create AI prompt templates"""
        prompts_data = [
            {
                'name': 'Generate Wedding Template',
                'prompt_type': 'template_generation',
                'prompt_text': 'Create a beautiful wedding invitation template with {theme} theme, using {color_scheme} colors. Include sections for {sections}. Make it {style} and suitable for {occasion}.',
                'variables': ['theme', 'color_scheme', 'sections', 'style', 'occasion'],
                'description': 'Generate complete wedding invitation template'
            },
            {
                'name': 'Improve Template Design',
                'prompt_type': 'design_improvement',
                'prompt_text': 'Improve this wedding template design by enhancing {aspects}. Focus on {priorities} while maintaining {constraints}.',
                'variables': ['aspects', 'priorities', 'constraints'],
                'description': 'Improve existing template design'
            },
            {
                'name': 'Generate Color Scheme',
                'prompt_type': 'color_scheme',
                'prompt_text': 'Create a harmonious color palette for a {theme} wedding invitation. Include primary, secondary, and accent colors that work well with {mood} atmosphere.',
                'variables': ['theme', 'mood'],
                'description': 'Generate color schemes for templates'
            },
            {
                'name': 'Content Suggestions',
                'prompt_type': 'content_suggestion',
                'prompt_text': 'Suggest appropriate content for a {type} wedding invitation including {elements}. Make it {tone} and culturally appropriate for {culture}.',
                'variables': ['type', 'elements', 'tone', 'culture'],
                'description': 'Suggest content for invitations'
            }
        ]

        for prompt_data in prompts_data:
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                prompt_data['created_by'] = admin_user
                AIPromptTemplate.objects.get_or_create(
                    name=prompt_data['name'],
                    defaults=prompt_data
                )
        
        self.stdout.write('Created AI prompt templates')

    def create_sample_feedback(self):
        """Create sample customer feedback"""
        feedback_data = [
            {
                'customer_name': 'Andi Wijaya',
                'customer_email': 'andi@example.com',
                'subject': 'Template sangat bagus!',
                'message': 'Saya sangat puas dengan template yang disediakan. Desainnya modern dan mudah dikustomisasi.',
                'rating': 5,
                'feedback_type': 'compliment'
            },
            {
                'customer_name': 'Sari Dewi',
                'customer_email': 'sari@example.com',
                'subject': 'Saran untuk template floral',
                'message': 'Template floral sudah bagus, tapi mungkin bisa ditambahkan lebih banyak variasi warna.',
                'rating': 4,
                'feedback_type': 'suggestion'
            },
            {
                'customer_name': 'Budi Santoso',
                'customer_email': 'budi@example.com',
                'subject': 'Masalah loading template',
                'message': 'Template kadang loading lama saat dibuka di mobile. Mohon diperbaiki.',
                'rating': 3,
                'feedback_type': 'complaint'
            }
        ]

        for feedback in feedback_data:
            CustomerFeedback.objects.get_or_create(
                customer_email=feedback['customer_email'],
                subject=feedback['subject'],
                defaults=feedback
            )
        
        self.stdout.write('Created sample feedback')











    def create_sample_orders(self):
        """Create sample orders for testing"""
        # This will be implemented when we have proper template data
        self.stdout.write('Sample orders will be created after templates')

    def create_sample_templates(self):
        """Create sample invitation templates"""
        self.stdout.write('Creating sample templates...')
        
        sample_templates = [
            {
                'name': 'Classic Elegant',
                'description': 'A timeless and elegant wedding invitation template',
                'html_content': '''
                <div style="font-family: 'Georgia', serif; max-width: 600px; margin: 0 auto; padding: 40px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 15px;">
                    <div style="text-align: center; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                        <h1 style="color: #8b5a3c; font-size: 2.5em; margin-bottom: 10px; font-weight: 300;">{{ bride_name }} & {{ groom_name }}</h1>
                        <p style="color: #666; font-size: 1.2em; margin-bottom: 30px;">Together with their families</p>
                        <h2 style="color: #8b5a3c; font-size: 1.8em; margin-bottom: 20px;">Request the pleasure of your company</h2>
                        <p style="color: #666; font-size: 1.1em; margin-bottom: 30px;">at the celebration of their marriage</p>
                        <div style="border-top: 2px solid #8b5a3c; border-bottom: 2px solid #8b5a3c; padding: 20px; margin: 30px 0;">
                            <p style="color: #8b5a3c; font-size: 1.3em; margin: 5px 0;"><strong>{{ wedding_date }}</strong></p>
                            <p style="color: #666; margin: 5px 0;">{{ wedding_time }}</p>
                            <p style="color: #666; margin: 5px 0;">{{ venue_name }}</p>
                            <p style="color: #666; margin: 5px 0;">{{ venue_address }}</p>
                        </div>
                        <p style="color: #8b5a3c; font-style: italic;">RSVP by {{ rsvp_date }}</p>
                    </div>
                </div>
                ''',
                'is_active': True,
                'is_featured': True
            },
            {
                'name': 'Modern Minimalist',
                'description': 'Clean and modern wedding invitation design',
                'html_content': '''
                <div style="font-family: 'Helvetica', sans-serif; max-width: 600px; margin: 0 auto; padding: 40px; background: #f8f9fa;">
                    <div style="background: white; padding: 60px 40px; text-align: center; border-radius: 5px; box-shadow: 0 5px 15px rgba(0,0,0,0.08);">
                        <h1 style="color: #2c3e50; font-size: 2.2em; font-weight: 100; letter-spacing: 3px; margin-bottom: 40px;">{{ bride_name }} <span style="font-weight: 300;">&</span> {{ groom_name }}</h1>
                        <div style="width: 60px; height: 1px; background: #3498db; margin: 0 auto 40px;"></div>
                        <h2 style="color: #34495e; font-size: 1.4em; font-weight: 300; margin-bottom: 30px;">ARE GETTING MARRIED</h2>
                        <div style="background: #ecf0f1; padding: 30px; margin: 40px 0; border-left: 4px solid #3498db;">
                            <p style="color: #2c3e50; font-size: 1.2em; margin: 10px 0; font-weight: 500;">{{ wedding_date }}</p>
                            <p style="color: #7f8c8d; margin: 10px 0;">{{ wedding_time }}</p>
                            <p style="color: #7f8c8d; margin: 10px 0;">{{ venue_name }}</p>
                            <p style="color: #7f8c8d; margin: 10px 0;">{{ venue_address }}</p>
                        </div>
                        <p style="color: #95a5a6; font-size: 0.9em; letter-spacing: 1px;">PLEASE RSVP BY {{ rsvp_date }}</p>
                    </div>
                </div>
                ''',
                'is_active': True,
                'is_featured': True
            }
        ]
        
        for template_data in sample_templates:
            InvitationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            
        self.stdout.write(f'Created {len(sample_templates)} sample templates')

    def sync_with_template_editor(self):
        """Sync data with template editor"""
        # Sync categories
        admin_categories = TemplateCategory.objects.all()
        for admin_cat in admin_categories:
            EditorTemplateCategory.objects.get_or_create(
                slug=admin_cat.slug,
                defaults={
                    'name': admin_cat.name,
                    'description': admin_cat.description,
                    'is_active': admin_cat.is_active
                }
            )

        # Sync tags
        admin_tags = TemplateTag.objects.all()
        for admin_tag in admin_tags:
            EditorTemplateTag.objects.get_or_create(
                slug=admin_tag.slug,
                defaults={
                    'name': admin_tag.name,
                    'color': admin_tag.color
                }
            )

        self.stdout.write('Synced data with template editor')