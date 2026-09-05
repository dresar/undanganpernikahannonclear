from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import InvitationTemplate, Order, InvitationData
import json

def home(request):
    """Homepage dengan daftar template undangan"""
    templates = InvitationTemplate.objects.filter(is_active=True)
    return render(request, 'main/index.html', {
        'templates': templates
    })

def template_detail(request, template_id):
    """Detail template undangan"""
    template = get_object_or_404(InvitationTemplate, id=template_id, is_active=True)
    return render(request, 'main/template_detail.html', {
        'template': template
    })

def order_template(request, template_id):
    """Form pemesanan template"""
    template = get_object_or_404(InvitationTemplate, id=template_id, is_active=True)
    
    if request.method == 'POST':
        # Proses pemesanan
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        customer_phone = request.POST.get('customer_phone')
        
        # Data undangan
        bride_name = request.POST.get('bride_name')
        groom_name = request.POST.get('groom_name')
        wedding_date = request.POST.get('wedding_date')
        wedding_time = request.POST.get('wedding_time')
        venue_name = request.POST.get('venue_name')
        venue_address = request.POST.get('venue_address')
        
        # Buat order
        order = Order.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            template=template,
            total_price=100000,  # Harga default
            status='pending'
        )
        
        # Buat data undangan
        InvitationData.objects.create(
            order=order,
            bride_name=bride_name,
            groom_name=groom_name,
            wedding_date=wedding_date,
            wedding_time=wedding_time,
            venue_name=venue_name,
            venue_address=venue_address
        )
        
        messages.success(request, 'Pesanan berhasil dibuat! Kami akan menghubungi Anda segera.')
        return redirect('main:order_success', order_id=order.id)
    
    return render(request, 'main/order_form.html', {
        'template': template
    })

def order_success(request, order_id):
    """Halaman sukses pemesanan"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'main/order_success.html', {
        'order': order
    })

def preview_invitation(request, order_id):
    """Preview undangan yang sudah dibuat"""
    order = get_object_or_404(Order, id=order_id)
    invitation_data = get_object_or_404(InvitationData, order=order)
    
    return render(request, 'main/invitation_preview.html', {
        'order': order,
        'invitation_data': invitation_data,
        'template': order.template
    })
