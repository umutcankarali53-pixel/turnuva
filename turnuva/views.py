# turnuva/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
import pandas as pd
from django.http import HttpResponse
from .forms import BasketbolTakimiForm, BasketbolOyuncuFormSet, FutbolTakimiForm, FutbolOyuncuFormSet, DuyuruForm
from .models import Duyuru, BasketbolTakimi, BasketbolOyuncu, FutbolTakimi, FutbolOyuncu


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

# --- YENİ EKLENEN KİMLİK DOĞRULAMA (AUTH) FONKSİYONLARI ---
def kayit_ol(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profil')
    else:
        form = UserCreationForm()
    return render(request, 'turnuva/kayit.html', {'form': form})

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
    return redirect('admin_dashboard')


def _admin_ctx(page, **extra):
    data = {'active_page': page}
    data.update(extra)
    return data


def _dashboard_stats():
    now = timezone.now()
    s7, s30 = now - timedelta(days=7), now - timedelta(days=30)
    bb = BasketbolTakimi.objects.count()
    fb = FutbolTakimi.objects.count()
    return {
        'toplam_kullanici': User.objects.count(), 'basketbol_sayisi': bb, 'futbol_sayisi': fb,
        'toplam_takim': bb + fb, 'basketbol_oyuncu': BasketbolOyuncu.objects.count(),
        'futbol_oyuncu': FutbolOyuncu.objects.count(),
        'toplam_oyuncu': BasketbolOyuncu.objects.count() + FutbolOyuncu.objects.count(),
        'aktif_duyuru': Duyuru.objects.filter(aktif=True).count(), 'toplam_duyuru': Duyuru.objects.count(),
        'son_7_gun_basketbol': BasketbolTakimi.objects.filter(kayit_tarihi__gte=s7).count(),
        'son_7_gun_futbol': FutbolTakimi.objects.filter(kayit_tarihi__gte=s7).count(),
        'son_30_gun_basketbol': BasketbolTakimi.objects.filter(kayit_tarihi__gte=s30).count(),
        'son_30_gun_futbol': FutbolTakimi.objects.filter(kayit_tarihi__gte=s30).count(),
        'takimsiz_kullanici': User.objects.filter(basketbol_takimi__isnull=True, futbol_takimi__isnull=True).count(),
        'her_iki_takim': User.objects.filter(basketbol_takimi__isnull=False, futbol_takimi__isnull=False).count(),
    }


@staff_member_required(login_url='giris_yap')
def admin_dashboard(request):
    stats = _dashboard_stats()
    today = timezone.localdate()
    cubuklar = []
    mx = 1
    raw = []
    for i in range(6, -1, -1):
        tarih = today - timedelta(days=i)
        bb = BasketbolTakimi.objects.filter(kayit_tarihi__date=tarih).count()
        fb = FutbolTakimi.objects.filter(kayit_tarihi__date=tarih).count()
        raw.append((tarih.strftime('%d.%m'), bb, fb))
        mx = max(mx, bb, fb)
    for label, bb, fb in raw:
        cubuklar.append({'label': label, 'bb_yukseklik': round(bb / mx * 100), 'fb_yukseklik': round(fb / mx * 100)})
    bb_list = [{'brans': 'Basketbol', 'takim': t.takim_adi, 'kaptan': t.kaptan.username, 'tarih': t.kayit_tarihi, 'pk': t.pk, 'tip': 'basketbol'} for t in BasketbolTakimi.objects.select_related('kaptan').order_by('-kayit_tarihi')[:8]]
    fb_list = [{'brans': 'Futbol', 'takim': t.takim_adi, 'kaptan': t.kaptan.username, 'tarih': t.kayit_tarihi, 'pk': t.pk, 'tip': 'futbol'} for t in FutbolTakimi.objects.select_related('kaptan').order_by('-kayit_tarihi')[:8]]
    son = sorted(bb_list + fb_list, key=lambda x: x['tarih'], reverse=True)[:8]
    return render(request, 'admin/dashboard.html', _admin_ctx('dashboard', grafik_cubuklar=cubuklar, son_kayitlar=son, son_duyurular=Duyuru.objects.order_by('-yayinlanma_tarihi')[:5], **stats))


@staff_member_required(login_url='giris_yap')
def admin_basketbol_listesi(request):
    q = request.GET.get('q', '').strip()
    qs = BasketbolTakimi.objects.select_related('kaptan').prefetch_related('oyuncular')
    if q:
        qs = qs.filter(Q(takim_adi__icontains=q) | Q(telefon__icontains=q) | Q(kaptan__username__icontains=q))
    page = Paginator(qs.order_by('-kayit_tarihi'), 15).get_page(request.GET.get('sayfa'))
    return render(request, 'admin/takim_listesi.html', _admin_ctx('basketbol', brans='Basketbol', brans_slug='basketbol', takimlar=page, q=q, toplam=page.paginator.count))


@staff_member_required(login_url='giris_yap')
def admin_futbol_listesi(request):
    q = request.GET.get('q', '').strip()
    qs = FutbolTakimi.objects.select_related('kaptan').prefetch_related('oyuncular')
    if q:
        qs = qs.filter(Q(takim_adi__icontains=q) | Q(telefon__icontains=q) | Q(kaptan__username__icontains=q))
    page = Paginator(qs.order_by('-kayit_tarihi'), 15).get_page(request.GET.get('sayfa'))
    return render(request, 'admin/takim_listesi.html', _admin_ctx('futbol', brans='Futbol', brans_slug='futbol', takimlar=page, q=q, toplam=page.paginator.count))


@staff_member_required(login_url='giris_yap')
def admin_basketbol_detay(request, pk):
    takim = get_object_or_404(BasketbolTakimi.objects.select_related('kaptan').prefetch_related('oyuncular'), pk=pk)
    return render(request, 'admin/takim_detay.html', _admin_ctx('basketbol', brans='Basketbol', brans_slug='basketbol', takim=takim, oyuncular=takim.oyuncular.all()))


@staff_member_required(login_url='giris_yap')
def admin_futbol_detay(request, pk):
    takim = get_object_or_404(FutbolTakimi.objects.select_related('kaptan').prefetch_related('oyuncular'), pk=pk)
    return render(request, 'admin/takim_detay.html', _admin_ctx('futbol', brans='Futbol', brans_slug='futbol', takim=takim, oyuncular=takim.oyuncular.all()))


@staff_member_required(login_url='giris_yap')
@require_POST
def admin_basketbol_sil(request, pk):
    takim = get_object_or_404(BasketbolTakimi, pk=pk)
    ad = takim.takim_adi
    takim.delete()
    messages.success(request, f'"{ad}" silindi.')
    return redirect('admin_basketbol_listesi')


@staff_member_required(login_url='giris_yap')
@require_POST
def admin_futbol_sil(request, pk):
    takim = get_object_or_404(FutbolTakimi, pk=pk)
    ad = takim.takim_adi
    takim.delete()
    messages.success(request, f'"{ad}" silindi.')
    return redirect('admin_futbol_listesi')


@staff_member_required(login_url='giris_yap')
def admin_duyurular(request):
    if request.method == 'POST':
        form = DuyuruForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Duyuru yayinlandi.')
            return redirect('admin_duyurular')
    else:
        form = DuyuruForm()
    return render(request, 'admin/duyurular.html', _admin_ctx('duyurular', form=form, duyurular=Duyuru.objects.order_by('-yayinlanma_tarihi')))


@staff_member_required(login_url='giris_yap')
def admin_duyuru_duzenle(request, pk):
    duyuru = get_object_or_404(Duyuru, pk=pk)
    if request.method == 'POST':
        form = DuyuruForm(request.POST, instance=duyuru)
        if form.is_valid():
            form.save()
            messages.success(request, 'Duyuru guncellendi.')
            return redirect('admin_duyurular')
    else:
        form = DuyuruForm(instance=duyuru)
    return render(request, 'admin/duyuru_duzenle.html', _admin_ctx('duyurular', form=form, duyuru=duyuru))


@staff_member_required(login_url='giris_yap')
@require_POST
def admin_duyuru_sil(request, pk):
    duyuru = get_object_or_404(Duyuru, pk=pk)
    baslik = duyuru.baslik
    duyuru.delete()
    messages.success(request, f'"{baslik}" silindi.')
    return redirect('admin_duyurular')


@staff_member_required(login_url='giris_yap')
@require_POST
def admin_duyuru_toggle(request, pk):
    duyuru = get_object_or_404(Duyuru, pk=pk)
    duyuru.aktif = not duyuru.aktif
    duyuru.save()
    messages.success(request, 'Duyuru durumu guncellendi.')
    return redirect('admin_duyurular')


@staff_member_required(login_url='giris_yap')
def admin_kullanicilar(request):
    q = request.GET.get('q', '').strip()
    filtre = request.GET.get('filtre', '')
    qs = User.objects.select_related('basketbol_takimi', 'futbol_takimi').order_by('-date_joined')
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q))
    if filtre == 'takimsiz':
        qs = qs.filter(basketbol_takimi__isnull=True, futbol_takimi__isnull=True)
    elif filtre == 'basketbol':
        qs = qs.filter(basketbol_takimi__isnull=False)
    elif filtre == 'futbol':
        qs = qs.filter(futbol_takimi__isnull=False)
    page = Paginator(qs, 20).get_page(request.GET.get('sayfa'))
    return render(request, 'admin/kullanicilar.html', _admin_ctx('kullanicilar', kullanicilar=page, q=q, filtre=filtre, toplam=page.paginator.count))


