from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from datetime import datetime, timedelta
import json
import os
import uuid
import requests
import google.generativeai as genai
from PIL import Image
import io
import base64
import csv
import zipfile
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# JWT imports
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.permissions import IsAuthenticated
from functools import wraps

# Import models
from main.models import InvitationTemplate, Order, InvitationData
from template_editor.models import (
    Template as EditorTemplate, TemplateCategory as EditorTemplateCategory, 
    TemplateTag as EditorTemplateTag, ColorPalette, FontFamily, TemplateLayout,
    TemplateStyle, TemplateComponent, AIPromptTemplate as EditorAIPromptTemplate
)
from .models import (
    AdminProfile, SystemSettings, ActivityLog, TemplateCategory, TemplateTag,
    TemplateVersion, AIPromptTemplate, AIGenerationHistory, CustomerFeedback,
    EmailTemplate, EmailLog, PaymentMethod, PaymentTransaction, Discount,
    Analytics, BackupSchedule, BackupFile, NotificationTemplate, NotificationQueue,
    WebhookEndpoint, WebhookDelivery, ContentBlock,
    MediaLibrary, TemplateReview, SEOSettings, SecurityLog
)

# Configure Gemini AI
if hasattr(settings, 'GEMINI_API_KEY'):
    genai.configure(api_key=settings.GEMINI_API_KEY)

