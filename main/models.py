from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class InvitationTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    html_content = models.TextField()
    css_content = models.TextField(blank=True)
    js_content = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='templates/thumbnails/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    template = models.ForeignKey(InvitationTemplate, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

class InvitationData(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    bride_name = models.CharField(max_length=100)
    groom_name = models.CharField(max_length=100)
    wedding_date = models.DateField()
    wedding_time = models.TimeField()
    venue_name = models.CharField(max_length=200)
    venue_address = models.TextField()
    reception_date = models.DateField(blank=True, null=True)
    reception_time = models.TimeField(blank=True, null=True)
    reception_venue = models.CharField(max_length=200, blank=True)
    reception_address = models.TextField(blank=True)
    custom_message = models.TextField(blank=True)
    gallery_images = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return f"Invitation Data - {self.bride_name} & {self.groom_name}"