def _excel_yanit(df, dosya, sayfa='Veri'):
    resp = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = f'attachment; filename={dosya}'
    with pd.ExcelWriter(resp, engine='openpyxl') as w:
        df.to_excel(w, index=False, sheet_name=sayfa)
    return resp


@staff_member_required(login_url='giris_yap')
def admin_export_basketbol(request):
    return excel_indir_basketbol(request)


@staff_member_required(login_url='giris_yap')
def admin_export_futbol(request):
    return excel_indir_futbol(request)


@staff_member_required(login_url='giris_yap')
def admin_export_tum(request):
    bb, fb = [], []
    for t in BasketbolTakimi.objects.select_related('kaptan').prefetch_related('oyuncular'):
        s = {'Takim': t.takim_adi, 'Kaptan': t.kaptan.username, 'Tel': t.telefon}
        for i, o in enumerate(t.oyuncular.all(), 1):
            s[f'O{i}'] = f'{o.ad} {o.soyad}'
        bb.append(s)
    for t in FutbolTakimi.objects.select_related('kaptan').prefetch_related('oyuncular'):
        s = {'Takim': t.takim_adi, 'Kaptan': t.kaptan.username, 'Tel': t.telefon}
        for i, o in enumerate(t.oyuncular.all(), 1):
            s[f'O{i}'] = f'{o.ad} {o.soyad}'
        fb.append(s)
    resp = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = 'attachment; filename=Turnuva_Tum_Veriler.xlsx'
    with pd.ExcelWriter(resp, engine='openpyxl') as w:
        pd.DataFrame(bb).to_excel(w, index=False, sheet_name='Basketbol')
        pd.DataFrame(fb).to_excel(w, index=False, sheet_name='Futbol')
    return resp


