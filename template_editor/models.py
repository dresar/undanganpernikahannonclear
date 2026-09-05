from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse
import uuid
import json

class TemplateCategory(models.Model):
    """
    Categories for organizing templates
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-folder')
    color = models.CharField(max_length=7, default='#667eea')
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Template Categories'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while TemplateCategory.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

class TemplateTag(models.Model):
    """
    Tags for template classification and search
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#6b7280')
    usage_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return self.name

class ColorPalette(models.Model):
    """
    Color palettes for templates
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    primary_color = models.CharField(max_length=7, help_text='Primary color hex code')
    secondary_color = models.CharField(max_length=7, help_text='Secondary color hex code')
    accent_color = models.CharField(max_length=7, help_text='Accent color hex code')
    background_color = models.CharField(max_length=7, default='#ffffff')
    text_color = models.CharField(max_length=7, default='#333333')
    colors_json = models.JSONField(default=dict, help_text='Additional colors as JSON')
    preview_image = models.ImageField(upload_to='color_palettes/', blank=True)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class FontFamily(models.Model):
    """
    Font families for templates
    """
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100, default='', help_text='Name to display to users')
    font_family_css = models.CharField(max_length=200, default='', help_text='CSS font-family value')
    google_fonts_url = models.URLField(blank=True, help_text='Google Fonts URL if applicable')
    font_files = models.JSONField(default=list, help_text='Local font file paths')
    preview_text = models.CharField(max_length=200, default='The quick brown fox jumps over the lazy dog')
    category = models.CharField(max_length=50, choices=[
        ('serif', 'Serif'),
        ('sans-serif', 'Sans Serif'),
        ('monospace', 'Monospace'),
        ('cursive', 'Cursive'),
        ('fantasy', 'Fantasy'),
        ('display', 'Display')
    ], default='sans-serif')
    is_web_safe = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.display_name

class TemplateStyle(models.Model):
    """
    Predefined styles for templates
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    css_variables = models.JSONField(default=dict, help_text='CSS custom properties as JSON')
    preview_image = models.ImageField(upload_to='template_styles/', blank=True)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class TemplateLayout(models.Model):
    """
    Template layout structures
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    html_structure = models.TextField(help_text='Base HTML structure')
    css_framework = models.CharField(max_length=50, choices=[
        ('custom', 'Custom CSS'),
        ('bootstrap', 'Bootstrap'),
        ('tailwind', 'Tailwind CSS'),
        ('bulma', 'Bulma'),
        ('foundation', 'Foundation')
    ], default='custom')
    responsive_breakpoints = models.JSONField(default=dict)
    preview_image = models.ImageField(upload_to='template_layouts/', blank=True)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class TemplateComponent(models.Model):
    """
    Reusable template components
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    component_type = models.CharField(max_length=50, choices=[
        ('header', 'Header'),
        ('footer', 'Footer'),
        ('content', 'Content Block'),
        ('sidebar', 'Sidebar'),
        ('navigation', 'Navigation'),
        ('form', 'Form'),
        ('gallery', 'Gallery'),
        ('testimonial', 'Testimonial'),
        ('pricing', 'Pricing'),
        ('contact', 'Contact'),
        ('countdown', 'Countdown Timer'),
        ('map', 'Map'),
        ('social', 'Social Media'),
        ('rsvp', 'RSVP Form')
    ])
    html_code = models.TextField()
    css_code = models.TextField(blank=True)
    js_code = models.TextField(blank=True)
    dependencies = models.JSONField(default=list, help_text='Required CSS/JS dependencies')
    customizable_fields = models.JSONField(default=list, help_text='Fields that can be customized')
    preview_image = models.ImageField(upload_to='template_components/', blank=True)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.component_type})"

