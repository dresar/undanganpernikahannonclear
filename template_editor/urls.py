from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'template_editor'

urlpatterns = [
    # Main editor
    path('', views.editor_dashboard, name='editor_dashboard'),
    path('editor/', views.template_editor, name='editor'),
    path('editor/<uuid:template_id>/', views.template_editor, name='edit_template'),
    
    # Template management
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.create_template, name='create_template'),
    path('templates/<uuid:template_id>/update/', views.update_template, name='update_template'),
    path('templates/<uuid:template_id>/delete/', views.delete_template, name='delete_template'),
    path('templates/<uuid:template_id>/preview/', views.preview_template, name='preview_template'),
    # path('templates/<uuid:template_id>/publish/', views.publish_template, name='publish_template'),
    
    # Template gallery (public)
    path('gallery/', views.template_gallery, name='gallery'),
    path('gallery/template/<int:pk>/preview/', views.template_preview_public, name='template_preview_public'),
    path('gallery/template/<int:pk>/', views.template_preview_public, name='template_preview'),
    
    # Invitation management
    path('invitations/', views.my_invitations, name='my_invitations'),
    path('invitations/create/', views.create_invitation, name='create_invitation'),
    path('invitations/<slug:slug>/edit/', views.edit_invitation, name='edit_invitation'),
    path('invitations/<slug:slug>/preview/', views.invitation_preview, name='invitation_preview'),
    path('invitations/<slug:slug>/publish/', views.publish_invitation, name='publish_invitation'),
    
    # API endpoints
    path('api/templates/', views.api_templates, name='api_templates'),
    path('api/tools/', views.get_editor_tools, name='api_tools'),
    path('api/components/', views.get_components, name='api_components'),
    path('api/ai-generate/', views.generate_ai_content, name='api_ai_generate'),
    # path('api/save-template/', views.save_template, name='api_save_template'),
    path('api/export-template/', views.export_template, name='api_export_template'),
    path('api/template-preview/<int:template_id>/', views.get_template_preview_api, name='api_template_preview'),
    
    # ============================================================================
    # UNDANGAN URLS - Wedding Invitation Management
    # ============================================================================
    
    # Undangan CRUD
    path('undangan/create/', views.create_undangan, name='create_undangan'),
    path('undangan/create/<int:template_id>/', views.create_undangan, name='create_undangan_from_template'),
    path('undangan/edit/<slug:slug>/', views.edit_undangan, name='edit_undangan'),
    path('undangan/publish/<slug:slug>/', views.publish_undangan, name='publish_undangan'),
    path('undangan/dashboard/', views.undangan_dashboard, name='undangan_dashboard'),
    
    # Undangan display
    path('undangan/<slug:slug>/', views.undangan_detail, name='undangan_detail'),
    path('undangan/<slug:slug>/export/<str:format_type>/', views.export_undangan, name='export_undangan'),
    
    # AJAX endpoints for undangan
    path('undangan/<slug:slug>/comment/', views.add_guest_comment, name='add_guest_comment'),
]

# Add media files serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)