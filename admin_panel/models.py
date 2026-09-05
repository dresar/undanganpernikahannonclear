from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from main.models import InvitationTemplate, Order, InvitationData
import json
from datetime import datetime, timedelta

class AdminProfile(models.Model):
    """Profile untuk admin dengan informasi tambahan"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='admin/avatars/', blank=True)
    department = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    is_super_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Admin Profile - {self.user.username}"
    
    class Meta:
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"

class SystemSettings(models.Model):
    """Pengaturan sistem global"""
    SETTING_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('email', 'Email'),
        ('url', 'URL'),
        ('color', 'Color'),
        ('file', 'File'),
    ]
    
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='text')
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, default='general')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_value(self):
        """Mengembalikan nilai dengan tipe yang sesuai"""
        if self.setting_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes']
        elif self.setting_type == 'number':
            try:
                return float(self.value)
            except ValueError:
                return 0
        elif self.setting_type == 'json':
            try:
                return json.loads(self.value)
            except json.JSONDecodeError:
                return {}
        return self.value
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"
    
    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"
        ordering = ['category', 'key']

class ActivityLog(models.Model):
    """Log aktivitas admin"""
    ACTION_TYPES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('backup', 'Backup'),
        ('restore', 'Restore'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.model_name}"
    
    class Meta:
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        ordering = ['-created_at']

class TemplateCategory(models.Model):
    """Kategori template undangan"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code")
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Template Category"
        verbose_name_plural = "Template Categories"
        ordering = ['sort_order', 'name']

class TemplateTag(models.Model):
    """Tag untuk template"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#6B7280')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Template Tag"
        verbose_name_plural = "Template Tags"
        ordering = ['name']

class TemplateVersion(models.Model):
    """Versi template untuk tracking perubahan"""
    template = models.ForeignKey(InvitationTemplate, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=20)
    html_content = models.TextField()
    css_content = models.TextField(blank=True)
    js_content = models.TextField(blank=True)
    changelog = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_panel_template_versions')
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.template.name} v{self.version_number}"
    
    class Meta:
        verbose_name = "Template Version"
        verbose_name_plural = "Template Versions"
        ordering = ['-created_at']
        unique_together = ['template', 'version_number']

class AIPromptTemplate(models.Model):
    """Template prompt untuk AI generation"""
    PROMPT_TYPES = [
        ('template_generation', 'Template Generation'),
        ('content_suggestion', 'Content Suggestion'),
        ('design_improvement', 'Design Improvement'),
        ('color_scheme', 'Color Scheme'),
        ('layout_optimization', 'Layout Optimization'),
        ('text_enhancement', 'Text Enhancement'),
    ]
    
    name = models.CharField(max_length=100)
    prompt_type = models.CharField(max_length=30, choices=PROMPT_TYPES)
    prompt_text = models.TextField(help_text="Use {variables} for dynamic content")
    variables = models.JSONField(default=list, help_text="List of variable names")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_panel_ai_prompts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.prompt_type})"
    
    class Meta:
        verbose_name = "AI Prompt Template"
        verbose_name_plural = "AI Prompt Templates"
        ordering = ['prompt_type', 'name']

class AIGenerationHistory(models.Model):
    """Riwayat generasi AI"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt_template = models.ForeignKey(AIPromptTemplate, on_delete=models.CASCADE, null=True, blank=True)
    input_prompt = models.TextField()
    generated_content = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    processing_time = models.FloatField(null=True, blank=True)
    tokens_used = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"AI Generation #{self.id} - {self.status}"
    
    class Meta:
        verbose_name = "AI Generation History"
        verbose_name_plural = "AI Generation Histories"
        ordering = ['-created_at']

class CustomerFeedback(models.Model):
    """Feedback dari customer"""
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    FEEDBACK_TYPES = [
        ('general', 'General'),
        ('template', 'Template'),
        ('service', 'Service'),
        ('bug_report', 'Bug Report'),
        ('feature_request', 'Feature Request'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='general')
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_public = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    admin_response = models.TextField(blank=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.customer_name} - {self.subject}"
    
    class Meta:
        verbose_name = "Customer Feedback"
        verbose_name_plural = "Customer Feedbacks"
        ordering = ['-created_at']

class EmailTemplate(models.Model):
    """Template email untuk berbagai keperluan"""
    EMAIL_TYPES = [
        ('order_confirmation', 'Order Confirmation'),
        ('payment_received', 'Payment Received'),
        ('order_completed', 'Order Completed'),
        ('welcome', 'Welcome'),
        ('newsletter', 'Newsletter'),
        ('promotion', 'Promotion'),
        ('reminder', 'Reminder'),
        ('feedback_request', 'Feedback Request'),
    ]
    
    name = models.CharField(max_length=100)
    email_type = models.CharField(max_length=30, choices=EMAIL_TYPES)
    subject = models.CharField(max_length=200)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    variables = models.JSONField(default=list, help_text="Available variables for this template")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.email_type})"
    
    class Meta:
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"
        ordering = ['email_type', 'name']

