# turnuva/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Duyuru
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pandas as pd
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from .forms import BasketbolTakimiForm, BasketbolOyuncuFormSet, FutbolTakimiForm, FutbolOyuncuFormSet, DuyuruForm
from .models import Duyuru, BasketbolTakimi, FutbolTakimi

# --- MEVCUT FONKSİYONLAR ---
def ana_sayfa(request):
    son_duyuru = Duyuru.objects.filter(aktif=True).first()
    context = {'son_duyuru': son_duyuru}
    return render(request, 'turnuva/ana_sayfa.html', context)

def duyurular_sayfasi(request):
    tum_duyurular = Duyuru.objects.filter(aktif=True).order_by('-yayinlanma_tarihi')
    context = {'duyurular': tum_duyurular}
    return render(request, 'turnuva/duyurular.html', context)

# --- YENİ EKLENEN KİMLİK DOĞRULAMA (AUTH) FONKSİYONLARI ---
def kayit_ol(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Kayıt olduktan sonra otomatik giriş yap
            return redirect('ana_sayfa')
    else:
        form = UserCreationForm()
    return render(request, 'turnuva/kayit.html', {'form': form})

def giris_yap(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('ana_sayfa')
    else:
        form = AuthenticationForm()
    return render(request, 'turnuva/giris.html', {'form': form})

def cikis_yap(request):
    logout(request)
    return redirect('ana_sayfa')

@login_required(login_url='giris_yap')
def profil(request):
    # Kullanıcının önceden oluşturduğu bir takımı var mı kontrol ediyoruz
    basketbol_takimi = getattr(request.user, 'basketbol_takimi', None)
    futbol_takimi = getattr(request.user, 'futbol_takimi', None)
    
    context = {
        'basketbol_takimi': basketbol_takimi,
        'futbol_takimi': futbol_takimi
    }
    return render(request, 'turnuva/profil.html', context)

@login_required(login_url='giris_yap')
def basketbol_takim_yonetimi(request):
    # Kullanıcının daha önceden takımı varsa onu getir, yoksa boş (None) kabul et
    takim = getattr(request.user, 'basketbol_takimi', None)
    
    if request.method == 'POST':
        # Formları kullanıcının gönderdiği (POST) verilerle doldur
        form = BasketbolTakimiForm(request.POST, instance=takim)
        formset = BasketbolOyuncuFormSet(request.POST, instance=takim)
        
        if form.is_valid() and formset.is_valid():
            # Önce takımı kaydet (ama veritabanına tam yazmadan önce kaptanı ekle)
            kaydedilen_takim = form.save(commit=False)
            kaydedilen_takim.kaptan = request.user
            kaydedilen_takim.save()
            
            # Şimdi oyuncuları bu takıma bağlayarak kaydet
            formset.instance = kaydedilen_takim
            formset.save()
            
            messages.success(request, "Basketbol takımınız başarıyla kaydedildi!")
            return redirect('profil')
        else:
            messages.error(request, "Lütfen formdaki hataları kontrol edin. (Bir TC numarası daha önce kullanılmış olabilir!)")
    else:
        # Sayfa ilk kez açılıyorsa boş (veya mevcut) formları göster
        form = BasketbolTakimiForm(instance=takim)
        formset = BasketbolOyuncuFormSet(instance=takim)
        
    return render(request, 'turnuva/takim_form.html', {
        'form': form, 
        'formset': formset, 
        'brans': 'Basketbol Takımı'
    })


@login_required(login_url='giris_yap')
def futbol_takim_yonetimi(request):
    takim = getattr(request.user, 'futbol_takimi', None)
    
    if request.method == 'POST':
        form = FutbolTakimiForm(request.POST, instance=takim)
        formset = FutbolOyuncuFormSet(request.POST, instance=takim)
        
        if form.is_valid() and formset.is_valid():
            kaydedilen_takim = form.save(commit=False)
            kaydedilen_takim.kaptan = request.user
            kaydedilen_takim.save()
            
            formset.instance = kaydedilen_takim
            formset.save()
            
            messages.success(request, "Futbol takımınız başarıyla kaydedildi!")
            return redirect('profil')
        else:
            messages.error(request, "Lütfen formdaki hataları kontrol edin.")
    else:
        form = FutbolTakimiForm(instance=takim)
        formset = FutbolOyuncuFormSet(instance=takim)
        
    return render(request, 'turnuva/takim_form.html', {
        'form': form, 
        'formset': formset, 
        'brans': 'Futbol Takımı'
    })

@staff_member_required(login_url='giris_yap')
def ozel_yonetim_paneli(request):
    # Sadece admin (staff) olanlar bu sayfaya girebilir
    basketbol_sayisi = BasketbolTakimi.objects.count()
    futbol_sayisi = FutbolTakimi.objects.count()
    duyurular = Duyuru.objects.all().order_by('-yayinlanma_tarihi')

    if request.method == 'POST':
        form = DuyuruForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Yeni duyuru başarıyla yayınlandı!")
            return redirect('ozel_yonetim')
    else:
        form = DuyuruForm()

    context = {
        'basketbol_sayisi': basketbol_sayisi,
        'futbol_sayisi': futbol_sayisi,
        'duyurular': duyurular,
        'form': form
    }
    return render(request, 'turnuva/ozel_yonetim.html', context)


@staff_member_required(login_url='giris_yap')
def excel_indir_basketbol(request):
    takimlar = BasketbolTakimi.objects.all()
    veri_listesi = []
    for takim in takimlar:
        satir = {
            'Takım Adı': takim.takim_adi,
            'Kaptan': takim.kaptan.username,
            'Telefon': takim.telefon,
            'Kayıt Tarihi': takim.kayit_tarihi.strftime('%Y-%m-%d %H:%M'),
        }
        for i, oyuncu in enumerate(takim.oyuncular.all(), start=1):
            satir[f'Oyuncu {i} Ad'] = oyuncu.ad
            satir[f'Oyuncu {i} Soyad'] = oyuncu.soyad
            satir[f'Oyuncu {i} TC'] = oyuncu.tc_no
        veri_listesi.append(satir)
        
    df = pd.DataFrame(veri_listesi)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Basketbol_Tum_Kayitlar.xlsx'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Basketbol')
    return response


@staff_member_required(login_url='giris_yap')
def excel_indir_futbol(request):
    takimlar = FutbolTakimi.objects.all()
    veri_listesi = []
    for takim in takimlar:
        satir = {
            'Takım Adı': takim.takim_adi,
            'Kaptan': takim.kaptan.username,
            'Telefon': takim.telefon,
            'Kayıt Tarihi': takim.kayit_tarihi.strftime('%Y-%m-%d %H:%M'),
        }
        for i, oyuncu in enumerate(takim.oyuncular.all(), start=1):
            satir[f'Oyuncu {i} Ad'] = oyuncu.ad
            satir[f'Oyuncu {i} Soyad'] = oyuncu.soyad
            satir[f'Oyuncu {i} TC'] = oyuncu.tc_no
        veri_listesi.append(satir)
        
    df = pd.DataFrame(veri_listesi)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Futbol_Tum_Kayitlar.xlsx'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Futbol')
    return response