def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def jwt_required(view_func):
    """JWT authentication decorator for template editor integration"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        jwt_auth = JWTAuthentication()
        try:
            # Try to authenticate with JWT token
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                validated_token = jwt_auth.get_validated_token(token)
                user = jwt_auth.get_user(validated_token)
                request.user = user
                request.jwt_authenticated = True
            else:
                # Fallback to session authentication for admin panel
                if not request.user.is_authenticated or not is_admin(request.user):
                    return JsonResponse({
                        'success': False,
                        'message': 'Authentication required. Please login or provide valid JWT token.'
                    }, status=401)
                request.jwt_authenticated = False
        except (InvalidToken, TokenError) as e:
            # Fallback to session authentication
            if not request.user.is_authenticated or not is_admin(request.user):
                return JsonResponse({
                    'success': False,
                    'message': f'Invalid JWT token: {str(e)}'
                }, status=401)
            request.jwt_authenticated = False
        
        return view_func(request, *args, **kwargs)
    return wrapper

def log_activity(user, action, model_name='', object_id='', object_repr='', description='', request=None):
    """Log admin activity"""
    ip_address = None
    user_agent = ''
    
    if request:
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    ActivityLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=str(object_id),
        object_repr=object_repr,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )

# Login and Authentication Views
def admin_login(request):
    """Admin login view"""
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin_panel:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')
        
        # Validate input
        if not username or not password:
            messages.error(request, 'Username dan password harus diisi.')
            return render(request, 'admin_panel/login.html')
        
        # Check if user exists
        try:
            user_exists = User.objects.filter(username=username).exists()
        except:
            user_exists = False
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if is_admin(user):
                if user.is_active:
                    login(request, user)
                    
                    # Set session expiry based on remember me
                    if not remember_me:
                        request.session.set_expiry(0)  # Session expires when browser closes
                    else:
                        request.session.set_expiry(1209600)  # 2 weeks
                    
                    log_activity(user, 'login', description='Admin login successful', request=request)
                    
                    # Redirect to next page or dashboard
                    next_page = request.GET.get('next', 'admin_panel:dashboard')
                    return redirect(next_page)
                else:
                    messages.error(request, 'Akun Anda telah dinonaktifkan. Hubungi administrator.')
                    log_activity(None, 'login_failed', description=f'Login attempt with inactive account: {username}', request=request)
            else:
                messages.error(request, 'Anda tidak memiliki akses administrator.')
                log_activity(None, 'login_failed', description=f'Login attempt without admin privileges: {username}', request=request)
        else:
            if user_exists:
                messages.error(request, 'Password yang Anda masukkan salah.')
                log_activity(None, 'login_failed', description=f'Wrong password for username: {username}', request=request)
            else:
                messages.error(request, 'Username tidak ditemukan.')
                log_activity(None, 'login_failed', description=f'Login attempt with non-existent username: {username}', request=request)
    
    return render(request, 'admin_panel/login.html')

def admin_logout(request):
    """Admin logout view"""
    if request.user.is_authenticated:
        log_activity(request.user, 'logout', description='Admin logout', request=request)
        logout(request)
        messages.success(request, 'Anda telah berhasil logout.')
    
    return redirect('admin_panel:login')

# API key login removed - using SQLite-only authentication

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard"""
    # Get statistics
    total_orders = Order.objects.count()
    total_templates = InvitationTemplate.objects.count()
    total_users = User.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    # Recent orders
    recent_orders = Order.objects.select_related('template').order_by('-created_at')[:5]
    
    # Revenue statistics
    today = timezone.now().date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    monthly_revenue = Order.objects.filter(
        created_at__gte=this_month,
        status='completed'
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    last_month_revenue = Order.objects.filter(
        created_at__gte=last_month,
        created_at__lt=this_month,
        status='completed'
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # Chart data for revenue over last 6 months
    chart_labels = []
    chart_data = []
    
    for i in range(5, -1, -1):
        month_date = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        next_month = (month_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        month_revenue = Order.objects.filter(
            created_at__gte=month_date,
            created_at__lt=next_month,
            status='completed'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        chart_labels.append(month_date.strftime('%b %Y'))
        chart_data.append(float(month_revenue))
    
    # Popular templates
    popular_templates = InvitationTemplate.objects.annotate(
        order_count=Count('order')
    ).order_by('-order_count')[:5]
    
    # Recent activities
    recent_activities = ActivityLog.objects.select_related('user').order_by('-created_at')[:10]
    
    # System alerts
    system_alerts = []
    
    # Check for pending feedbacks
    try:
        pending_feedbacks = CustomerFeedback.objects.filter(is_resolved=False).count()
        if pending_feedbacks > 0:
            system_alerts.append({
                'type': 'warning',
                'message': f'{pending_feedbacks} feedback belum ditanggapi'
            })
    except:
        pass
    
    # Check for failed payments
    try:
        failed_payments = PaymentTransaction.objects.filter(status='failed').count()
        if failed_payments > 0:
            system_alerts.append({
                'type': 'danger',
                'message': f'{failed_payments} pembayaran gagal'
            })
    except:
        pass
    
    context = {
        'total_orders': total_orders,
        'total_templates': total_templates,
        'total_users': total_users,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
        'monthly_revenue': monthly_revenue,
        'last_month_revenue': last_month_revenue,
        'popular_templates': popular_templates,
        'recent_activities': recent_activities,
        'system_alerts': system_alerts,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    
    log_activity(request.user, 'read', 'Dashboard', description='Viewed dashboard', request=request)
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_refresh(request):
    """AJAX endpoint to refresh dashboard data"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Method not allowed'})
    
    try:
        # Get updated statistics
        total_orders = Order.objects.count()
        total_templates = InvitationTemplate.objects.count()
        total_users = User.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        
        # Revenue statistics
        today = timezone.now().date()
        this_month = today.replace(day=1)
        
        monthly_revenue = Order.objects.filter(
            created_at__gte=this_month,
            status='completed'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        # Recent orders
        recent_orders = Order.objects.select_related('template').order_by('-created_at')[:5]
        recent_orders_data = []
        for order in recent_orders:
            recent_orders_data.append({
                'id': order.id,
                'customer_name': order.customer_name,
                'template_name': order.template.name if order.template else 'No Template',
                'total_amount': float(order.total_price),
                'status': order.status
            })
        
        # Recent activities
        recent_activities = ActivityLog.objects.select_related('user').order_by('-created_at')[:10]
        activities_data = []
        for activity in recent_activities:
            activities_data.append({
                'action': activity.action,
                'description': activity.description or f'{activity.action.title()} {activity.model_name} {activity.object_repr}',
                'time_ago': activity.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        # Chart data
        chart_labels = []
        chart_data = []
        
        for i in range(5, -1, -1):
            month_date = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
            next_month = (month_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            
            month_revenue = Order.objects.filter(
                created_at__gte=month_date,
                created_at__lt=next_month,
                status='completed'
            ).aggregate(total=Sum('total_price'))['total'] or 0
            
            chart_labels.append(month_date.strftime('%b %Y'))
            chart_data.append(float(month_revenue))
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_orders': total_orders,
                'total_templates': total_templates,
                'total_users': total_users,
                'monthly_revenue': float(monthly_revenue)
            },
            'recent_orders': recent_orders_data,
            'recent_activities': activities_data,
            'chart_data': {
                'labels': chart_labels,
                'data': chart_data
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

def orders_list(request):
    """List all orders with filtering and pagination"""
    orders = Order.objects.select_related('template').order_by('-created_at')
    
    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(
            Q(customer_name__icontains=search_query) |
            Q(customer_email__icontains=search_query) |
            Q(bride_name__icontains=search_query) |
            Q(groom_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'order_statuses': Order.STATUS_CHOICES,
    }
    
    return render(request, 'admin_panel/orders/list.html', context)

def order_detail(request, order_id):
    """Order detail view"""
    order = get_object_or_404(Order, id=order_id)
    
    # Get related data
    invitation_data = InvitationData.objects.filter(order=order).first()
    payment_transactions = PaymentTransaction.objects.filter(order=order).order_by('-created_at')
    
    context = {
        'order': order,
        'invitation_data': invitation_data,
        'payment_transactions': payment_transactions,
    }
    
    log_activity(request.user, 'read', 'Order', order.id, str(order), request=request)
    return render(request, 'admin_panel/orders/detail.html', context)

@require_POST
def update_order_status(request, order_id):
    """Update order status via AJAX"""
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    
    if new_status in dict(Order.STATUS_CHOICES):
        old_status = order.status
        order.status = new_status
        order.save()
        
        log_activity(
            request.user, 'update', 'Order', order.id, str(order),
            f'Status changed from {old_status} to {new_status}', request
        )
        
        # Send notification email if needed
        if new_status == 'completed':
            send_order_completion_email(order)
        
        return JsonResponse({
            'success': True,
            'message': 'Status order berhasil diupdate',
            'new_status': new_status
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Status tidak valid'
    })

def templates_list(request):
    """List all templates"""
    templates = InvitationTemplate.objects.annotate(
        order_count=Count('order')
    ).order_by('-created_at')
    
    # Filtering
    category_filter = request.GET.get('category')
    if category_filter:
        templates = templates.filter(category__slug=category_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        templates = templates.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(templates, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = TemplateCategory.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'category_filter': category_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin_panel/templates/list.html', context)

@login_required
@user_passes_test(is_admin)
@jwt_required
def create_template(request):
    """Create new template with JWT authentication for template editor integration"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        html_content = request.POST.get('html_content')
        preview_image = request.FILES.get('preview_image')
        
        template = InvitationTemplate.objects.create(
            name=name,
            description=description,
            html_content=html_content,
            preview_image=preview_image
        )
        
        # Create initial version
        TemplateVersion.objects.create(
            template=template,
            version_number='1.0',
            html_content=html_content,
            created_by=request.user,
            is_published=True
        )
        
        log_activity(
            request.user, 'create', 'InvitationTemplate', template.id, str(template),
            request=request
        )
        
        messages.success(request, 'Template berhasil dibuat!')
        return redirect('admin_panel:templates_list')
    
    categories = TemplateCategory.objects.filter(is_active=True)
    tags = TemplateTag.objects.all()
    
    context = {
        'categories': categories,
        'tags': tags,
    }
    
    return render(request, 'admin_panel/templates/create.html', context)

def edit_template(request, template_id):
    """Edit existing template"""
    template = get_object_or_404(InvitationTemplate, id=template_id)
    
    if request.method == 'POST':
        template.name = request.POST.get('name')
        template.description = request.POST.get('description')
        template.html_content = request.POST.get('html_content')
        
        if request.FILES.get('preview_image'):
            template.preview_image = request.FILES.get('preview_image')
        
        template.save()
        
        # Create new version if content changed
        latest_version = template.versions.order_by('-created_at').first()
        if not latest_version or latest_version.html_content != template.html_content:
            version_number = f"1.{template.versions.count()}"
            TemplateVersion.objects.create(
                template=template,
                version_number=version_number,
                html_content=template.html_content,
                created_by=request.user
            )
        
        log_activity(
            request.user, 'update', 'InvitationTemplate', template.id, str(template),
            request=request
        )
        
        messages.success(request, 'Template berhasil diupdate!')
        return redirect('admin_panel:templates_list')
    
    categories = TemplateCategory.objects.filter(is_active=True)
    tags = TemplateTag.objects.all()
    versions = template.versions.order_by('-created_at')[:10]
    
    context = {
        'template': template,
        'categories': categories,
        'tags': tags,
        'versions': versions,
    }
    
    return render(request, 'admin_panel/templates/edit.html', context)

# Template Editor Integration API
@csrf_exempt
@require_http_methods(["GET", "POST"])
@jwt_required
def template_editor_api(request):
    """API endpoint for template editor integration"""
    if request.method == 'GET':
        # Get templates from template_editor
        editor_templates = EditorTemplate.objects.filter(is_active=True).order_by('-created_at')
        templates_data = []
        
        for template in editor_templates:
            templates_data.append({
                'id': str(template.id),
                'name': template.name,
                'description': template.description,
                'category': template.category.name if template.category else '',
                'tags': [tag.name for tag in template.tags.all()],
                'preview_image': template.preview_image.url if template.preview_image else '',
                'is_premium': template.is_premium,
                'created_at': template.created_at.isoformat(),
                'usage_count': template.usage_count
            })
        
        return JsonResponse({
            'success': True,
            'templates': templates_data,
            'total': len(templates_data)
        })
    
    elif request.method == 'POST':
        # Create new template in main app from template_editor
        try:
            data = json.loads(request.body)
            editor_template_id = data.get('editor_template_id')
            
            if not editor_template_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Editor template ID is required'
                })
            
            editor_template = get_object_or_404(EditorTemplate, id=editor_template_id)
            
            # Create new InvitationTemplate from EditorTemplate
            invitation_template = InvitationTemplate.objects.create(
                name=data.get('name', editor_template.name),
                description=data.get('description', editor_template.description),
                html_content=editor_template.html_content,
                css_content=editor_template.css_content,
                js_content=editor_template.js_content,
                is_active=data.get('is_active', True)
            )
            
            # Create template version
            TemplateVersion.objects.create(
                template=invitation_template,
                version_number='1.0',
                html_content=editor_template.html_content,
                css_content=editor_template.css_content,
                js_content=editor_template.js_content,
                created_by=request.user,
                is_published=True,
                changelog=f'Imported from Template Editor (ID: {editor_template_id})'
            )
            
            log_activity(
                request.user, 'create', 'InvitationTemplate', invitation_template.id, 
                str(invitation_template), 
                f'Created from Template Editor template: {editor_template.name}', 
                request
            )
            
            return JsonResponse({
                'success': True,
                'template_id': invitation_template.id,
                'message': 'Template berhasil diimpor dari Template Editor'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error importing template: {str(e)}'
            })

@csrf_exempt
@require_http_methods(["POST"])
def generate_template_from_editor(request):
    """Generate new template using Template Editor API"""
    try:
        data = json.loads(request.body)
        
        # Template generation parameters
        template_data = {
            'name': data.get('name', 'Generated Template'),
            'description': data.get('description', ''),
            'category_id': data.get('category_id'),
            'tags': data.get('tags', []),
            'style_preferences': data.get('style_preferences', {}),
            'color_palette_id': data.get('color_palette_id'),
            'font_family_id': data.get('font_family_id'),
            'layout_id': data.get('layout_id'),
            'ai_prompt': data.get('ai_prompt', '')
        }
        
        # Create template in template_editor
        editor_template = EditorTemplate.objects.create(
            name=template_data['name'],
            description=template_data['description'],
            html_content=generate_html_content(template_data),
            css_content=generate_css_content(template_data),
            js_content=generate_js_content(template_data),
            category_id=template_data['category_id'],
            is_ai_generated=bool(template_data['ai_prompt']),
            ai_prompt=template_data['ai_prompt'],
            created_by=request.user
        )
        
        # Add tags
        if template_data['tags']:
            for tag_name in template_data['tags']:
                tag, created = EditorTemplateTag.objects.get_or_create(
                    name=tag_name,
                    defaults={'slug': tag_name.lower().replace(' ', '-')}
                )
                editor_template.tags.add(tag)
        
        # Set design elements
        if template_data['color_palette_id']:
            editor_template.color_palette_id = template_data['color_palette_id']
        if template_data['font_family_id']:
            editor_template.font_family_id = template_data['font_family_id']
        if template_data['layout_id']:
            editor_template.layout_id = template_data['layout_id']
        
        editor_template.save()
        
        log_activity(
            request.user, 'create', 'EditorTemplate', editor_template.id, 
            str(editor_template), 
            'Generated new template via Admin Panel', 
            request
        )
        
        return JsonResponse({
            'success': True,
            'editor_template_id': str(editor_template.id),
            'message': 'Template berhasil dibuat di Template Editor'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error generating template: {str(e)}'
        })

def generate_html_content(template_data):
    """Generate HTML content based on template data"""
    base_html = '''
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{name}</title>
    </head>
    <body>
        <div class="invitation-container">
            <header class="invitation-header">
                <h1>{name}</h1>
            </header>
            <main class="invitation-content">
                <p>{description}</p>
                <!-- Template content will be generated here -->
            </main>
        </div>
    </body>
    </html>
    '''.format(
        name=template_data.get('name', 'Wedding Invitation'),
        description=template_data.get('description', 'Beautiful wedding invitation')
    )
    return base_html

def generate_css_content(template_data):
    """Generate CSS content based on template data"""
    base_css = '''
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
        color: #333;
    }
    
    .invitation-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .invitation-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .invitation-header h1 {
        font-size: 2.5rem;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    
    .invitation-content {
        text-align: center;
    }
    '''
    return base_css

def generate_js_content(template_data):
    """Generate JavaScript content based on template data"""
    base_js = '''
    // Template JavaScript
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Template loaded successfully');
        
        // Add any interactive features here
    });
    '''
    return base_js

@login_required
def template_editor_integration(request):
    """Template Editor Integration page"""
    context = {
        'page_title': 'Template Editor Integration',
        'breadcrumbs': [
            {'name': 'Dashboard', 'url': reverse('admin_panel:dashboard')},
            {'name': 'Template Editor Integration', 'url': '#'}
        ]
    }
    return render(request, 'admin_panel/template_editor_integration.html', context)

@require_POST
def delete_template(request, template_id):
    """Delete template via AJAX"""
    template = get_object_or_404(InvitationTemplate, id=template_id)
    
    # Check if template has orders
    if template.order_set.exists():
        return JsonResponse({
            'success': False,
            'message': 'Template tidak dapat dihapus karena sudah digunakan dalam order'
        })
    
    template_name = str(template)
    template.delete()
    
    log_activity(
        request.user, 'delete', 'InvitationTemplate', template_id, template_name,
        request=request
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Template berhasil dihapus'
    })

def ai_content_generator(request):
    """AI content generator using Gemini"""
    if request.method == 'POST':
        prompt_type = request.POST.get('prompt_type')
        custom_prompt = request.POST.get('custom_prompt')
        template_id = request.POST.get('template_id')
        
        try:
            # Get or create AI prompt template
            prompt_template = None
            if prompt_type != 'custom':
                prompt_template = AIPromptTemplate.objects.filter(
                    prompt_type=prompt_type,
                    is_active=True
                ).first()
            
            # Prepare prompt
            if prompt_template:
                prompt_text = prompt_template.prompt_text
                prompt_template.usage_count += 1
                prompt_template.save()
            else:
                prompt_text = custom_prompt
            
            # Generate content using Gemini
            if hasattr(settings, 'GEMINI_API_KEY'):
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt_text)
                generated_content = response.text
                
                # Log generation
                AIGenerationHistory.objects.create(
                    user=request.user,
                    prompt_template=prompt_template,
                    input_prompt=prompt_text,
                    generated_content=generated_content,
                    status='completed',
                    tokens_used=len(prompt_text.split()) + len(generated_content.split())
                )
                
                return JsonResponse({
                    'success': True,
                    'content': generated_content
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Gemini API key tidak dikonfigurasi'
                })
                
        except Exception as e:
            # Log failed generation
            AIGenerationHistory.objects.create(
                user=request.user,
                prompt_template=prompt_template,
                input_prompt=prompt_text if 'prompt_text' in locals() else custom_prompt,
                status='failed',
                error_message=str(e)
            )
            
            return JsonResponse({
                'success': False,
                'message': f'Error generating content: {str(e)}'
            })
    
    # GET request - show form
    prompt_templates = AIPromptTemplate.objects.filter(is_active=True)
    recent_generations = AIGenerationHistory.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'prompt_templates': prompt_templates,
        'recent_generations': recent_generations,
    }
    
    return render(request, 'admin_panel/ai/content_generator.html', context)