class EmailLog(models.Model):
    """Log pengiriman email"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
    ]
    
    email_template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, null=True, blank=True)
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Email to {self.recipient_email} - {self.status}"
    
    class Meta:
        verbose_name = "Email Log"
        verbose_name_plural = "Email Logs"
        ordering = ['-created_at']

class PaymentMethod(models.Model):
    """Metode pembayaran yang tersedia"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='payment/icons/', blank=True)
    is_active = models.BooleanField(default=True)
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fee_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    api_config = models.JSONField(default=dict, blank=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_fee(self, amount):
        """Menghitung biaya untuk jumlah tertentu"""
        percentage_fee = amount * (self.fee_percentage / 100)
        return percentage_fee + self.fee_fixed
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"
        ordering = ['sort_order', 'name']

class PaymentTransaction(models.Model):
    """Transaksi pembayaran"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    external_id = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_url = models.URLField(blank=True)
    callback_data = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"
    
    class Meta:
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"
        ordering = ['-created_at']

class Discount(models.Model):
    """Diskon dan kupon"""
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_valid(self):
        """Cek apakah diskon masih valid"""
        now = timezone.now()
        return (self.is_active and 
                self.valid_from <= now <= self.valid_until and
                (self.usage_limit is None or self.usage_count < self.usage_limit))
    
    def calculate_discount(self, amount):
        """Menghitung jumlah diskon"""
        if not self.is_valid() or amount < self.min_order_amount:
            return 0
        
        if self.discount_type == 'percentage':
            discount = amount * (self.value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return discount
        elif self.discount_type == 'fixed':
            return min(self.value, amount)
        return 0
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        verbose_name = "Discount"
        verbose_name_plural = "Discounts"
        ordering = ['-created_at']

class Analytics(models.Model):
    """Data analytics dan statistik"""
    METRIC_TYPES = [
        ('page_view', 'Page View'),
        ('template_view', 'Template View'),
        ('order_created', 'Order Created'),
        ('payment_completed', 'Payment Completed'),
        ('email_sent', 'Email Sent'),
        ('user_registration', 'User Registration'),
        ('search_query', 'Search Query'),
    ]
    
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    metric_name = models.CharField(max_length=100)
    value = models.FloatField(default=1)
    dimensions = models.JSONField(default=dict, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.metric_type} - {self.metric_name}"
    
    class Meta:
        verbose_name = "Analytics"
        verbose_name_plural = "Analytics"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['metric_type', 'created_at']),
            models.Index(fields=['created_at']),
        ]

class BackupSchedule(models.Model):
    """Jadwal backup otomatis"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    name = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    time = models.TimeField()
    is_active = models.BooleanField(default=True)
    include_media = models.BooleanField(default=True)
    retention_days = models.IntegerField(default=30)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.frequency}"
    
    class Meta:
        verbose_name = "Backup Schedule"
        verbose_name_plural = "Backup Schedules"

class BackupFile(models.Model):
    """File backup yang tersimpan"""
    STATUS_CHOICES = [
        ('creating', 'Creating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    schedule = models.ForeignKey(BackupSchedule, on_delete=models.CASCADE, null=True, blank=True)
    filename = models.CharField(max_length=200)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='creating')
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename
    
    class Meta:
        verbose_name = "Backup File"
        verbose_name_plural = "Backup Files"
        ordering = ['-created_at']

class NotificationTemplate(models.Model):
    """Template notifikasi untuk berbagai event"""
    NOTIFICATION_TYPES = [
        ('order_status', 'Order Status Update'),
        ('payment_reminder', 'Payment Reminder'),
        ('system_alert', 'System Alert'),
        ('marketing', 'Marketing'),
        ('maintenance', 'Maintenance'),
        ('security', 'Security Alert'),
    ]
    
    DELIVERY_METHODS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
    ]
    
    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS)
    subject = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    variables = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.delivery_method})"
    
    class Meta:
        verbose_name = "Notification Template"
        verbose_name_plural = "Notification Templates"
        ordering = ['notification_type', 'name']

