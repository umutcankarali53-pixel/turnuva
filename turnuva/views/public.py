# turnuva/views/public.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
from django.utils import timezone
from turnuva.models import Duyuru, SiteAyar
from turnuva.forms import DuyuruForm


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


def ana_sayfa(request):
    from turnuva.models import Turnuva, Mac
    
    site_ayar = SiteAyar.objects.filter(aktif=True).first()
    son_duyuru = Duyuru.objects.filter(aktif=True).first()
    
    # Aktif turnuva ve maçları bul
    turnuvalar = Turnuva.objects.filter(durum__in=['eslesme_yapildi', 'devam_ediyor']).order_by('-olusturma_tarihi')[:1]
    maclar = []
    if turnuvalar:
        maclar = turnuvalar[0].maclar.all().order_by('tur', 'mac_sirasi')[:10]
    
    context = {
        'son_duyuru': son_duyuru,
        'site_ayar': site_ayar,
        'site': site_ayar,
        'turnuvalar': turnuvalar,
        'maclar': maclar,
    }
    return render(request, 'turnuva/ana_sayfa.html', context)


def duyurular_sayfasi(request):
    tum_duyurular = Duyuru.objects.filter(aktif=True).order_by('-yayinlanma_tarihi')
    context = {'duyurular': tum_duyurular}
    return render(request, 'turnuva/duyurular.html', context)


@ratelimit(key='ip', rate='5/m', block=True)
@ratelimit(key='post:username', rate='3/m', block=True)
def kayit_ol(request):
    # Kayıt bitiş kontrolü
    site_ayar = SiteAyar.objects.filter(aktif=True).first()
    if site_ayar and site_ayar.kayit_bitis_tarihi and site_ayar.kayit_bitis_tarihi <= timezone.now():
        messages.error(request, "Kayıt süresi dolmuştur. Yeni hesap oluşturulamaz.")
        return redirect('ana_sayfa')
    
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


def fikstur_sayfasi(request):
    """Fikstür sayfası - Kullanıcılar turnuva eşleşmelerini görür"""
    from turnuva.models import Turnuva, Mac
    
    # Aktif turnuvaları getir
    turnuvalar = Turnuva.objects.filter(durum__in=['eslesme_yapildi', 'devam_ediyor']).order_by('-olusturma_tarihi')
    
    secili_turnuva = None
    maclar = []
    
    turnuva_id = request.GET.get('turnuva')
    if turnuva_id:
        secili_turnuva = Turnuva.objects.filter(pk=turnuva_id).first()
        if secili_turnuva:
            maclar = secili_turnuva.maclar.all().order_by('tur', 'mac_sirasi')
    
    context = {
        'turnuvalar': turnuvalar,
        'secili_turnuva': secili_turnuva,
        'maclar': maclar,
    }
    return render(request, 'turnuva/fikstur.html', context)