class Template(models.Model):
    """
    Main template model for the editor
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(TemplateCategory, on_delete=models.CASCADE, related_name='templates')
    tags = models.ManyToManyField(TemplateTag, blank=True, related_name='templates')
    
    # Template Content
    html_content = models.TextField(help_text='Main HTML content')
    css_content = models.TextField(blank=True, help_text='Custom CSS styles')
    js_content = models.TextField(blank=True, help_text='Custom JavaScript')
    
    # Music and Media
    music_url = models.URLField(blank=True, help_text='Background music URL')
    music_file = models.FileField(upload_to='template_music/', blank=True, help_text='Background music file')
    
    # Design Elements
    layout = models.ForeignKey(TemplateLayout, on_delete=models.SET_NULL, null=True, blank=True)
    style = models.ForeignKey(TemplateStyle, on_delete=models.SET_NULL, null=True, blank=True)
    color_palette = models.ForeignKey(ColorPalette, on_delete=models.SET_NULL, null=True, blank=True)
    font_family = models.ForeignKey(FontFamily, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Template Properties
    is_responsive = models.BooleanField(default=True)
    is_print_ready = models.BooleanField(default=False)
    is_interactive = models.BooleanField(default=False)
    has_animations = models.BooleanField(default=False)
    
    # AI Generation
    is_ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True, help_text='AI prompt used to generate this template')
    ai_model_used = models.CharField(max_length=100, blank=True)
    
    # Media
    preview_image = models.ImageField(upload_to='template_previews/', blank=True)
    thumbnail_image = models.ImageField(upload_to='template_thumbnails/', blank=True)
    demo_url = models.URLField(blank=True, help_text='Live demo URL')
    
    # Pricing and Access
    is_free = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Status and Visibility
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    
    # Statistics
    view_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    usage_count = models.IntegerField(default=0)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    
    # Timestamps
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_templates', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_published', 'is_active']),
            models.Index(fields=['category', 'is_published']),
            models.Index(fields=['created_at']),
            models.Index(fields=['view_count']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f'/template-editor/template/{self.slug}/'
    
    def get_edit_url(self):
        return f'/admin-panel/templates/editor/{self.id}/'

class TemplateVersion(models.Model):
    """
    Version history for templates
    """
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=20)
    html_content = models.TextField()
    css_content = models.TextField(blank=True)
    js_content = models.TextField(blank=True)
    changelog = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_editor_versions')
    created_at = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['template', 'version_number']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.template.name} v{self.version_number}"

class TemplateCustomization(models.Model):
    """
    User customizations of templates
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='customizations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_customizations')
    name = models.CharField(max_length=200)
    customized_fields = models.JSONField(default=dict, help_text='User customized field values')
    generated_html = models.TextField(blank=True, help_text='Generated HTML with customizations')
    generated_css = models.TextField(blank=True, help_text='Generated CSS with customizations')
    preview_image = models.ImageField(upload_to='customization_previews/', blank=True)
    is_saved = models.BooleanField(default=False)
    is_shared = models.BooleanField(default=False)
    share_token = models.CharField(max_length=100, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} by {self.user.username}"

class AIPromptTemplate(models.Model):
    """
    AI prompt templates for generating content
    """
    PROMPT_TYPES = [
        ('template_generation', 'Template Generation'),
        ('content_suggestion', 'Content Suggestion'),
        ('design_improvement', 'Design Improvement'),
        ('color_scheme', 'Color Scheme'),
        ('layout_optimization', 'Layout Optimization'),
        ('text_enhancement', 'Text Enhancement'),
        ('html_generation', 'HTML Generation'),
        ('css_generation', 'CSS Generation'),
        ('js_generation', 'JavaScript Generation'),
    ]
    
    name = models.CharField(max_length=100)
    prompt_type = models.CharField(max_length=30, choices=PROMPT_TYPES)
    prompt_text = models.TextField(default='', help_text="Use {variables} for dynamic content")
    variables = models.JSONField(default=list, help_text="List of variable names")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_prompt_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.prompt_type})"
    
    class Meta:
        verbose_name = "AI Prompt Template"
        verbose_name_plural = "AI Prompt Templates"
        ordering = ['prompt_type', 'name']

class EditorTool(models.Model):
    """
    Tools available in the template editor
    """
    TOOL_TYPES = [
        ('text', 'Text Editor'),
        ('image', 'Image Editor'),
        ('color', 'Color Picker'),
        ('font', 'Font Selector'),
        ('layout', 'Layout Tool'),
        ('component', 'Component Library'),
        ('animation', 'Animation Tool'),
        ('responsive', 'Responsive Design'),
        ('code', 'Code Editor'),
        ('ai', 'AI Assistant'),
        ('preview', 'Preview Tool'),
        ('export', 'Export Tool'),
    ]
    
    name = models.CharField(max_length=100)
    tool_type = models.CharField(max_length=20, choices=TOOL_TYPES)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-tool')
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    configuration = models.JSONField(default=dict, help_text='Tool configuration options')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.tool_type})"