def ai_prompt_templates(request):
    """Manage AI prompt templates"""
    templates = AIPromptTemplate.objects.order_by('prompt_type', 'name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            AIPromptTemplate.objects.create(
                name=request.POST.get('name'),
                prompt_type=request.POST.get('prompt_type'),
                prompt_text=request.POST.get('prompt_text'),
                variables=json.loads(request.POST.get('variables', '[]')),
                description=request.POST.get('description'),
                created_by=request.user
            )
            messages.success(request, 'Prompt template berhasil dibuat!')
        
        elif action == 'update':
            template_id = request.POST.get('template_id')
            template = get_object_or_404(AIPromptTemplate, id=template_id)
            template.name = request.POST.get('name')
            template.prompt_type = request.POST.get('prompt_type')
            template.prompt_text = request.POST.get('prompt_text')
            template.variables = json.loads(request.POST.get('variables', '[]'))
            template.description = request.POST.get('description')
            template.save()
            messages.success(request, 'Prompt template berhasil diupdate!')
        
        return redirect('admin_panel:ai_prompt_templates')
    
    context = {
        'templates': templates,
        'prompt_types': AIPromptTemplate.PROMPT_TYPES,
    }
    
    return render(request, 'admin_panel/ai/prompt_templates.html', context)

def customer_feedback(request):
    """Manage customer feedback"""
    feedbacks = CustomerFeedback.objects.select_related('order').order_by('-created_at')
    
    # Filtering
    status_filter = request.GET.get('status')
    if status_filter == 'resolved':
        feedbacks = feedbacks.filter(is_resolved=True)
    elif status_filter == 'unresolved':
        feedbacks = feedbacks.filter(is_resolved=False)
    
    type_filter = request.GET.get('type')
    if type_filter:
        feedbacks = feedbacks.filter(feedback_type=type_filter)
    
    # Pagination
    paginator = Paginator(feedbacks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'feedback_types': CustomerFeedback.FEEDBACK_TYPES,
    }
    
    return render(request, 'admin_panel/feedback/list.html', context)

