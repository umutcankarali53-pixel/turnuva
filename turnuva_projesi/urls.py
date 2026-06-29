"""
URL configuration for turnuva_projesi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include

handler404 = 'turnuva.views.public.handler404'
handler500 = 'turnuva.views.public.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('turnuva.urls')),
    path('accounts/', include('allauth.urls')),
]

# Şifre sıfırlama URL'leri
from django.contrib.auth import views as auth_views

urlpatterns += [
    path('sifre-sifirla/', auth_views.PasswordResetView.as_view(
        template_name='turnuva/sifre_sifirla.html',
        email_template_name='turnuva/sifre_sifirla_email.html',
        subject_template_name='turnuva/sifre_sifirla_konu.txt',
        success_url='/sifre-sifirla/basari/'
    ), name='sifre_sifirla'),
    path('sifre-sifirla/basari/', auth_views.PasswordResetDoneView.as_view(
        template_name='turnuva/sifre_sifirla_basari.html'
    ), name='sifre_sifirla_basari'),
    path('sifre-sifirla/onay/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='turnuva/sifre_sifirla_onay.html',
        success_url='/sifre-sifirla/tamam/'
    ), name='sifre_sifirla_onay'),
    path('sifre-sifirla/tamam/', auth_views.PasswordResetCompleteView.as_view(
        template_name='turnuva/sifre_sifirla_tamam.html'
    ), name='sifre_sifirla_tamam'),
]