@staff_member_required(login_url='giris_yap')
def admin_export_kullanicilar(request):
    veri = [{'Kullanici': u.username, 'E-posta': u.email,
             'BB': 'Evet' if BasketbolTakimi.objects.filter(kaptan=u).exists() else 'Hayir',
             'FB': 'Evet' if FutbolTakimi.objects.filter(kaptan=u).exists() else 'Hayir'} for u in User.objects.order_by('-date_joined')]
    return _excel_yanit(pd.DataFrame(veri), 'Kullanicilar.xlsx', 'Kullanicilar')


@staff_member_required(login_url='giris_yap')
def excel_indir_basketbol(request):
    veri = []
    for t in BasketbolTakimi.objects.select_related('kaptan').prefetch_related('oyuncular'):
        s = {'Takim Adi': t.takim_adi, 'Kaptan': t.kaptan.username, 'Telefon': t.telefon}
        for i, o in enumerate(t.oyuncular.all(), 1):
            s[f'Oyuncu{i}'] = f'{o.ad} {o.soyad} ({o.tc_no})'
        veri.append(s)
    return _excel_yanit(pd.DataFrame(veri), 'Basketbol_Tum_Kayitlar.xlsx', 'Basketbol')


@staff_member_required(login_url='giris_yap')
def excel_indir_futbol(request):
    veri = []
    for t in FutbolTakimi.objects.select_related('kaptan').prefetch_related('oyuncular'):
        s = {'Takim Adi': t.takim_adi, 'Kaptan': t.kaptan.username, 'Telefon': t.telefon}
        for i, o in enumerate(t.oyuncular.all(), 1):
            s[f'Oyuncu{i}'] = f'{o.ad} {o.soyad} ({o.tc_no})'
        veri.append(s)
    return _excel_yanit(pd.DataFrame(veri), 'Futbol_Tum_Kayitlar.xlsx', 'Futbol')