@require_POST
def respond_feedback(request, feedback_id):
    """Respond to customer feedback"""
    feedback = get_object_or_404(CustomerFeedback, id=feedback_id)
    response_text = request.POST.get('response')
    
    feedback.admin_response = response_text
    feedback.is_resolved = True
    feedback.responded_by = request.user
    feedback.responded_at = timezone.now()
    feedback.save()
    
    # Send email response to customer
    try:
        send_mail(
            subject=f'Re: {feedback.subject}',
            message=response_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[feedback.customer_email],
            fail_silently=False,
        )
        
        # Log email
        EmailLog.objects.create(
            recipient_email=feedback.customer_email,
            recipient_name=feedback.customer_name,
            subject=f'Re: {feedback.subject}',
            content=response_text,
            status='sent',
            sent_at=timezone.now()
        )
        
    except Exception as e:
        EmailLog.objects.create(
            recipient_email=feedback.customer_email,
            recipient_name=feedback.customer_name,
            subject=f'Re: {feedback.subject}',
            content=response_text,
            status='failed',
            error_message=str(e)
        )
    
    log_activity(
        request.user, 'update', 'CustomerFeedback', feedback.id, str(feedback),
        'Responded to feedback', request
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Response berhasil dikirim'
    })

def analytics_dashboard(request):
    """Analytics dashboard"""
    # Date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    date_range = request.GET.get('range', '30')
    if date_range == '7':
        start_date = end_date - timedelta(days=7)
    elif date_range == '90':
        start_date = end_date - timedelta(days=90)
    elif date_range == '365':
        start_date = end_date - timedelta(days=365)
    
    # Order analytics
    orders_data = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).extra(
        select={'date': 'DATE(created_at)'}
    ).values('date').annotate(
        count=Count('id'),
        revenue=Sum('total_price')
    ).order_by('date')
    
    # Template popularity
    template_stats = InvitationTemplate.objects.annotate(
        order_count=Count('order', filter=Q(
            order__created_at__date__gte=start_date,
            order__created_at__date__lte=end_date
        ))
    ).order_by('-order_count')[:10]
    
    # User analytics
    user_registrations = User.objects.filter(
        date_joined__date__gte=start_date,
        date_joined__date__lte=end_date
    ).extra(
        select={'date': 'DATE(date_joined)'}
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Revenue by payment method
    payment_stats = PaymentTransaction.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status='completed'
    ).values('payment_method__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'orders_data': list(orders_data),
        'template_stats': template_stats,
        'user_registrations': list(user_registrations),
        'payment_stats': list(payment_stats),
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'admin_panel/analytics/dashboard.html', context)

