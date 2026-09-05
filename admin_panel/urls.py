from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Authentication URLs
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    # API endpoints removed - using SQLite-only authentication
    
    # Dashboard URLs (require authentication)
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/refresh/', views.dashboard_refresh, name='dashboard_refresh'),
    path('mobile/dashboard/', views.mobile_dashboard, name='mobile_dashboard'),
    
    # Order Management URLs
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/list/', views.orders_list, name='orders_list_alt'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/detail/', views.order_detail, name='order_detail_alt'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/status/', views.update_order_status, name='order_status_update'),
    path('mobile/orders/', views.mobile_orders, name='mobile_orders'),
    
    # Template Management URLs
    path('templates/', views.templates_list, name='templates_list'),
    path('templates/list/', views.templates_list, name='templates_list_alt'),
    path('templates/create/', views.create_template, name='create_template'),
    path('templates/new/', views.create_template, name='new_template'),
    path('templates/<int:template_id>/edit/', views.edit_template, name='edit_template'),
    path('templates/<int:template_id>/update/', views.edit_template, name='update_template'),
    path('templates/<int:template_id>/delete/', views.delete_template, name='delete_template'),
    path('templates/<int:template_id>/remove/', views.delete_template, name='remove_template'),
    path('templates/<int:template_id>/toggle-status/', views.toggle_template_status, name='toggle_template_status'),
    path('templates/<int:template_id>/status/', views.toggle_template_status, name='template_status'),
    path('templates/<int:template_id>/preview/', views.get_template_preview, name='template_preview'),
    path('mobile/templates/', views.mobile_templates, name='mobile_templates'),
    
    # AI Content Generator URLs
    path('ai/', views.ai_content_generator, name='ai_content_generator'),
    path('ai/generator/', views.ai_content_generator, name='ai_generator'),
    path('ai/content/', views.ai_content_generator, name='ai_content'),
    path('ai/generate/', views.ai_content_generator, name='ai_generate'),
    path('ai/prompts/', views.ai_prompt_templates, name='ai_prompt_templates'),
    path('ai/prompt-templates/', views.ai_prompt_templates, name='ai_prompts'),
    path('ai/templates/', views.ai_prompt_templates, name='ai_template_prompts'),
    
    # Customer Feedback URLs
    path('feedback/', views.customer_feedback, name='customer_feedback'),
    path('feedback/list/', views.customer_feedback, name='feedback_list'),
    path('feedback/customer/', views.customer_feedback, name='feedback_customer'),
    path('feedback/<int:feedback_id>/respond/', views.respond_feedback, name='respond_feedback'),
    path('feedback/<int:feedback_id>/reply/', views.respond_feedback, name='reply_feedback'),
    path('feedback/<int:feedback_id>/response/', views.respond_feedback, name='feedback_response'),
    
    # Analytics URLs
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/dashboard/', views.analytics_dashboard, name='analytics'),
    path('analytics/reports/', views.analytics_dashboard, name='analytics_reports'),
    path('analytics/stats/', views.analytics_dashboard, name='analytics_stats'),
    
    # System Settings URLs
    path('settings/', views.system_settings, name='system_settings'),
    path('settings/system/', views.system_settings, name='settings_system'),
    path('settings/general/', views.system_settings, name='general_settings'),
    path('config/', views.system_settings, name='config'),
    path('configuration/', views.system_settings, name='configuration'),
    
    # Media Library URLs
    path('media/', views.media_library, name='media_library'),
    path('media/library/', views.media_library, name='media_lib'),
    path('media/files/', views.media_library, name='media_files'),
    path('media/upload/', views.upload_media, name='upload_media'),
    path('media/upload-file/', views.upload_media, name='upload_file'),
    path('upload/', views.upload_media, name='media_upload'),
    
    # Backup Management URLs
    path('backup/', views.backup_management, name='backup_management'),
    path('backup/management/', views.backup_management, name='backup_mgmt'),
    path('backup/list/', views.backup_management, name='backup_list'),
    path('backup/create/', views.create_backup, name='create_backup'),
    path('backup/new/', views.create_backup, name='new_backup'),
    path('backup/generate/', views.create_backup, name='generate_backup'),
    
    # Data Export URLs
    path('export/', views.export_data, name='export_data'),
    path('export/data/', views.export_data, name='data_export'),
    path('export/orders/', views.export_data, name='export_orders'),
    path('export/templates/', views.export_data, name='export_templates'),
    path('export/users/', views.export_data, name='export_users'),
    
    # Activity Logs URLs
    path('logs/', views.activity_logs, name='activity_logs'),
    path('logs/activity/', views.activity_logs, name='logs_activity'),
    path('logs/admin/', views.activity_logs, name='admin_logs'),
    path('activity/', views.activity_logs, name='activity'),
    path('audit/', views.activity_logs, name='audit_logs'),
    
    # Security Logs URLs
    path('logs/security/', views.security_logs, name='security_logs'),
    path('security/', views.security_logs, name='security'),
    path('security/logs/', views.security_logs, name='sec_logs'),
    path('audit/security/', views.security_logs, name='security_audit'),
    
    # API Endpoints for AJAX/Mobile
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/dashboard/statistics/', views.api_dashboard_stats, name='api_stats'),
    path('api/stats/', views.api_dashboard_stats, name='api_statistics'),
    path('api/orders/recent/', views.api_recent_orders, name='api_recent_orders'),
    path('api/orders/latest/', views.api_recent_orders, name='api_latest_orders'),
    path('api/templates/stats/', views.api_template_stats, name='api_template_stats'),
    path('api/templates/statistics/', views.api_template_stats, name='api_template_statistics'),
    
    # Template Editor Integration API
    path('api/template-editor/', views.template_editor_api, name='template_editor_api'),
    path('api/generate-template/', views.generate_template_from_editor, name='generate_template_from_editor'),
    
    # Template Editor Integration Page
    path('template-editor-integration/', views.template_editor_integration, name='template_editor_integration'),
    
    # Additional Management URLs
    path('users/', views.dashboard, name='users_management'),  # Placeholder
    path('users/list/', views.dashboard, name='users_list'),  # Placeholder
    path('users/create/', views.dashboard, name='create_user'),  # Placeholder
    path('users/edit/<int:user_id>/', views.dashboard, name='edit_user'),  # Placeholder
    path('users/delete/<int:user_id>/', views.dashboard, name='delete_user'),  # Placeholder
    
    # Email Management URLs
    path('emails/', views.dashboard, name='email_management'),  # Placeholder
    path('emails/templates/', views.dashboard, name='email_templates'),  # Placeholder
    path('emails/logs/', views.dashboard, name='email_logs'),  # Placeholder
    path('emails/send/', views.dashboard, name='send_email'),  # Placeholder
    path('emails/queue/', views.dashboard, name='email_queue'),  # Placeholder
    
    # Payment Management URLs
    path('payments/', views.dashboard, name='payment_management'),  # Placeholder
    path('payments/methods/', views.dashboard, name='payment_methods'),  # Placeholder
    path('payments/transactions/', views.dashboard, name='payment_transactions'),  # Placeholder
    path('payments/refunds/', views.dashboard, name='payment_refunds'),  # Placeholder
    path('payments/reports/', views.dashboard, name='payment_reports'),  # Placeholder
    
    # Discount Management URLs
    path('discounts/', views.dashboard, name='discount_management'),  # Placeholder
    path('discounts/list/', views.dashboard, name='discounts_list'),  # Placeholder
    path('discounts/create/', views.dashboard, name='create_discount'),  # Placeholder
    path('discounts/edit/<int:discount_id>/', views.dashboard, name='edit_discount'),  # Placeholder
    path('discounts/delete/<int:discount_id>/', views.dashboard, name='delete_discount'),  # Placeholder
    
    # Category Management URLs
    path('categories/', views.dashboard, name='category_management'),  # Placeholder
    path('categories/list/', views.dashboard, name='categories_list'),  # Placeholder
    path('categories/create/', views.dashboard, name='create_category'),  # Placeholder
    path('categories/edit/<int:category_id>/', views.dashboard, name='edit_category'),  # Placeholder
    path('categories/delete/<int:category_id>/', views.dashboard, name='delete_category'),  # Placeholder
    
    # Tag Management URLs
    path('tags/', views.dashboard, name='tag_management'),  # Placeholder
    path('tags/list/', views.dashboard, name='tags_list'),  # Placeholder
    path('tags/create/', views.dashboard, name='create_tag'),  # Placeholder
    path('tags/edit/<int:tag_id>/', views.dashboard, name='edit_tag'),  # Placeholder
    path('tags/delete/<int:tag_id>/', views.dashboard, name='delete_tag'),  # Placeholder
    
    # Review Management URLs
    path('reviews/', views.dashboard, name='review_management'),  # Placeholder
    path('reviews/list/', views.dashboard, name='reviews_list'),  # Placeholder
    path('reviews/moderate/', views.dashboard, name='moderate_reviews'),  # Placeholder
    path('reviews/approve/<int:review_id>/', views.dashboard, name='approve_review'),  # Placeholder
    path('reviews/reject/<int:review_id>/', views.dashboard, name='reject_review'),  # Placeholder
    
    # SEO Management URLs
    path('seo/', views.dashboard, name='seo_management'),  # Placeholder
    path('seo/settings/', views.dashboard, name='seo_settings'),  # Placeholder
    path('seo/meta/', views.dashboard, name='seo_meta'),  # Placeholder
    path('seo/sitemap/', views.dashboard, name='seo_sitemap'),  # Placeholder
    path('seo/robots/', views.dashboard, name='seo_robots'),  # Placeholder
    
    # API Key Management removed - using SQLite-only authentication
    
    # Webhook Management URLs
    path('webhooks/', views.dashboard, name='webhook_management'),  # Placeholder
    path('webhooks/list/', views.dashboard, name='webhooks_list'),  # Placeholder
    path('webhooks/create/', views.dashboard, name='create_webhook'),  # Placeholder
    path('webhooks/edit/<int:webhook_id>/', views.dashboard, name='edit_webhook'),  # Placeholder
    path('webhooks/delete/<int:webhook_id>/', views.dashboard, name='delete_webhook'),  # Placeholder
    path('webhooks/test/<int:webhook_id>/', views.dashboard, name='test_webhook'),  # Placeholder
    
    # Notification Management URLs
    path('notifications/', views.dashboard, name='notification_management'),  # Placeholder
    path('notifications/templates/', views.dashboard, name='notification_templates'),  # Placeholder
    path('notifications/queue/', views.dashboard, name='notification_queue'),  # Placeholder
    path('notifications/send/', views.dashboard, name='send_notification'),  # Placeholder
    path('notifications/history/', views.dashboard, name='notification_history'),  # Placeholder
    
    # Content Block Management URLs
    path('content/', views.dashboard, name='content_management'),  # Placeholder
    path('content/blocks/', views.dashboard, name='content_blocks'),  # Placeholder
    path('content/create/', views.dashboard, name='create_content'),  # Placeholder
    path('content/edit/<int:content_id>/', views.dashboard, name='edit_content'),  # Placeholder
    path('content/delete/<int:content_id>/', views.dashboard, name='delete_content'),  # Placeholder
    
    # System Monitoring URLs
    path('monitoring/', views.dashboard, name='system_monitoring'),  # Placeholder
    path('monitoring/performance/', views.dashboard, name='performance_monitoring'),  # Placeholder
    path('monitoring/errors/', views.dashboard, name='error_monitoring'),  # Placeholder
    path('monitoring/uptime/', views.dashboard, name='uptime_monitoring'),  # Placeholder
    path('monitoring/resources/', views.dashboard, name='resource_monitoring'),  # Placeholder
    
    # Cache Management URLs
    path('cache/', views.dashboard, name='cache_management'),  # Placeholder
    path('cache/clear/', views.dashboard, name='clear_cache'),  # Placeholder
    path('cache/stats/', views.dashboard, name='cache_stats'),  # Placeholder
    path('cache/keys/', views.dashboard, name='cache_keys'),  # Placeholder
    
    # Database Management URLs
    path('database/', views.dashboard, name='database_management'),  # Placeholder
    path('database/optimize/', views.dashboard, name='optimize_database'),  # Placeholder
    path('database/repair/', views.dashboard, name='repair_database'),  # Placeholder
    path('database/stats/', views.dashboard, name='database_stats'),  # Placeholder
    path('database/queries/', views.dashboard, name='database_queries'),  # Placeholder
    
    # File Management URLs
    path('files/', views.dashboard, name='file_management'),  # Placeholder
    path('files/cleanup/', views.dashboard, name='file_cleanup'),  # Placeholder
    path('files/orphaned/', views.dashboard, name='orphaned_files'),  # Placeholder
    path('files/storage/', views.dashboard, name='storage_stats'),  # Placeholder
    
    # Import/Export URLs
    path('import/', views.dashboard, name='import_data'),  # Placeholder
    path('import/orders/', views.dashboard, name='import_orders'),  # Placeholder
    path('import/templates/', views.dashboard, name='import_templates'),  # Placeholder
    path('import/users/', views.dashboard, name='import_users'),  # Placeholder
    
    # Maintenance URLs
    path('maintenance/', views.dashboard, name='maintenance_mode'),  # Placeholder
    path('maintenance/enable/', views.dashboard, name='enable_maintenance'),  # Placeholder
    path('maintenance/disable/', views.dashboard, name='disable_maintenance'),  # Placeholder
    path('maintenance/status/', views.dashboard, name='maintenance_status'),  # Placeholder
    
    # Help & Documentation URLs
    path('help/', views.dashboard, name='help_center'),  # Placeholder
    path('help/docs/', views.dashboard, name='documentation'),  # Placeholder
    path('help/api/', views.dashboard, name='api_documentation'),  # Placeholder
    path('help/faq/', views.dashboard, name='faq'),  # Placeholder
    path('help/support/', views.dashboard, name='support'),  # Placeholder
    
    # Profile Management URLs
    path('profile/', views.dashboard, name='admin_profile'),  # Placeholder
    path('profile/edit/', views.dashboard, name='edit_profile'),  # Placeholder
    path('profile/password/', views.dashboard, name='change_password'),  # Placeholder
    path('profile/preferences/', views.dashboard, name='user_preferences'),  # Placeholder
    
    # Quick Actions URLs
    path('quick/order-status/', views.dashboard, name='quick_order_status'),  # Placeholder
    path('quick/template-toggle/', views.dashboard, name='quick_template_toggle'),  # Placeholder
    path('quick/backup/', views.dashboard, name='quick_backup'),  # Placeholder
    path('quick/clear-cache/', views.dashboard, name='quick_clear_cache'),  # Placeholder
    
    # Bulk Actions URLs
    path('bulk/orders/', views.dashboard, name='bulk_orders'),  # Placeholder
    path('bulk/templates/', views.dashboard, name='bulk_templates'),  # Placeholder
    path('bulk/users/', views.dashboard, name='bulk_users'),  # Placeholder
    path('bulk/delete/', views.dashboard, name='bulk_delete'),  # Placeholder
    path('bulk/export/', views.dashboard, name='bulk_export'),  # Placeholder
    
    # Search URLs
    path('search/', views.dashboard, name='global_search'),  # Placeholder
    path('search/orders/', views.dashboard, name='search_orders'),  # Placeholder
    path('search/templates/', views.dashboard, name='search_templates'),  # Placeholder
    path('search/users/', views.dashboard, name='search_users'),  # Placeholder
    
    # Advanced Features URLs
    path('advanced/', views.dashboard, name='advanced_features'),  # Placeholder
    path('advanced/scheduler/', views.dashboard, name='task_scheduler'),  # Placeholder
    path('advanced/automation/', views.dashboard, name='automation'),  # Placeholder
    path('advanced/workflows/', views.dashboard, name='workflows'),  # Placeholder
    path('advanced/integrations/', views.dashboard, name='integrations'),  # Placeholder
    
    # Error Handling URLs
    path('errors/404/', views.admin_404, name='admin_404'),
    path('errors/500/', views.admin_500, name='admin_500'),
    path('errors/403/', views.dashboard, name='admin_403'),  # Placeholder
    path('errors/400/', views.dashboard, name='admin_400'),  # Placeholder
]

# Add static file serving for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)