class DatabaseConnection(models.Model):
    """
    Database connections for dynamic content
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    connection_type = models.CharField(max_length=50, choices=[
        ('mysql', 'MySQL'),
        ('postgresql', 'PostgreSQL'),
        ('sqlite', 'SQLite'),
        ('mongodb', 'MongoDB'),
        ('api', 'REST API'),
        ('json', 'JSON File'),
        ('csv', 'CSV File'),
    ])
    connection_string = models.TextField(help_text='Database connection string or API endpoint')
    credentials = models.JSONField(default=dict, help_text='Connection credentials (encrypted)')
    is_active = models.BooleanField(default=True)
    test_query = models.TextField(blank=True, help_text='Query to test connection')
    last_tested = models.DateTimeField(null=True, blank=True)
    is_connected = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.connection_type})"

class TemplateDataBinding(models.Model):
    """
    Data bindings for templates to connect with databases
    """
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='data_bindings')
    database_connection = models.ForeignKey(DatabaseConnection, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=100, help_text='Template field name')
    data_source = models.CharField(max_length=200, help_text='Database table/collection or API endpoint')
    data_field = models.CharField(max_length=100, help_text='Database field or JSON key')
    data_query = models.TextField(blank=True, help_text='Custom query or filter')
    data_transform = models.TextField(blank=True, help_text='JavaScript function to transform data')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['template', 'field_name']
    
    def __str__(self):
        return f"{self.template.name} - {self.field_name}"

class TemplateExport(models.Model):
    """
    Template export history and files
    """
    EXPORT_FORMATS = [
        ('html', 'HTML'),
        ('pdf', 'PDF'),
        ('png', 'PNG Image'),
        ('jpg', 'JPG Image'),
        ('zip', 'ZIP Package'),
        ('json', 'JSON Data'),
    ]
    
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='exports')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_exports')
    export_format = models.CharField(max_length=20, choices=EXPORT_FORMATS)
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    download_count = models.IntegerField(default=0)
    is_public = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.template.name} - {self.export_format}"

# Models untuk sistem undangan
class InvitationTemplate(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(TemplateCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Template HTML lengkap (HTML + CSS + JavaScript dalam satu file)
    html_content = models.TextField(help_text="Complete HTML template with embedded CSS and JavaScript")
    
    # Media
    preview_image = models.ImageField(upload_to='template_previews/', blank=True)
    music_url = models.URLField(blank=True, help_text="URL to background music")
    music_file = models.FileField(upload_to='template_music/', blank=True)
    
    # Settings
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('template_editor:preview_template', kwargs={'pk': self.pk})
    
    def increment_usage(self):
        """Increment usage count when template is used"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