def system_settings(request):
    """System settings management"""
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('setting_'):
                setting_key = key.replace('setting_', '')
                setting, created = SystemSettings.objects.get_or_create(
                    key=setting_key,
                    defaults={'value': value, 'setting_type': 'text'}
                )
                if not created:
                    setting.value = value
                    setting.save()
        
        messages.success(request, 'Pengaturan berhasil disimpan!')
        return redirect('admin_panel:system_settings')
    
    settings_by_category = {}
    for setting in SystemSettings.objects.all().order_by('category', 'key'):
        if setting.category not in settings_by_category:
            settings_by_category[setting.category] = []
        settings_by_category[setting.category].append(setting)
    
    context = {
        'settings_by_category': settings_by_category,
    }
    
    return render(request, 'admin_panel/settings/system.html', context)

def media_library(request):
    """Media library management"""
    media_files = MediaLibrary.objects.order_by('-created_at')
    
    # Filtering
    media_type = request.GET.get('type')
    if media_type:
        media_files = media_files.filter(media_type=media_type)
    
    search_query = request.GET.get('search')
    if search_query:
        media_files = media_files.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(media_files, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'media_types': MediaLibrary.MEDIA_TYPES,
        'media_type': media_type,
        'search_query': search_query,
    }
    
    return render(request, 'admin_panel/media/library.html', context)

