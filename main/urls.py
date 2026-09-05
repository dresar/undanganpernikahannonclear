from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('template/<int:template_id>/', views.template_detail, name='template_detail'),
    path('order/<int:template_id>/', views.order_template, name='order_template'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('preview/<int:order_id>/', views.preview_invitation, name='preview_invitation'),
]