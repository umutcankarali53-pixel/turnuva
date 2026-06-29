# turnuva/views/public.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
from turnuva.models import Duyuru


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


def ana_sayfa(request):
    son_duyuru = Duyuru.objects.filter(aktif=True).first()
    context = {'son_duyuru': son_duyuru}
    return render(request, 'turnuva/ana_sayfa.html', context)


def duyurular_sayfasi(request):
    tum_duyurular = Duyuru.objects.filter(aktif=True).order_by('-yayinlanma_tarihi')
    context = {'duyurular': tum_duyurular}
    return render(request, 'turnuva/duyurular.html', context)


@ratelimit(key='ip', rate='5/m', block=True)
@ratelimit(key='post:username', rate='3/m', block=True)
def kayit_ol(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Hesabınız başarıyla oluşturuldu!')
            return redirect('profil')
    else:
        form = UserCreationForm()
    return render(request, 'turnuva/kayit.html', {'form': form})


@ratelimit(key='ip', rate='5/m', block=True)
@ratelimit(key='post:username', rate='3/m', block=True)
def giris_yap(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profil')
    else:
        form = AuthenticationForm()
    return render(request, 'turnuva/giris.html', {'form': form})


def cikis_yap(request):
    logout(request)
    messages.info(request, 'Başarıyla çıkış yapıldı.')
    return redirect('ana_sayfa')