@require_POST
def upload_media(request):
    """Upload media file"""
    try:
        file = request.FILES.get('file')
        name = request.POST.get('name', file.name)
        description = request.POST.get('description', '')
        
        # Determine media type
        mime_type = file.content_type
        if mime_type.startswith('image/'):
            media_type = 'image'
        elif mime_type.startswith('video/'):
            media_type = 'video'
        elif mime_type.startswith('audio/'):
            media_type = 'audio'
        else:
            media_type = 'document'
        
        # Get image dimensions if it's an image
        width = height = None
        if media_type == 'image':
            try:
                image = Image.open(file)
                width, height = image.size
            except:
                pass
        
        media_file = MediaLibrary.objects.create(
            name=name,
            file=file,
            media_type=media_type,
            file_size=file.size,
            mime_type=mime_type,
            width=width,
            height=height,
            description=description,
            uploaded_by=request.user
        )
        
        log_activity(
            request.user, 'create', 'MediaLibrary', media_file.id, str(media_file),
            request=request
        )
        
        return JsonResponse({
            'success': True,
            'message': 'File berhasil diupload',
            'file_id': media_file.id,
            'file_url': media_file.file.url
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error uploading file: {str(e)}'
        })

def backup_management(request):
    """Backup management"""
    schedules = BackupSchedule.objects.order_by('-created_at')
    backup_files = BackupFile.objects.order_by('-created_at')[:20]
    
    context = {
        'schedules': schedules,
        'backup_files': backup_files,
    }
    
    return render(request, 'admin_panel/backup/management.html', context)