class NotificationQueue(models.Model):
    """Antrian notifikasi yang akan dikirim"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    recipient = models.CharField(max_length=200)
    subject = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification to {self.recipient} - {self.status}"
    
    class Meta:
        verbose_name = "Notification Queue"
        verbose_name_plural = "Notification Queues"
        ordering = ['-created_at']

# API Key models removed - migrating to SQLite-only authentication

class WebhookEndpoint(models.Model):
    """Webhook endpoints untuk notifikasi eksternal"""
    EVENT_TYPES = [
        ('order.created', 'Order Created'),
        ('order.updated', 'Order Updated'),
        ('payment.completed', 'Payment Completed'),
        ('template.published', 'Template Published'),
        ('user.registered', 'User Registered'),
    ]
    
    name = models.CharField(max_length=100)
    url = models.URLField()
    event_types = models.JSONField(default=list, help_text="List of event types to listen for")
    is_active = models.BooleanField(default=True)
    secret = models.CharField(max_length=255, blank=True)
    headers = models.JSONField(default=dict, blank=True)
    timeout = models.IntegerField(default=30)
    retry_count = models.IntegerField(default=3)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.url}"
    
    class Meta:
        verbose_name = "Webhook Endpoint"
        verbose_name_plural = "Webhook Endpoints"
        ordering = ['name']

class WebhookDelivery(models.Model):
    """Log pengiriman webhook"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_status = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    attempt_count = models.IntegerField(default=0)
    next_retry = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.endpoint.name} - {self.event_type} - {self.status}"
    
    class Meta:
        verbose_name = "Webhook Delivery"
        verbose_name_plural = "Webhook Deliveries"
        ordering = ['-created_at']

class ContentBlock(models.Model):
    """Blok konten yang dapat digunakan kembali"""
    BLOCK_TYPES = [
        ('text', 'Text Block'),
        ('image', 'Image Block'),
        ('gallery', 'Image Gallery'),
        ('video', 'Video Block'),
        ('map', 'Map Block'),
        ('countdown', 'Countdown Timer'),
        ('rsvp', 'RSVP Form'),
        ('contact', 'Contact Info'),
    ]
    
    name = models.CharField(max_length=100)
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES)
    content = models.JSONField(default=dict)
    html_template = models.TextField(blank=True)
    css_styles = models.TextField(blank=True)
    js_code = models.TextField(blank=True)
    is_reusable = models.BooleanField(default=True)
    category = models.CharField(max_length=50, blank=True)
    tags = models.ManyToManyField(TemplateTag, blank=True)
    usage_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.block_type})"
    
    class Meta:
        verbose_name = "Content Block"
        verbose_name_plural = "Content Blocks"
        ordering = ['category', 'name']

class MediaLibrary(models.Model):
    """Library media untuk template"""
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
    ]
    
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='media_library/')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    file_size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(TemplateTag, blank=True)
    is_public = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Media Library"
        verbose_name_plural = "Media Libraries"
        ordering = ['-created_at']

class TemplateReview(models.Model):
    """Review dan rating template"""
    template = models.ForeignKey(InvitationTemplate, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    reviewer_name = models.CharField(max_length=100)
    reviewer_email = models.EmailField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for {self.template.name} - {self.rating} stars"
    
    class Meta:
        verbose_name = "Template Review"
        verbose_name_plural = "Template Reviews"
        ordering = ['-created_at']
        unique_together = ['template', 'reviewer_email']

class SEOSettings(models.Model):
    """Pengaturan SEO untuk halaman"""
    page_type = models.CharField(max_length=50, unique=True)
    title_template = models.CharField(max_length=200)
    meta_description = models.TextField(max_length=160)
    meta_keywords = models.TextField(blank=True)
    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.TextField(max_length=300, blank=True)
    og_image = models.ImageField(upload_to='seo/og_images/', blank=True)
    canonical_url = models.URLField(blank=True)
    robots_meta = models.CharField(max_length=100, default='index,follow')
    schema_markup = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"SEO Settings - {self.page_type}"
    
    class Meta:
        verbose_name = "SEO Setting"
        verbose_name_plural = "SEO Settings"
        ordering = ['page_type']

class SecurityLog(models.Model):
    """Log keamanan sistem"""
    EVENT_TYPES = [
        ('login_success', 'Login Success'),
        ('login_failed', 'Login Failed'),
        ('password_changed', 'Password Changed'),
        ('permission_denied', 'Permission Denied'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('data_breach_attempt', 'Data Breach Attempt'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='low')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    path = models.CharField(max_length=500, blank=True)  # URL path yang diakses
    method = models.CharField(max_length=10, blank=True)  # HTTP method
    timestamp = models.DateTimeField(auto_now_add=True)  # Alias untuk created_at
    description = models.TextField()
    additional_data = models.JSONField(default=dict, blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_security_logs')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.event_type} - {self.severity} - {self.created_at}"
    
    class Meta:
        verbose_name = "Security Log"
        verbose_name_plural = "Security Logs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['severity', 'created_at']),
        ]