class Undangan(models.Model):
    # Referensi ke template yang digunakan
    template = models.ForeignKey(InvitationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Informasi Judul & URL
    judul = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    
    # Data Mempelai
    nama_panggilan_pria = models.CharField(max_length=100)
    nama_panggilan_wanita = models.CharField(max_length=100)
    nama_lengkap_pria = models.CharField(max_length=255)
    nama_lengkap_wanita = models.CharField(max_length=255)
    info_orang_tua_pria = models.CharField(max_length=255, blank=True)
    info_orang_tua_wanita = models.CharField(max_length=255, blank=True)
    foto_pria = models.ImageField(upload_to='couple_photos/', blank=True)
    foto_wanita = models.ImageField(upload_to='couple_photos/', blank=True)
    
    # Pengaturan Tampilan & Media
    foto_cover = models.ImageField(upload_to='cover_photos/', blank=True)
    file_musik = models.FileField(upload_to='wedding_music/', blank=True)
    
    # Teks & Kutipan
    kutipan_pembuka = models.TextField(blank=True)
    sumber_kutipan = models.CharField(max_length=255, blank=True)
    teks_pengantar_cerita = models.TextField(blank=True)
    teks_pengantar_acara = models.TextField(blank=True)
    teks_pengantar_galeri = models.TextField(blank=True)
    teks_pengantar_hadiah = models.TextField(blank=True)
    teks_pengantar_rsvp = models.TextField(blank=True)
    teks_penutup = models.TextField(blank=True)
    
    # Detail Acara 1 (Akad/Pemberkatan)
    judul_acara_1 = models.CharField(max_length=100, blank=True)
    tanggal_waktu_acara_1 = models.DateTimeField(null=True, blank=True)
    waktu_selesai_acara_1 = models.TimeField(null=True, blank=True)
    nama_lokasi_acara_1 = models.CharField(max_length=255, blank=True)
    alamat_lokasi_acara_1 = models.TextField(blank=True)
    link_gmaps_acara_1 = models.URLField(blank=True)
    
    # Detail Acara 2 (Resepsi)
    judul_acara_2 = models.CharField(max_length=100, blank=True)
    tanggal_waktu_acara_2 = models.DateTimeField(null=True, blank=True)
    waktu_selesai_acara_2 = models.TimeField(null=True, blank=True)
    nama_lokasi_acara_2 = models.CharField(max_length=255, blank=True)
    alamat_lokasi_acara_2 = models.TextField(blank=True)
    link_gmaps_acara_2 = models.URLField(blank=True)
    
    # HTML yang sudah dikustomisasi (hasil dari template + data)
    custom_html_content = models.TextField(blank=True, help_text="Customized HTML content based on template and user data")
    
    # Pengaturan Tambahan
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Undangan"
        verbose_name_plural = "Undangan"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.judul
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate base slug from judul, fallback to 'undangan' if empty
            base_slug = slugify(self.judul) if self.judul else 'undangan'
            
            # Ensure slug uniqueness
            slug = base_slug
            counter = 1
            while Undangan.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('undangan_detail', kwargs={'slug': self.slug})

class StoryItem(models.Model):
    undangan = models.ForeignKey(Undangan, on_delete=models.CASCADE, related_name='story_items')
    tanggal_kejadian = models.DateField()
    judul_kejadian = models.CharField(max_length=255)
    deskripsi = models.TextField(blank=True)
    kelas_ikon = models.CharField(max_length=50, blank=True, help_text="CSS class for icon (e.g., 'fa-heart')")
    
    class Meta:
        ordering = ['tanggal_kejadian']
    
    def __str__(self):
        return f"{self.undangan.judul} - {self.judul_kejadian}"

class GalleryPhoto(models.Model):
    undangan = models.ForeignKey(Undangan, on_delete=models.CASCADE, related_name='gallery_photos')
    foto = models.ImageField(upload_to='gallery_photos/')
    keterangan = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.undangan.judul} - Photo {self.id}"

class GiftAccount(models.Model):
    undangan = models.ForeignKey(Undangan, on_delete=models.CASCADE, related_name='gift_accounts')
    nama_bank = models.CharField(max_length=100)
    logo_bank = models.ImageField(upload_to='bank_logos/', blank=True)
    nomor_rekening = models.CharField(max_length=50)
    nama_pemilik = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.nama_bank} - {self.nomor_rekening}"

class GuestComment(models.Model):
    KEHADIRAN_CHOICES = [
        ('Hadir', 'Hadir'),
        ('Tidak Hadir', 'Tidak Hadir'),
        ('Belum Pasti', 'Belum Pasti'),
    ]
    
    undangan = models.ForeignKey(Undangan, on_delete=models.CASCADE, related_name='guest_comments')
    nama_tamu = models.CharField(max_length=255)
    ucapan = models.TextField()
    kehadiran = models.CharField(max_length=20, choices=KEHADIRAN_CHOICES)
    waktu_kirim = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-waktu_kirim']
    
    def __str__(self):
        return f"{self.nama_tamu} - {self.undangan.judul}"

class SocialLink(models.Model):
    PEMILIK_CHOICES = [
        ('Pria', 'Pria'),
        ('Wanita', 'Wanita'),
    ]
    
    undangan = models.ForeignKey(Undangan, on_delete=models.CASCADE, related_name='social_links')
    pemilik = models.CharField(max_length=10, choices=PEMILIK_CHOICES)
    url_profil = models.URLField()
    kelas_ikon = models.CharField(max_length=50, help_text="CSS class for social media icon (e.g., 'fab fa-instagram')")
    
    def __str__(self):
        return f"{self.undangan.judul} - {self.pemilik} - {self.kelas_ikon}"