@require_POST
def create_backup(request):
    """Create manual backup"""
    try:
        # Create backup filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_{timestamp}.json'
        
        # Collect data
        backup_data = {
            'timestamp': timestamp,
            'orders': list(Order.objects.values()),
            'templates': list(InvitationTemplate.objects.values()),
            'users': list(User.objects.values('id', 'username', 'email', 'first_name', 'last_name')),
            'settings': list(SystemSettings.objects.values()),
        }
        
        # Save to file
        backup_content = json.dumps(backup_data, indent=2, default=str)
        file_path = os.path.join(settings.MEDIA_ROOT, 'backups', filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(backup_content)
        
        # Create backup record
        backup_file = BackupFile.objects.create(
            filename=filename,
            file_path=file_path,
            file_size=len(backup_content.encode('utf-8')),
            status='completed',
            created_by=request.user
        )
        
        log_activity(
            request.user, 'backup', 'System', description='Manual backup created',
            request=request
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Backup berhasil dibuat',
            'filename': filename
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating backup: {str(e)}'
        })

def export_data(request):
    """Export data in various formats"""
    export_type = request.GET.get('type', 'orders')
    format_type = request.GET.get('format', 'csv')
    
    if export_type == 'orders':
        data = Order.objects.select_related('template').all()
        filename = f'orders_{timezone.now().strftime("%Y%m%d")}.{format_type}'
        
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            writer = csv.writer(response)
            writer.writerow([
                'ID', 'Customer Name', 'Email', 'Template', 'Status', 
                'Total Price', 'Created At'
            ])
            
            for order in data:
                writer.writerow([
                    order.id, order.customer_name, order.customer_email,
                    order.template.name, order.status, order.total_price,
                    order.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            return response
    
    return JsonResponse({'error': 'Invalid export parameters'})

def send_order_completion_email(order):
    """Send order completion email"""
    try:
        template = EmailTemplate.objects.filter(
            email_type='order_completed',
            is_active=True
        ).first()
        
        if template:
            subject = template.subject.format(
                customer_name=order.customer_name,
                order_id=order.id
            )
            
            content = template.html_content.format(
                customer_name=order.customer_name,
                order_id=order.id,
                template_name=order.template.name,
                bride_name=order.bride_name,
                groom_name=order.groom_name
            )
        else:
            subject = f'Order #{order.id} Completed'
            content = f'Dear {order.customer_name}, your order has been completed.'
        
        send_mail(
            subject=subject,
            message=content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=content,
            fail_silently=False,
        )
        
        # Log email
        EmailLog.objects.create(
            email_template=template,
            recipient_email=order.customer_email,
            recipient_name=order.customer_name,
            subject=subject,
            content=content,
            status='sent',
            sent_at=timezone.now()
        )
        
    except Exception as e:
        # Log failed email
        EmailLog.objects.create(
            recipient_email=order.customer_email,
            recipient_name=order.customer_name,
            subject=subject if 'subject' in locals() else 'Order Completed',
            content=content if 'content' in locals() else '',
            status='failed',
            error_message=str(e)
        )

# Additional utility views for AJAX operations

@require_POST
def toggle_template_status(request, template_id):
    """Toggle template active status"""
    template = get_object_or_404(InvitationTemplate, id=template_id)
    template.is_active = not template.is_active
    template.save()
    
    log_activity(
        request.user, 'update', 'InvitationTemplate', template.id, str(template),
        f'Status changed to {"active" if template.is_active else "inactive"}', request
    )
    
    return JsonResponse({
        'success': True,
        'is_active': template.is_active
    })

def get_template_preview(request, template_id):
    """Get template preview HTML"""
    template = get_object_or_404(InvitationTemplate, id=template_id)
    
    # Sample data for preview
    sample_data = {
        'bride_name': 'Sarah',
        'groom_name': 'John',
        'wedding_date': '2024-06-15',
        'wedding_time': '14:00',
        'venue_name': 'Grand Ballroom',
        'venue_address': '123 Wedding Street, City'
    }
    
    # Replace placeholders in HTML
    preview_html = template.html_content
    for key, value in sample_data.items():
        preview_html = preview_html.replace(f'{{{key}}}', str(value))
    
    return JsonResponse({
        'success': True,
        'html': preview_html
    })

def activity_logs(request):
    """View activity logs"""
    logs = ActivityLog.objects.select_related('user').order_by('-created_at')
    
    # Filtering
    user_filter = request.GET.get('user')
    if user_filter:
        logs = logs.filter(user_id=user_filter)
    
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    users = User.objects.filter(is_staff=True).order_by('username')
    
    context = {
        'page_obj': page_obj,
        'users': users,
        'user_filter': user_filter,
        'action_filter': action_filter,
        'action_choices': ActivityLog.ACTION_TYPES,
    }
    
    return render(request, 'admin_panel/logs/activity.html', context)

def security_logs(request):
    """View security logs"""
    logs = SecurityLog.objects.select_related('user').order_by('-created_at')
    
    # Filtering
    severity_filter = request.GET.get('severity')
    if severity_filter:
        logs = logs.filter(severity=severity_filter)
    
    event_filter = request.GET.get('event')
    if event_filter:
        logs = logs.filter(event_type=event_filter)
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'severity_filter': severity_filter,
        'event_filter': event_filter,
        'severity_choices': SecurityLog.SEVERITY_LEVELS,
        'event_choices': SecurityLog.EVENT_TYPES,
    }
    
    return render(request, 'admin_panel/logs/security.html', context)

# API endpoints for mobile responsiveness

def api_dashboard_stats(request):
    """API endpoint for dashboard statistics"""
    stats = {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_revenue': Order.objects.filter(status='completed').aggregate(
            total=Sum('total_price')
        )['total'] or 0,
        'total_templates': InvitationTemplate.objects.count(),
        'active_templates': InvitationTemplate.objects.filter(is_active=True).count(),
    }
    
    return JsonResponse(stats)

