from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.core.cache import cache
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from django.db.models import F
from django.middleware.csrf import get_token

import json
import uuid
import os
import logging
import base64
import io
from PIL import Image
import zipfile
import tempfile
from datetime import datetime, timedelta
import requests
# import sqlite3  # Commented out for MySQL migration
import csv
import pandas as pd
from typing import Dict, List, Any, Optional

# Import models
from .models import (
    Template, TemplateCategory, TemplateTag, TemplateStyle, TemplateLayout,
    TemplateComponent, ColorPalette, FontFamily, TemplateVersion,
    TemplateCustomization, AIPromptTemplate, EditorTool, DatabaseConnection,
    TemplateDataBinding, TemplateExport
)

# Import admin panel models for integration
from admin_panel.models import (
    AdminProfile, SystemSettings, ActivityLog, AIGenerationHistory,
    Analytics, MediaLibrary
)

# Import main app models
from .models import InvitationTemplate, Undangan, StoryItem, GalleryPhoto, GiftAccount, GuestComment, SocialLink
from main.models import Order

# Import forms
try:
    from .forms import UndanganForm, StoryItemForm, GalleryPhotoForm, GiftAccountForm
except ImportError:
    # Forms will be created later
    pass

logger = logging.getLogger(__name__)

# Helper functions
def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.is_superuser or hasattr(user, 'adminprofile'))

def log_activity(user, action, description, template_id=None):
    """Log admin activity"""
    try:
        ActivityLog.objects.create(
            admin=user,
            action=action,
            description=description,
            ip_address='127.0.0.1',  # You can get real IP from request
            template_id=template_id
        )
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")

def get_system_setting(key, default=None):
    """Get system setting value"""
    try:
        setting = SystemSettings.objects.get(key=key)
        return setting.get_value()
    except SystemSettings.DoesNotExist:
        return default

# Main Editor Views
@login_required
def editor_dashboard(request):
    """Main editor dashboard integrated with admin panel"""
    if not is_admin(request.user):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_panel:login')
    
    # Get dashboard data
    templates = Template.objects.filter(is_active=True).order_by('-created_at')[:10]
    categories = TemplateCategory.objects.filter(is_active=True).order_by('sort_order')
    tags = TemplateTag.objects.filter(is_featured=True).order_by('-usage_count')[:20]
    
    # Get editor tools
    editor_tools = EditorTool.objects.filter(is_active=True).order_by('sort_order')
    
    # Get recent activity
    recent_activity = ActivityLog.objects.filter(
        action__in=['template_created', 'template_updated', 'template_published']
    ).order_by('-created_at')[:10]
    
    # Get statistics
    stats = {
        'total_templates': Template.objects.count(),
        'published_templates': Template.objects.filter(is_published=True).count(),
        'draft_templates': Template.objects.filter(is_published=False).count(),
        'total_downloads': Template.objects.aggregate(total=models.Sum('download_count'))['total'] or 0,
        'total_views': Template.objects.aggregate(total=models.Sum('view_count'))['total'] or 0,
    }
    
    # Get database connections
    db_connections = DatabaseConnection.objects.filter(is_active=True)
    
    context = {
        'templates': templates,
        'categories': categories,
        'tags': tags,
        'editor_tools': editor_tools,
        'recent_activity': recent_activity,
        'stats': stats,
        'db_connections': db_connections,
        'page_title': 'Template Editor Dashboard',
    }
    
    log_activity(request.user, 'dashboard_accessed', 'Accessed template editor dashboard')
    
    return render(request, 'template_editor/dashboard.html', context)