def api_recent_orders(request):
    """API endpoint for recent orders"""
    orders = Order.objects.select_related('template').order_by('-created_at')[:10]
    
    data = []
    for order in orders:
        data.append({
            'id': order.id,
            'customer_name': order.customer_name,
            'template_name': order.template.name,
            'status': order.status,
            'total_price': float(order.total_price),
            'created_at': order.created_at.isoformat()
        })
    
    return JsonResponse({'orders': data})

def api_template_stats(request):
    """API endpoint for template statistics"""
    templates = InvitationTemplate.objects.annotate(
        order_count=Count('order')
    ).order_by('-order_count')[:10]
    
    data = []
    for template in templates:
        data.append({
            'id': template.id,
            'name': template.name,
            'order_count': template.order_count,
            'is_active': template.is_active
        })
    
    return JsonResponse({'templates': data})

# Mobile-specific views

def mobile_dashboard(request):
    """Mobile-optimized dashboard"""
    context = {
        'is_mobile': True,
    }
    return render(request, 'admin_panel/mobile/dashboard.html', context)

def mobile_orders(request):
    """Mobile-optimized orders list"""
    orders = Order.objects.select_related('template').order_by('-created_at')[:20]
    
    context = {
        'orders': orders,
        'is_mobile': True,
    }
    return render(request, 'admin_panel/mobile/orders.html', context)

def mobile_templates(request):
    """Mobile-optimized templates list"""
    templates = InvitationTemplate.objects.order_by('-created_at')[:20]
    
    context = {
        'templates': templates,
        'is_mobile': True,
    }
    return render(request, 'admin_panel/mobile/templates.html', context)

# Template Editor Integration

@login_required
@user_passes_test(is_admin)
def template_editor_integration(request):
    """Template editor integration page"""
    context = {
        'page_title': 'Template Editor Integration',
    }
    return render(request, 'admin_panel/templates/editor_integration.html', context)

# Error handlers

def admin_404(request, exception):
    """Custom 404 page for admin panel"""
    return render(request, 'admin_panel/errors/404.html', status=404)

def admin_500(request):
    """Custom 500 page for admin panel"""
    return render(request, 'admin_panel/errors/500.html', status=500)