@login_required
def template_editor(request, template_id=None):
    """Advanced template editor with full tools integration"""
    if not is_admin(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    template = None
    if template_id:
        template = get_object_or_404(Template, id=template_id)
        # Increment view count
        Template.objects.filter(id=template_id).update(view_count=F('view_count') + 1)
    
    # Get all editor resources
    categories = TemplateCategory.objects.filter(is_active=True).order_by('sort_order')
    tags = TemplateTag.objects.all().order_by('name')
    styles = TemplateStyle.objects.filter(is_active=True)
    layouts = TemplateLayout.objects.filter(is_active=True)
    components = TemplateComponent.objects.filter(is_active=True).order_by('component_type', 'name')
    color_palettes = ColorPalette.objects.filter(is_active=True)
    font_families = FontFamily.objects.filter(is_active=True).order_by('category', 'name')
    editor_tools = EditorTool.objects.filter(is_active=True).order_by('sort_order')
    ai_prompts = AIPromptTemplate.objects.filter(is_active=True).order_by('prompt_type', 'name')
    
    # Get database connections for dynamic content
    db_connections = DatabaseConnection.objects.filter(is_active=True)
    data_bindings = []
    if template:
        data_bindings = TemplateDataBinding.objects.filter(template=template, is_active=True)
    
    context = {
        'template': template,
        'categories': categories,
        'tags': tags,
        'styles': styles,
        'layouts': layouts,
        'components': components,
        'color_palettes': color_palettes,
        'font_families': font_families,
        'editor_tools': editor_tools,
        'ai_prompts': ai_prompts,
        'db_connections': db_connections,
        'data_bindings': data_bindings,
        'csrf_token': get_token(request),
        'page_title': f'Edit {template.name}' if template else 'Create New Template',
    }
    
    if template:
        log_activity(request.user, 'template_editor_opened', f'Opened template editor for: {template.name}', template.id)
    else:
        log_activity(request.user, 'template_editor_opened', 'Opened template editor for new template')
    
    return render(request, 'template_editor/editor.html', context)

# Template CRUD Operations
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_template(request):
    """Create new template with advanced features"""
    if not is_admin(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        # Create new template
        template = Template.objects.create(
            name=data.get('name', 'Untitled Template'),
            slug=slugify(data.get('name', 'untitled-template')),
            description=data.get('description', ''),
            html_content=data.get('html_content', ''),
            css_content=data.get('css_content', ''),
            js_content=data.get('js_content', ''),
            music_url=data.get('music_url', ''),
            category_id=data.get('category_id', 1),  # Default category
            created_by=request.user,
            updated_by=request.user
        )
        
        log_activity(request.user, 'template_created', f'Created template: {template.name}', template.id)
        
        return JsonResponse({
            'success': True,
            'template_id': str(template.id),
            'message': 'Template created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        return JsonResponse({'error': 'Failed to create template'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_template(request, template_id):
    """Update existing template"""
    if not is_admin(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        template = get_object_or_404(Template, id=template_id)
        data = json.loads(request.body)
        
        # Update template fields
        template.name = data.get('name', template.name)
        template.slug = slugify(data.get('name', template.name))
        template.description = data.get('description', template.description)
        template.html_content = data.get('html_content', template.html_content)
        template.css_content = data.get('css_content', template.css_content)
        template.js_content = data.get('js_content', template.js_content)
        template.music_url = data.get('music_url', template.music_url)
        template.updated_by = request.user
        template.save()
        
        log_activity(request.user, 'template_updated', f'Updated template: {template.name}', template.id)
        
        return JsonResponse({
            'success': True,
            'message': 'Template updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating template: {e}")
        return JsonResponse({'error': 'Failed to update template'}, status=500)

def template_gallery(request):
    """Gallery of available invitation templates"""
    categories = TemplateCategory.objects.filter(is_active=True)
    templates = InvitationTemplate.objects.filter(is_active=True).order_by('-created_at')
    
    # Filter by category if specified
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(TemplateCategory, slug=category_slug)
        templates = templates.filter(category=category)
    
    context = {
        'categories': categories,
        'templates': templates,
        'selected_category': category_slug,
        'page_title': 'Template Gallery',
    }
    
    return render(request, 'template_editor/gallery.html', context)

def template_preview_public(request, pk):
    """Preview a specific template"""
    template = get_object_or_404(InvitationTemplate, pk=pk, is_active=True)
    
    # Sample data for preview
    sample_data = {
        'judul': 'Preview Undangan',
        'nama_panggilan_pria': 'John',
        'nama_panggilan_wanita': 'Jane',
        'nama_lengkap_pria': 'John Doe',
        'nama_lengkap_wanita': 'Jane Smith',
        'tanggal_waktu_acara_1': timezone.now(),
        'tanggal_waktu_acara_2': timezone.now(),
        'judul_acara_1': 'Akad Nikah',
        'judul_acara_2': 'Resepsi',
        'nama_lokasi_acara_1': 'Masjid Al-Ikhlas',
        'nama_lokasi_acara_2': 'Gedung Serbaguna',
        'alamat_lokasi_acara_1': 'Jl. Contoh No. 123',
        'alamat_lokasi_acara_2': 'Jl. Contoh No. 456',
        'kutipan_pembuka': 'Dan di antara tanda-tanda kekuasaan-Nya...',
        'sumber_kutipan': 'QS. Ar-Rum: 21',
    }
    
    # Render template with sample data
    from django.template import Template as DjangoTemplate, Context
    django_template = DjangoTemplate(template.html_content)
    context = Context({'undangan': type('obj', (object,), sample_data)})
    rendered_html = django_template.render(context)
    
    return HttpResponse(rendered_html)

def create_invitation(request):
    """Create new invitation with template selection"""
    
    if request.method == 'POST':
        # Process form data
        data = request.POST
        files = request.FILES
        
        # Get selected template
        template_id = data.get('template_id')
        if not template_id:
            messages.error(request, 'Silakan pilih template terlebih dahulu')
            return redirect('template_editor:create_invitation')
        
        template = get_object_or_404(InvitationTemplate, pk=template_id, is_active=True)
        
        # Generate unique slug
        base_slug = slugify(data.get('slug', data.get('judul', 'undangan')))
        slug = base_slug
        counter = 1
        while Undangan.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Create new invitation
        undangan = Undangan(
            template=template,
            judul=data.get('judul', ''),
            slug=slug,
            nama_panggilan_pria=data.get('nama_panggilan_pria', ''),
            nama_panggilan_wanita=data.get('nama_panggilan_wanita', ''),
            nama_lengkap_pria=data.get('nama_lengkap_pria', ''),
            nama_lengkap_wanita=data.get('nama_lengkap_wanita', ''),
            info_orang_tua_pria=data.get('info_orang_tua_pria', ''),
            info_orang_tua_wanita=data.get('info_orang_tua_wanita', ''),
            kutipan_pembuka=data.get('kutipan_pembuka', ''),
            teks_penutup=data.get('teks_penutup', ''),
            judul_acara_1='Akad Nikah / Pemberkatan',
            nama_lokasi_acara_1=data.get('nama_lokasi_acara_1', ''),
            alamat_lokasi_acara_1=data.get('alamat_lokasi_acara_1', ''),
            judul_acara_2='Resepsi',
            nama_lokasi_acara_2=data.get('nama_lokasi_acara_2', ''),
            alamat_lokasi_acara_2=data.get('alamat_lokasi_acara_2', ''),
        )
        
        # Parse dates
        try:
            if data.get('tanggal_waktu_acara_1'):
                undangan.tanggal_waktu_acara_1 = datetime.strptime(
                    data.get('tanggal_waktu_acara_1'), '%Y-%m-%dT%H:%M'
                )
            if data.get('tanggal_waktu_acara_2'):
                undangan.tanggal_waktu_acara_2 = datetime.strptime(
                    data.get('tanggal_waktu_acara_2'), '%Y-%m-%dT%H:%M'
                )
        except ValueError:
            messages.error(request, 'Format tanggal tidak valid')
            return redirect('template_editor:create_invitation')
        
        # Handle file uploads
        if 'foto_pria' in files:
            undangan.foto_pria = files['foto_pria']
        if 'foto_wanita' in files:
            undangan.foto_wanita = files['foto_wanita']
        if 'foto_cover' in files:
            undangan.foto_cover = files['foto_cover']
        
        undangan.save()
        
        # Increment template usage
        template.increment_usage()
        
        messages.success(request, 'Undangan berhasil dibuat!')
        return redirect('template_editor:edit_invitation', slug=undangan.slug)
    
    context = {
        'page_title': 'Buat Undangan Baru',
    }
    
    return render(request, 'template_editor/create_invitation.html', context)

@require_http_methods(["GET"])
def api_templates(request):
    """API endpoint to get available templates"""
    templates = InvitationTemplate.objects.filter(is_active=True).select_related('category')
    
    template_data = []
    for template in templates:
        template_data.append({
            'id': template.id,
            'name': template.name,
            'category': template.category.name if template.category else 'Uncategorized',
            'preview_image': template.preview_image.url if template.preview_image else None,
            'description': template.description,
        })
    
    return JsonResponse(template_data, safe=False)

def edit_invitation(request, slug):
    """Edit existing invitation"""
    undangan = get_object_or_404(Undangan, slug=slug)
    
    if request.method == 'POST':
        # Update invitation data
        data = request.POST
        
        undangan.judul = data.get('judul', undangan.judul)
        undangan.nama_panggilan_pria = data.get('nama_panggilan_pria', undangan.nama_panggilan_pria)
        undangan.nama_panggilan_wanita = data.get('nama_panggilan_wanita', undangan.nama_panggilan_wanita)
        undangan.nama_lengkap_pria = data.get('nama_lengkap_pria', undangan.nama_lengkap_pria)
        undangan.nama_lengkap_wanita = data.get('nama_lengkap_wanita', undangan.nama_lengkap_wanita)
        undangan.kutipan_pembuka = data.get('kutipan_pembuka', undangan.kutipan_pembuka)
        undangan.sumber_kutipan = data.get('sumber_kutipan', undangan.sumber_kutipan)
        undangan.judul_acara_1 = data.get('judul_acara_1', undangan.judul_acara_1)
        undangan.nama_lokasi_acara_1 = data.get('nama_lokasi_acara_1', undangan.nama_lokasi_acara_1)
        undangan.alamat_lokasi_acara_1 = data.get('alamat_lokasi_acara_1', undangan.alamat_lokasi_acara_1)
        undangan.link_gmaps_acara_1 = data.get('link_gmaps_acara_1', undangan.link_gmaps_acara_1)
        undangan.judul_acara_2 = data.get('judul_acara_2', undangan.judul_acara_2)
        undangan.nama_lokasi_acara_2 = data.get('nama_lokasi_acara_2', undangan.nama_lokasi_acara_2)
        undangan.alamat_lokasi_acara_2 = data.get('alamat_lokasi_acara_2', undangan.alamat_lokasi_acara_2)
        undangan.link_gmaps_acara_2 = data.get('link_gmaps_acara_2', undangan.link_gmaps_acara_2)
        
        # Parse dates
        try:
            if data.get('tanggal_waktu_acara_1'):
                undangan.tanggal_waktu_acara_1 = datetime.strptime(
                    data.get('tanggal_waktu_acara_1'), '%Y-%m-%dT%H:%M'
                )
            if data.get('tanggal_waktu_acara_2'):
                undangan.tanggal_waktu_acara_2 = datetime.strptime(
                    data.get('tanggal_waktu_acara_2'), '%Y-%m-%dT%H:%M'
                )
        except ValueError:
            messages.error(request, 'Format tanggal tidak valid')
        
        undangan.save()
        messages.success(request, 'Undangan berhasil diperbarui!')
        return redirect('template_editor:edit_invitation', slug=slug)
    
    context = {
        'undangan': undangan,
        'page_title': f'Edit Undangan - {undangan.judul}',
    }
    
    return render(request, 'template_editor/edit_invitation.html', context)

def invitation_preview(request, slug):
    """Preview invitation with actual data"""
    undangan = get_object_or_404(Undangan, slug=slug)
    
    if undangan.template and undangan.template.html_content:
        # Render template with invitation data
        from django.template import Template as DjangoTemplate, Context
        django_template = DjangoTemplate(undangan.template.html_content)
        context = Context({'undangan': undangan})
        rendered_html = django_template.render(context)
        return HttpResponse(rendered_html)
    else:
        return HttpResponse('<h1>Template tidak ditemukan</h1>')

def publish_invitation(request, slug):
    """Publish/unpublish invitation"""
    undangan = get_object_or_404(Undangan, slug=slug)
    
    if request.method == 'POST':
        undangan.is_published = not undangan.is_published
        undangan.save()
        
        status = 'dipublikasikan' if undangan.is_published else 'disembunyikan'
        messages.success(request, f'Undangan berhasil {status}!')
    
    return redirect('template_editor:edit_invitation', slug=slug)

def my_invitations(request):
    """List user's invitations"""
    undangan_list = Undangan.objects.all().order_by('-created_at')
    
    context = {
        'undangan_list': undangan_list,
        'page_title': 'Undangan Saya',
    }
    
    return render(request, 'template_editor/my_invitations.html', context)

@login_required
def template_editor(request, template_id=None):
    """Template editor interface"""
    template = None
    if template_id:
        template = get_object_or_404(Template, id=template_id)
    
    categories = TemplateCategory.objects.all()
    
    context = {
        'template': template,
        'categories': categories,
        'is_edit_mode': template is not None
    }
    
    return render(request, 'template_editor/editor.html', context)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_template_data(request, template_id):
    """Get template data for editor"""
    try:
        template = get_object_or_404(Template, id=template_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': str(template.id),
                'name': template.name,
                'description': template.description,
                'html_content': template.html_content,
                'css_content': template.css_content,
                'js_content': template.js_content,
                'music_url': template.music_url,
                'category_id': template.category_id,
                'created_at': template.created_at.isoformat(),
                'updated_at': template.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting template data: {e}")
        return JsonResponse({'error': 'Failed to get template data'}, status=500)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['name', 'category_id', 'html_content']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        
        with transaction.atomic():
            # Create template
            template = Template.objects.create(
                name=data['name'],
                slug=slugify(data['name']) + '-' + str(uuid.uuid4())[:8],
                description=data.get('description', ''),
                category_id=data['category_id'],
                html_content=data['html_content'],
                css_content=data.get('css_content', ''),
                js_content=data.get('js_content', ''),
                layout_id=data.get('layout_id'),
                style_id=data.get('style_id'),
                color_palette_id=data.get('color_palette_id'),
                font_family_id=data.get('font_family_id'),
                is_responsive=data.get('is_responsive', True),
                is_print_ready=data.get('is_print_ready', False),
                is_interactive=data.get('is_interactive', False),
                has_animations=data.get('has_animations', False),
                is_ai_generated=data.get('is_ai_generated', False),
                ai_prompt=data.get('ai_prompt', ''),
                ai_model_used=data.get('ai_model_used', ''),
                meta_title=data.get('meta_title', ''),
                meta_description=data.get('meta_description', ''),
                meta_keywords=data.get('meta_keywords', ''),
                created_by=request.user,
                updated_by=request.user
            )
            
            # Add tags
            if data.get('tags'):
                tag_ids = data['tags']
                template.tags.set(tag_ids)
            
            # Create initial version
            TemplateVersion.objects.create(
                template=template,
                version_number='1.0.0',
                html_content=template.html_content,
                css_content=template.css_content,
                js_content=template.js_content,
                changelog='Initial version',
                created_by=request.user,
                is_current=True
            )
            
            # Create data bindings if provided
            if data.get('data_bindings'):
                for binding in data['data_bindings']:
                    TemplateDataBinding.objects.create(
                        template=template,
                        database_connection_id=binding['connection_id'],
                        field_name=binding['field_name'],
                        data_source=binding['data_source'],
                        data_field=binding['data_field'],
                        data_query=binding.get('data_query', ''),
                        data_transform=binding.get('data_transform', '')
                    )
            
            log_activity(request.user, 'template_created', f'Created template: {template.name}', template.id)
            
            return JsonResponse({
                'success': True,
                'template_id': str(template.id),
                'message': 'Template created successfully',
                'redirect_url': reverse('template_editor:editor', kwargs={'template_id': template.id})
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# ============================================================================
# UNDANGAN VIEWS - Wedding Invitation Management
# ============================================================================

def undangan_detail(request, slug):
    """Display undangan using the beautiful template"""
    undangan = get_object_or_404(Undangan, slug=slug)
    
    # Get all related data
    story_items = undangan.story_items.all().order_by('tanggal_kejadian')
    gallery_photos = undangan.gallery_photos.all()
    gift_accounts = undangan.gift_accounts.all()
    guest_comments = undangan.guest_comments.all().order_by('-waktu_kirim')[:20]
    social_links = undangan.social_links.all()
    
    context = {
        'undangan': undangan,
        'story_items': story_items,
        'gallery_photos': gallery_photos,
        'gift_accounts': gift_accounts,
        'guest_comments': guest_comments,
        'social_links': social_links,
    }
    return render(request, 'template_editor/wedding_template.html', context)

@login_required
def create_undangan(request, template_id=None):
    """Create new undangan from template"""
    template = None
    if template_id:
        template = get_object_or_404(InvitationTemplate, id=template_id, is_active=True)
    
    if request.method == 'POST':
        # Validasi field yang wajib diisi
        required_fields = {
            'judul': 'Judul undangan',
            'nama_panggilan_pria': 'Nama panggilan pria',
            'nama_panggilan_wanita': 'Nama panggilan wanita',
            'nama_lengkap_pria': 'Nama lengkap pria',
            'nama_lengkap_wanita': 'Nama lengkap wanita',
            'slug': 'URL undangan'
        }
        
        errors = []
        for field, label in required_fields.items():
            value = request.POST.get(field, '').strip()
            if not value:
                errors.append(f'{label} wajib diisi')
        
        # Validasi slug format
        slug = request.POST.get('slug', '').strip()
        if slug:
            import re
            if not re.match(r'^[a-z0-9-]+$', slug):
                errors.append('URL undangan hanya boleh mengandung huruf kecil, angka, dan tanda hubung')
            
            # Cek keunikan slug
            if Undangan.objects.filter(slug=slug).exists():
                errors.append('URL undangan sudah digunakan, silakan gunakan URL yang lain')
        
        # Validasi template
        selected_template_id = request.POST.get('selectedTemplateId')
        if selected_template_id:
            try:
                template = get_object_or_404(InvitationTemplate, id=selected_template_id, is_active=True)
            except:
                errors.append('Template yang dipilih tidak valid')
        
        # Jika ada error, tampilkan pesan error
        if errors:
            for error in errors:
                messages.error(request, error)
            # Get available templates for re-rendering form
            available_templates = InvitationTemplate.objects.filter(is_active=True).order_by('name')
            context = {
                'template': template,
                'available_templates': available_templates,
                'form_data': request.POST,  # Preserve form data
            }
            return render(request, 'template_editor/create_undangan.html', context)
        
        # Create undangan from POST data
        undangan = Undangan(
            judul=request.POST.get('judul', ''),
            slug=slug,
            nama_panggilan_pria=request.POST.get('nama_panggilan_pria', ''),
            nama_panggilan_wanita=request.POST.get('nama_panggilan_wanita', ''),
            nama_lengkap_pria=request.POST.get('nama_lengkap_pria', ''),
            nama_lengkap_wanita=request.POST.get('nama_lengkap_wanita', ''),
            info_orang_tua_pria=request.POST.get('info_orang_tua_pria', ''),
            info_orang_tua_wanita=request.POST.get('info_orang_tua_wanita', ''),
            kutipan_pembuka=request.POST.get('kutipan_pembuka', ''),
            sumber_kutipan=request.POST.get('sumber_kutipan', ''),
            teks_pengantar_cerita=request.POST.get('teks_pengantar_cerita', ''),
            teks_pengantar_acara=request.POST.get('teks_pengantar_acara', ''),
            teks_pengantar_galeri=request.POST.get('teks_pengantar_galeri', ''),
            teks_pengantar_hadiah=request.POST.get('teks_pengantar_hadiah', ''),
            teks_pengantar_rsvp=request.POST.get('teks_pengantar_rsvp', ''),
            teks_penutup=request.POST.get('teks_penutup', ''),
            judul_acara_1=request.POST.get('judul_acara_1', ''),
            nama_lokasi_acara_1=request.POST.get('nama_lokasi_acara_1', ''),
            alamat_lokasi_acara_1=request.POST.get('alamat_lokasi_acara_1', ''),
            link_gmaps_acara_1=request.POST.get('link_gmaps_acara_1', ''),
            judul_acara_2=request.POST.get('judul_acara_2', ''),
            nama_lokasi_acara_2=request.POST.get('nama_lokasi_acara_2', ''),
            alamat_lokasi_acara_2=request.POST.get('alamat_lokasi_acara_2', ''),
            link_gmaps_acara_2=request.POST.get('link_gmaps_acara_2', ''),
        )
        
        if template:
            undangan.template = template
        
        # Handle file uploads dengan validasi
        if 'foto_cover' in request.FILES:
            file = request.FILES['foto_cover']
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                messages.error(request, 'Ukuran foto cover maksimal 5MB')
                return redirect('template_editor:create_undangan')
            undangan.foto_cover = file
            
        if 'foto_pria' in request.FILES:
            file = request.FILES['foto_pria']
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                messages.error(request, 'Ukuran foto pria maksimal 5MB')
                return redirect('template_editor:create_undangan')
            undangan.foto_pria = file
            
        if 'foto_wanita' in request.FILES:
            file = request.FILES['foto_wanita']
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                messages.error(request, 'Ukuran foto wanita maksimal 5MB')
                return redirect('template_editor:create_undangan')
            undangan.foto_wanita = file
            
        if 'file_musik' in request.FILES:
            file = request.FILES['file_musik']
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                messages.error(request, 'Ukuran file musik maksimal 10MB')
                return redirect('template_editor:create_undangan')
            undangan.file_musik = file
        
        # Handle datetime fields dengan validasi
        try:
            if request.POST.get('tanggal_waktu_acara_1'):
                undangan.tanggal_waktu_acara_1 = request.POST.get('tanggal_waktu_acara_1')
            if request.POST.get('waktu_selesai_acara_1'):
                undangan.waktu_selesai_acara_1 = request.POST.get('waktu_selesai_acara_1')
            if request.POST.get('tanggal_waktu_acara_2'):
                undangan.tanggal_waktu_acara_2 = request.POST.get('tanggal_waktu_acara_2')
            if request.POST.get('waktu_selesai_acara_2'):
                undangan.waktu_selesai_acara_2 = request.POST.get('waktu_selesai_acara_2')
        except ValueError as e:
            messages.error(request, 'Format tanggal atau waktu tidak valid')
            return redirect('template_editor:create_undangan')
        
        try:
            undangan.save()
            messages.success(request, 'Undangan berhasil dibuat!')
            return redirect('template_editor:edit_undangan', slug=undangan.slug)
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan saat menyimpan undangan: {str(e)}')
            return redirect('template_editor:create_undangan')
    
    # Get available templates for selection
    available_templates = InvitationTemplate.objects.filter(is_active=True).order_by('name')
    
    context = {
        'template': template,
        'available_templates': available_templates,
    }
    return render(request, 'template_editor/create_undangan.html', context)

@login_required
def edit_undangan(request, slug):
    """Edit undangan"""
    undangan = get_object_or_404(Undangan, slug=slug)
    
    if request.method == 'POST':
        # Update undangan from POST data
        undangan.judul = request.POST.get('judul', undangan.judul)
        undangan.nama_panggilan_pria = request.POST.get('nama_panggilan_pria', undangan.nama_panggilan_pria)
        undangan.nama_panggilan_wanita = request.POST.get('nama_panggilan_wanita', undangan.nama_panggilan_wanita)
        undangan.nama_lengkap_pria = request.POST.get('nama_lengkap_pria', undangan.nama_lengkap_pria)
        undangan.nama_lengkap_wanita = request.POST.get('nama_lengkap_wanita', undangan.nama_lengkap_wanita)
        undangan.info_orang_tua_pria = request.POST.get('info_orang_tua_pria', undangan.info_orang_tua_pria)
        undangan.info_orang_tua_wanita = request.POST.get('info_orang_tua_wanita', undangan.info_orang_tua_wanita)
        undangan.kutipan_pembuka = request.POST.get('kutipan_pembuka', undangan.kutipan_pembuka)
        undangan.sumber_kutipan = request.POST.get('sumber_kutipan', undangan.sumber_kutipan)
        undangan.teks_pengantar_cerita = request.POST.get('teks_pengantar_cerita', undangan.teks_pengantar_cerita)
        undangan.teks_pengantar_acara = request.POST.get('teks_pengantar_acara', undangan.teks_pengantar_acara)
        undangan.teks_pengantar_galeri = request.POST.get('teks_pengantar_galeri', undangan.teks_pengantar_galeri)
        undangan.teks_pengantar_hadiah = request.POST.get('teks_pengantar_hadiah', undangan.teks_pengantar_hadiah)
        undangan.teks_pengantar_rsvp = request.POST.get('teks_pengantar_rsvp', undangan.teks_pengantar_rsvp)
        undangan.teks_penutup = request.POST.get('teks_penutup', undangan.teks_penutup)
        undangan.judul_acara_1 = request.POST.get('judul_acara_1', undangan.judul_acara_1)
        undangan.nama_lokasi_acara_1 = request.POST.get('nama_lokasi_acara_1', undangan.nama_lokasi_acara_1)
        undangan.alamat_lokasi_acara_1 = request.POST.get('alamat_lokasi_acara_1', undangan.alamat_lokasi_acara_1)
        undangan.link_gmaps_acara_1 = request.POST.get('link_gmaps_acara_1', undangan.link_gmaps_acara_1)
        undangan.judul_acara_2 = request.POST.get('judul_acara_2', undangan.judul_acara_2)
        undangan.nama_lokasi_acara_2 = request.POST.get('nama_lokasi_acara_2', undangan.nama_lokasi_acara_2)
        undangan.alamat_lokasi_acara_2 = request.POST.get('alamat_lokasi_acara_2', undangan.alamat_lokasi_acara_2)
        undangan.link_gmaps_acara_2 = request.POST.get('link_gmaps_acara_2', undangan.link_gmaps_acara_2)
        
        # Handle file uploads
        if 'foto_cover' in request.FILES:
            undangan.foto_cover = request.FILES['foto_cover']
        if 'foto_pria' in request.FILES:
            undangan.foto_pria = request.FILES['foto_pria']
        if 'foto_wanita' in request.FILES:
            undangan.foto_wanita = request.FILES['foto_wanita']
        if 'file_musik' in request.FILES:
            undangan.file_musik = request.FILES['file_musik']
        
        # Handle datetime fields
        if request.POST.get('tanggal_waktu_acara_1'):
            undangan.tanggal_waktu_acara_1 = request.POST.get('tanggal_waktu_acara_1')
        if request.POST.get('waktu_selesai_acara_1'):
            undangan.waktu_selesai_acara_1 = request.POST.get('waktu_selesai_acara_1')
        if request.POST.get('tanggal_waktu_acara_2'):
            undangan.tanggal_waktu_acara_2 = request.POST.get('tanggal_waktu_acara_2')
        if request.POST.get('waktu_selesai_acara_2'):
            undangan.waktu_selesai_acara_2 = request.POST.get('waktu_selesai_acara_2')
        
        undangan.save()
        messages.success(request, 'Undangan berhasil diperbarui!')
        return redirect('template_editor:edit_undangan', slug=undangan.slug)
    
    # Get related objects
    story_items = undangan.story_items.all()
    gallery_photos = undangan.gallery_photos.all()
    gift_accounts = undangan.gift_accounts.all()
    social_links = undangan.social_links.all()
    
    context = {
        'undangan': undangan,
        'story_items': story_items,
        'gallery_photos': gallery_photos,
        'gift_accounts': gift_accounts,
        'social_links': social_links,
    }
    return render(request, 'template_editor/edit_undangan.html', context)

@csrf_exempt
def add_guest_comment(request, slug):
    """Add guest comment via AJAX"""
    if request.method == 'POST':
        undangan = get_object_or_404(Undangan, slug=slug)
        
        try:
            data = json.loads(request.body)
            comment = GuestComment.objects.create(
                undangan=undangan,
                nama_tamu=data.get('nama_tamu'),
                ucapan=data.get('ucapan'),
                kehadiran=data.get('kehadiran')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Ucapan berhasil dikirim!',
                'comment': {
                    'nama_tamu': comment.nama_tamu,
                    'ucapan': comment.ucapan,
                    'kehadiran': comment.kehadiran,
                    'waktu_kirim': comment.waktu_kirim.strftime('%d %b %Y %H:%M')
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Terjadi kesalahan saat mengirim ucapan.'
            })
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})

@login_required
def publish_undangan(request, slug):
    """Publish/unpublish undangan"""
    undangan = get_object_or_404(Undangan, slug=slug)
    
    if request.method == 'POST':
        undangan.is_published = not undangan.is_published
        undangan.save()
        
        status = 'dipublikasikan' if undangan.is_published else 'disembunyikan'
        messages.success(request, f'Undangan berhasil {status}!')
    
    return redirect('template_editor:edit_undangan', slug=slug)

@login_required
def undangan_dashboard(request):
    """Dashboard showing all undangan"""
    undangan_list = Undangan.objects.all().order_by('-created_at')
    
    # Calculate statistics
    total_undangan = undangan_list.count()
    published_count = undangan_list.filter(is_published=True).count()
    draft_count = undangan_list.filter(is_published=False).count()
    total_views = sum(undangan.view_count or 0 for undangan in undangan_list)
    
    # Pagination
    paginator = Paginator(undangan_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'undangan_list': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_undangan': total_undangan,
        'published_count': published_count,
        'draft_count': draft_count,
        'total_views': total_views,
    }
    return render(request, 'template_editor/dashboard.html', context)

def export_undangan(request, slug, format_type='html'):
    """Export undangan in various formats"""
    undangan = get_object_or_404(Undangan, slug=slug)
    
    if format_type == 'html':
        # Render the template as HTML
        context = {
            'undangan': undangan,
            'story_items': undangan.story_items.all(),
            'gallery_photos': undangan.gallery_photos.all(),
            'gift_accounts': undangan.gift_accounts.all(),
            'guest_comments': undangan.guest_comments.all(),
            'social_links': undangan.social_links.all(),
        }
        
        html_content = render_to_string('template_editor/wedding_template.html', context)
        
        response = HttpResponse(html_content, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="{undangan.slug}.html"'
        return response
    
    # Add other export formats (PDF, etc.) here
    return HttpResponse('Format not supported yet', status=400)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_template(request, template_id):
    """Update existing template"""
    if not is_admin(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        template = get_object_or_404(Template, id=template_id)
        data = json.loads(request.body)
        
        with transaction.atomic():
            # Store old version if content changed
            content_changed = (
                data.get('html_content') != template.html_content or
                data.get('css_content') != template.css_content or
                data.get('js_content') != template.js_content
            )
            
            if content_changed:
                # Create new version
                version_number = data.get('version_number', '1.0.1')
                TemplateVersion.objects.filter(template=template).update(is_current=False)
                TemplateVersion.objects.create(
                    template=template,
                    version_number=version_number,
                    html_content=data.get('html_content', template.html_content),
                    css_content=data.get('css_content', template.css_content),
                    js_content=data.get('js_content', template.js_content),
                    changelog=data.get('changelog', 'Updated template'),
                    created_by=request.user,
                    is_current=True
                )
            
            # Update template fields
            update_fields = [
                'name', 'description', 'html_content', 'css_content', 'js_content',
                'is_responsive', 'is_print_ready', 'is_interactive', 'has_animations',
                'meta_title', 'meta_description', 'meta_keywords'
            ]
            
            for field in update_fields:
                if field in data:
                    setattr(template, field, data[field])
            
            # Update foreign key fields
            fk_fields = ['category_id', 'layout_id', 'style_id', 'color_palette_id', 'font_family_id']
            for field in fk_fields:
                if field in data:
                    setattr(template, field, data[field])
            
            template.updated_by = request.user
            template.save()
            
            # Update tags
            if 'tags' in data:
                template.tags.set(data['tags'])
            
            # Update data bindings
            if 'data_bindings' in data:
                # Remove existing bindings
                TemplateDataBinding.objects.filter(template=template).delete()
                
                # Create new bindings
                for binding in data['data_bindings']:
                    TemplateDataBinding.objects.create(
                        template=template,
                        database_connection_id=binding['connection_id'],
                        field_name=binding['field_name'],
                        data_source=binding['data_source'],
                        data_field=binding['data_field'],
                        data_query=binding.get('data_query', ''),
                        data_transform=binding.get('data_transform', '')
                    )
            
            log_activity(request.user, 'template_updated', f'Updated template: {template.name}', template.id)
            
            return JsonResponse({
                'success': True,
                'message': 'Template updated successfully'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error updating template: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
@login_required
def get_template(request, template_id):
    """Get template data for editor"""
    try:
        template = get_object_or_404(Template, id=template_id)
        
        # Get data bindings
        data_bindings = []
        for binding in template.data_bindings.filter(is_active=True):
            data_bindings.append({
                'id': binding.id,
                'connection_id': binding.database_connection.id,
                'connection_name': binding.database_connection.name,
                'field_name': binding.field_name,
                'data_source': binding.data_source,
                'data_field': binding.data_field,
                'data_query': binding.data_query,
                'data_transform': binding.data_transform
            })
        
        # Get template data
        template_data = {
            'id': str(template.id),
            'name': template.name,
            'slug': template.slug,
            'description': template.description,
            'category_id': template.category.id if template.category else None,
            'category_name': template.category.name if template.category else None,
            'tags': [{'id': tag.id, 'name': tag.name} for tag in template.tags.all()],
            'html_content': template.html_content,
            'css_content': template.css_content,
            'js_content': template.js_content,
            'layout_id': template.layout.id if template.layout else None,
            'style_id': template.style.id if template.style else None,
            'color_palette_id': template.color_palette.id if template.color_palette else None,
            'font_family_id': template.font_family.id if template.font_family else None,
            'is_responsive': template.is_responsive,
            'is_print_ready': template.is_print_ready,
            'is_interactive': template.is_interactive,
            'has_animations': template.has_animations,
            'is_ai_generated': template.is_ai_generated,
            'ai_prompt': template.ai_prompt,
            'ai_model_used': template.ai_model_used,
            'meta_title': template.meta_title,
            'meta_description': template.meta_description,
            'meta_keywords': template.meta_keywords,
            'is_published': template.is_published,
            'is_featured': template.is_featured,
            'view_count': template.view_count,
            'download_count': template.download_count,
            'data_bindings': data_bindings,
            'created_at': template.created_at.isoformat(),
            'updated_at': template.updated_at.isoformat(),
        }
        
        return JsonResponse({
            'success': True,
            'template': template_data
        })
        
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# Database Integration Functions
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def test_database_connection(request):
    """Test database connection"""
    if not is_admin(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        connection_id = data.get('connection_id')
        
        if not connection_id:
            return JsonResponse({'error': 'Connection ID required'}, status=400)
        
        db_connection = get_object_or_404(DatabaseConnection, id=connection_id)
        
        # Test connection based on type
        success = False
        error_message = ''
        
        try:
            # SQLite connection commented out for MySQL migration
            # if db_connection.connection_type == 'sqlite':
            #     conn = sqlite3.connect(db_connection.connection_string)
            #     cursor = conn.cursor()
            #     if db_connection.test_query:
            #         cursor.execute(db_connection.test_query)
            #     else:
            #         cursor.execute("SELECT 1")
            #     conn.close()
            #     success = True
                
            if db_connection.connection_type == 'api':
                response = requests.get(db_connection.connection_string, timeout=10)
                if response.status_code == 200:
                    success = True
                else:
                    error_message = f"API returned status code: {response.status_code}"
                    
            elif db_connection.connection_type == 'json':
                if os.path.exists(db_connection.connection_string):
                    with open(db_connection.connection_string, 'r') as f:
                        json.load(f)
                    success = True
                else:
                    error_message = "JSON file not found"
                    
            elif db_connection.connection_type == 'csv':
                if os.path.exists(db_connection.connection_string):
                    pd.read_csv(db_connection.connection_string, nrows=1)
                    success = True
                else:
                    error_message = "CSV file not found"
            
            # Update connection status
            db_connection.is_connected = success
            db_connection.last_tested = timezone.now()
            db_connection.save()
            
        except Exception as e:
            error_message = str(e)
            success = False
        
        return JsonResponse({
            'success': success,
            'message': 'Connection successful' if success else f'Connection failed: {error_message}'
        })
        
    except Exception as e:
        logger.error(f"Error testing database connection: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def get_database_data(request):
    """Get data from database for template binding"""
    if not is_admin(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        connection_id = data.get('connection_id')
        data_source = data.get('data_source')
        query = data.get('query', '')
        limit = data.get('limit', 100)
        
        if not connection_id or not data_source:
            return JsonResponse({'error': 'Connection ID and data source required'}, status=400)
        
        db_connection = get_object_or_404(DatabaseConnection, id=connection_id)
        
        result_data = []
        columns = []
        
        try:
            # SQLite connection commented out for MySQL migration
            # if db_connection.connection_type == 'sqlite':
            #     conn = sqlite3.connect(db_connection.connection_string)
            #     cursor = conn.cursor()
            #     
            #     if query:
            #         cursor.execute(query)
            #     else:
            #         cursor.execute(f"SELECT * FROM {data_source} LIMIT {limit}")
            #     
            #     columns = [description[0] for description in cursor.description]
            #     result_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            #     conn.close()
                
            if db_connection.connection_type == 'api':
                url = f"{db_connection.connection_string}/{data_source}"
                if query:
                    url += f"?{query}"
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    api_data = response.json()
                    if isinstance(api_data, list):
                        result_data = api_data[:limit]
                        if result_data:
                            columns = list(result_data[0].keys())
                    elif isinstance(api_data, dict):
                        result_data = [api_data]
                        columns = list(api_data.keys())
                        
            elif db_connection.connection_type == 'json':
                with open(db_connection.connection_string, 'r') as f:
                    json_data = json.load(f)
                
                if data_source in json_data:
                    source_data = json_data[data_source]
                    if isinstance(source_data, list):
                        result_data = source_data[:limit]
                        if result_data:
                            columns = list(result_data[0].keys())
                            
            elif db_connection.connection_type == 'csv':
                df = pd.read_csv(db_connection.connection_string, nrows=limit)
                columns = df.columns.tolist()
                result_data = df.to_dict('records')
        
        except Exception as e:
            return JsonResponse({'error': f'Database query failed: {str(e)}'}, status=500)
        
        return JsonResponse({
            'success': True,
            'data': result_data,
            'columns': columns,
            'count': len(result_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting database data: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# AI Integration
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def generate_ai_content(request):
    """Generate content using AI"""
    if not is_admin(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt')
        content_type = data.get('content_type', 'html')  # html, css, js
        template_id = data.get('template_id')
        
        if not prompt:
            return JsonResponse({'error': 'Prompt required'}, status=400)
        
        # Create AI generation history record
        ai_history = AIGenerationHistory.objects.create(
            admin=request.user,
            prompt=prompt,
            content_type=content_type,
            template_id=template_id,
            status='processing'
        )
        
        try:
            # Here you would integrate with your AI service (Gemini, OpenAI, etc.)
            # For now, we'll return a placeholder response
            
            generated_content = f"<!-- AI Generated {content_type.upper()} Content -->\n"
            
            if content_type == 'html':
                generated_content += f"<div class='ai-generated'>\n  <h2>AI Generated Content</h2>\n  <p>Based on prompt: {prompt}</p>\n</div>"
            elif content_type == 'css':
                generated_content += f".ai-generated {{\n  background: linear-gradient(45deg, #667eea, #764ba2);\n  padding: 20px;\n  border-radius: 10px;\n  color: white;\n}}"
            elif content_type == 'js':
                generated_content += f"// AI Generated JavaScript\nconsole.log('Generated from prompt: {prompt}');\n\nfunction aiGeneratedFunction() {{\n  alert('This is AI generated content!');\n}}"
            
            # Update AI history
            ai_history.generated_content = generated_content
            ai_history.status = 'completed'
            ai_history.completed_at = timezone.now()
            ai_history.save()
            
            log_activity(request.user, 'ai_content_generated', f'Generated {content_type} content using AI')
            
            return JsonResponse({
                'success': True,
                'content': generated_content,
                'content_type': content_type,
                'generation_id': ai_history.id
            })
            
        except Exception as e:
            ai_history.status = 'failed'
            ai_history.error_message = str(e)
            ai_history.save()
            raise e
            
    except Exception as e:
        logger.error(f"Error generating AI content: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# Template Export Functions
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def export_template(request, template_id):
    """Export template in various formats"""
    if not is_admin(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        template = get_object_or_404(Template, id=template_id)
        data = json.loads(request.body)
        export_format = data.get('format', 'html')
        
        # Create export record
        export_record = TemplateExport.objects.create(
            template=template,
            user=request.user,
            export_format=export_format
        )
        
        try:
            if export_format == 'html':
                # Generate complete HTML file
                html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{template.name}</title>
    <style>
{template.css_content}
    </style>
</head>
<body>
{template.html_content}
    <script>
{template.js_content}
    </script>
</body>
</html>"""
                
                # Save to file
                filename = f"{template.slug}.html"
                file_path = default_storage.save(
                    f"exports/{filename}",
                    ContentFile(html_content.encode('utf-8'))
                )
                
                export_record.file_path = file_path
                export_record.file_size = len(html_content.encode('utf-8'))
                
            elif export_format == 'json':
                # Export as JSON data
                template_data = {
                    'name': template.name,
                    'description': template.description,
                    'html_content': template.html_content,
                    'css_content': template.css_content,
                    'js_content': template.js_content,
                    'category': template.category.name if template.category else None,
                    'tags': [tag.name for tag in template.tags.all()],
                    'is_responsive': template.is_responsive,
                    'is_interactive': template.is_interactive,
                    'has_animations': template.has_animations,
                    'created_at': template.created_at.isoformat(),
                    'updated_at': template.updated_at.isoformat(),
                }
                
                json_content = json.dumps(template_data, indent=2, ensure_ascii=False)
                filename = f"{template.slug}.json"
                file_path = default_storage.save(
                    f"exports/{filename}",
                    ContentFile(json_content.encode('utf-8'))
                )
                
                export_record.file_path = file_path
                export_record.file_size = len(json_content.encode('utf-8'))
            
            # Update download count
            Template.objects.filter(id=template_id).update(download_count=F('download_count') + 1)
            
            export_record.save()
            
            log_activity(request.user, 'template_exported', f'Exported template: {template.name} as {export_format}', template.id)
            
            return JsonResponse({
                'success': True,
                'download_url': default_storage.url(export_record.file_path),
                'filename': filename,
                'file_size': export_record.file_size
            })
            
        except Exception as e:
            export_record.delete()
            raise e
            
    except Exception as e:
        logger.error(f"Error exporting template: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# Integration with Main App
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def publish_to_main_app(request, template_id):
    """Publish template to main invitation app"""
    if not is_admin(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        template = get_object_or_404(Template, id=template_id)
        
        # Create or update InvitationTemplate in main app
        invitation_template, created = InvitationTemplate.objects.get_or_create(
            editor_template_id=str(template.id),
            defaults={
                'name': template.name,
                'description': template.description,
                'html_content': template.html_content,
                'css_content': template.css_content,
                'js_content': template.js_content,
                'category': template.category.name if template.category else 'General',
                'price': template.price,
                'is_premium': template.is_premium,
                'is_active': True,
                'created_by': request.user
            }
        )
        
        if not created:
            # Update existing template
            invitation_template.name = template.name
            invitation_template.description = template.description
            invitation_template.html_content = template.html_content
            invitation_template.css_content = template.css_content
            invitation_template.js_content = template.js_content
            invitation_template.price = template.price
            invitation_template.is_premium = template.is_premium
            invitation_template.save()
        
        # Mark template as published
        template.is_published = True
        template.published_at = timezone.now()
        template.save()
        
        log_activity(request.user, 'template_published', f'Published template to main app: {template.name}', template.id)
        
        return JsonResponse({
            'success': True,
            'message': 'Template published to main app successfully',
            'invitation_template_id': invitation_template.id
        })
        
    except Exception as e:
        logger.error(f"Error publishing template: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# API Endpoints for Editor Tools
@require_http_methods(["GET"])
@login_required
def get_editor_tools(request):
    """Get all available editor tools"""
    try:
        tools = EditorTool.objects.filter(is_active=True).order_by('sort_order')
        tools_data = []
        
        for tool in tools:
            tools_data.append({
                'id': tool.id,
                'name': tool.name,
                'tool_type': tool.tool_type,
                'description': tool.description,
                'icon': tool.icon,
                'is_premium': tool.is_premium,
                'configuration': tool.configuration
            })
        
        return JsonResponse({
            'success': True,
            'tools': tools_data
        })
        
    except Exception as e:
        logger.error(f"Error getting editor tools: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
@login_required
def get_components(request):
    """Get template components by type"""
    try:
        component_type = request.GET.get('type')
        components = TemplateComponent.objects.filter(is_active=True)
        
        if component_type:
            components = components.filter(component_type=component_type)
        
        components_data = []
        for component in components:
            components_data.append({
                'id': component.id,
                'name': component.name,
                'description': component.description,
                'component_type': component.component_type,
                'html_code': component.html_code,
                'css_code': component.css_code,
                'js_code': component.js_code,
                'dependencies': component.dependencies,
                'customizable_fields': component.customizable_fields,
                'is_premium': component.is_premium,
                'usage_count': component.usage_count
            })
        
        return JsonResponse({
            'success': True,
            'components': components_data
        })
        
    except Exception as e:
        logger.error(f"Error getting components: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# Template Preview
@require_http_methods(["GET"])
def preview_template(request, template_id):
    """Preview template in full screen"""
    try:
        template = get_object_or_404(Template, id=template_id)
        
        # Process dynamic content if data bindings exist
        html_content = template.html_content
        css_content = template.css_content
        js_content = template.js_content
        
        # Replace data bindings with actual data
        data_bindings = template.data_bindings.filter(is_active=True)
        for binding in data_bindings:
            try:
                # Get data from database
                db_connection = binding.database_connection
                if db_connection.is_connected:
                    # Fetch data based on connection type
                    data_value = "Sample Data"  # Placeholder - implement actual data fetching
                    
                    # Replace placeholder in HTML
                    placeholder = f"{{{{{binding.field_name}}}}}"
                    html_content = html_content.replace(placeholder, str(data_value))
                    
            except Exception as e:
                logger.error(f"Error processing data binding {binding.field_name}: {e}")
        
        # Increment view count
        Template.objects.filter(id=template_id).update(view_count=F('view_count') + 1)
        
        context = {
            'template': template,
            'html_content': html_content,
            'css_content': css_content,
            'js_content': js_content
        }
        
        return render(request, 'template_editor/preview.html', context)
        
    except Exception as e:
        logger.error(f"Error previewing template: {e}")
        return render(request, 'template_editor/error.html', {'error': str(e)})

# Template List for Admin Panel
@login_required
def template_list(request):
    """List all templates for admin panel"""
    if not is_admin(request.user):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('admin_panel:login')
    
    templates = Template.objects.all().order_by('-created_at')
    
    # Apply filters
    category_id = request.GET.get('category')
    if category_id:
        templates = templates.filter(category_id=category_id)
    
    status = request.GET.get('status')
    if status == 'published':
        templates = templates.filter(is_published=True)
    elif status == 'draft':
        templates = templates.filter(is_published=False)
    
    search = request.GET.get('search')
    if search:
        templates = templates.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(tags__name__icontains=search)
        ).distinct()
    
    # Pagination
    paginator = Paginator(templates, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = TemplateCategory.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_id,
        'current_status': status,
        'search_query': search,
        'page_title': 'Template Management'
    }
    
    return render(request, 'template_editor/template_list.html', context)

# Delete Template
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def delete_template(request, template_id):
    """Delete template"""
    if not is_admin(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        template = get_object_or_404(Template, id=template_id)
        
        # Check if template is used in any orders
        if hasattr(template, 'invitationtemplate') and Order.objects.filter(template=template.invitationtemplate).exists():
            return JsonResponse({
                'error': 'Cannot delete template that has been used in orders'
            }, status=400)
        
        template_name = template.name
        template.delete()
        
        log_activity(request.user, 'template_deleted', f'Deleted template: {template_name}')
        
        return JsonResponse({
            'success': True,
            'message': 'Template deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting template: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# API for Template Preview
@require_http_methods(["GET"])
def get_template_preview_api(request, template_id):
    """Get template preview HTML for AJAX requests"""
    try:
        template = get_object_or_404(InvitationTemplate, id=template_id, is_active=True)
        
        # Sample data for preview
        sample_data = {
            'judul': 'Preview Undangan',
            'nama_panggilan_pria': request.GET.get('nama_panggilan_pria', 'John'),
            'nama_panggilan_wanita': request.GET.get('nama_panggilan_wanita', 'Jane'),
            'nama_lengkap_pria': request.GET.get('nama_lengkap_pria', 'John Doe'),
            'nama_lengkap_wanita': request.GET.get('nama_lengkap_wanita', 'Jane Smith'),
            'tanggal_akad': request.GET.get('tanggal_akad', '2024-06-15'),
            'alamat_resepsi': request.GET.get('alamat_resepsi', 'Gedung Serbaguna'),
            'slug': request.GET.get('slug', 'preview-undangan'),
        }
        
        # Render template with sample data
        from django.template import Template as DjangoTemplate, Context
        django_template = DjangoTemplate(template.html_content)
        context = Context({'undangan': type('obj', (object,), sample_data)})
        rendered_html = django_template.render(context)
        
        return JsonResponse({
            'success': True,
            'html': rendered_html,
            'template_name': template.name
        })
        
    except Exception as e:
        logger.error(f"Error getting template preview: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)