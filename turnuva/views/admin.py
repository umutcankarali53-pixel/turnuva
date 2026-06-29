# turnuva/views/admin.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, F, Case, When, IntegerField
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import HttpResponse, JsonResponse
from django.db.models.functions import TruncDate
from turnuva.forms import DuyuruForm
from turnuva.models import Duyuru, BasketbolTakimi, BasketbolOyuncu, FutbolTakimi, FutbolOyuncu, SiteAyar, SayfaGoruntuleme, Turnuva, Mac
from django.contrib.auth.models import User
from turnuva.utils.excel import export_basketbol_excel, export_futbol_excel, export_tum_excel, export_kullanicilar_excel
import pandas as pd


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
    
    # Sayfa görüntüleme istatistikleri
    sayfa_istatistikleri = _sayfa_goruntuleme_istatistikleri()
    
    return render(request, 'admin/dashboard.html', _admin_ctx('dashboard', 
        grafik_cubuklar=cubuklar, 
        son_kayitlar=son, 
        son_duyurular=Duyuru.objects.order_by('-yayinlanma_tarihi')[:5], 
        sayfa_istatistikleri=sayfa_istatistikleri,
        **stats))


def _sayfa_goruntuleme_istatistikleri():
    """Sayfa görüntüleme istatistiklerini hesapla"""
    today = timezone.localdate()
    son_7_gun = today - timedelta(days=7)
    son_30_gun = today - timedelta(days=30)
    
    # Günlük görüntülemeler (son 7 gün)
    gunluk_veri = []
    for i in range(6, -1, -1):
        tarih = today - timedelta(days=i)
        sayi = SayfaGoruntuleme.objects.filter(goruntuleme_tarihi=tarih).count()
        gunluk_veri.append({
            'tarih': tarih.strftime('%d.%m'),
            'sayi': sayi
        })
    
    # Aylık görüntülemeler (son 6 ay)
    aylik_veri = []
    for i in range(5, -1, -1):
        ay_baslangic = today.replace(day=1) - timedelta(days=i*30)
        ay_baslangic = ay_baslangic.replace(day=1)
        if i == 0:
            ay_bitis = today
        else:
            next_month = ay_baslangic.replace(day=28) + timedelta(days=4)
            ay_bitis = next_month - timedelta(days=next_month.day)
        
        sayi = SayfaGoruntuleme.objects.filter(
            goruntuleme_tarihi__gte=ay_baslangic,
            goruntuleme_tarihi__lte=ay_bitis
        ).count()
        aylik_veri.append({
            'ay': ay_baslangic.strftime('%m.%Y'),
            'sayi': sayi
        })
    
    # En çok görüntülenen sayfalar
    en_cok_goruntulenen = SayfaGoruntuleme.objects.values('sayfa_adi').annotate(
        sayi=Count('id')
    ).order_by('-sayi')[:5]
    
    # Toplam sayılar
    toplam_goruntuleme = SayfaGoruntuleme.objects.count()
    son_7_gun_goruntuleme = SayfaGoruntuleme.objects.filter(goruntuleme_tarihi__gte=son_7_gun).count()
    son_30_gun_goruntuleme = SayfaGoruntuleme.objects.filter(goruntuleme_tarihi__gte=son_30_gun).count()
    
    return {
        'gunluk_veri': gunluk_veri,
        'aylik_veri': aylik_veri,
        'en_cok_goruntulenen': en_cok_goruntulenen,
        'toplam_goruntuleme': toplam_goruntuleme,
        'son_7_gun_goruntuleme': son_7_gun_goruntuleme,
        'son_30_gun_goruntuleme': son_30_gun_goruntuleme,
    }


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


@staff_member_required(login_url='giris_yap')
def admin_site_ayarlari(request):
    """Site ayarlarını düzenleme sayfası"""
    site_ayar = SiteAyar.objects.filter(aktif=True).first()
    
    if request.method == 'POST':
        if site_ayar:
            # Mevcut kaydı güncelle
            site_ayar.kvkk_text = request.POST.get('kvkk_text', site_ayar.kvkk_text)
            site_ayar.kayit_bitis_tarihi = request.POST.get('kayit_bitis_tarihi') or None
            site_ayar.whatsapp_api_token = request.POST.get('whatsapp_api_token', '')
            site_ayar.whatsapp_phone_number_id = request.POST.get('whatsapp_phone_number_id', '')
            site_ayar.whatsapp_recipient_number = request.POST.get('whatsapp_recipient_number', '')
            
            # Countdown ayarları
            site_ayar.countdown_baslik = request.POST.get('countdown_baslik', '')
            site_ayar.countdown_alt_baslik = request.POST.get('countdown_alt_baslik', '')
            site_ayar.countdown_ust_baslik = request.POST.get('countdown_ust_baslik', '')
            
            site_ayar.save()
            messages.success(request, 'Site ayarları güncellendi.')
        else:
            # Yeni kayıt oluştur
            site_ayar = SiteAyar(
                kvkk_text=request.POST.get('kvkk_text', ''),
                kayit_bitis_tarihi=request.POST.get('kayit_bitis_tarihi') or None,
                whatsapp_api_token=request.POST.get('whatsapp_api_token', ''),
                whatsapp_phone_number_id=request.POST.get('whatsapp_phone_number_id', ''),
                whatsapp_recipient_number=request.POST.get('whatsapp_recipient_number', ''),
                countdown_baslik=request.POST.get('countdown_baslik', ''),
                countdown_alt_baslik=request.POST.get('countdown_alt_baslik', ''),
                countdown_ust_baslik=request.POST.get('countdown_ust_baslik', ''),
            )
            site_ayar.save()
            messages.success(request, 'Site ayarları oluşturuldu.')
        return redirect('admin_site_ayarlari')
    
    return render(request, 'admin/site_ayarlari.html', _admin_ctx('ayarlar', site_ayar=site_ayar))


@staff_member_required(login_url='giris_yap')
def admin_fikstur(request):
    """Fikstür yönetimi sayfası"""
    turnuvalar = Turnuva.objects.all().order_by('-olusturma_tarihi')
    secili_turnuva = None
    maclar = []
    
    turnuva_id = request.GET.get('turnuva')
    if turnuva_id:
        secili_turnuva = get_object_or_404(Turnuva, pk=turnuva_id)
        maclar = secili_turnuva.maclar.all().order_by('tur', 'mac_sirasi')
    
    context = {
        'turnuvalar': turnuvalar,
        'secili_turnuva': secili_turnuva,
        'maclar': maclar,
    }
    return render(request, 'admin/fikstur.html', _admin_ctx('fikstur', **context))


@staff_member_required(login_url='giris_yap')
@require_POST
def admin_mac_duzenle(request, pk):
    """Maç bilgilerini düzenle"""
    mac = get_object_or_404(Mac, pk=pk)
    
    mac.takim1_skor = request.POST.get('takim1_skor') or None
    mac.takim2_skor = request.POST.get('takim2_skor') or None
    mac.durum = request.POST.get('durum', mac.durum)
    mac.tarih = request.POST.get('tarih') or None
    mac.yer = request.POST.get('yer', mac.yer)
    
    mac.save()
    messages.success(request, f'{mac.takim1_adi} vs {mac.takim2_adi} maçı güncellendi.')
    return redirect(f'admin_fikstur?turnuva={mac.turnuva.pk}')


@staff_member_required(login_url='giris_yap')
@require_POST
def admin_mac_sil(request, pk):
    """Maç sil"""
    mac = get_object_or_404(Mac, pk=pk)
    turnuva_id = mac.turnuva.pk
    mac.delete()
    messages.success(request, 'Maç silindi.')
    return redirect(f'admin_fikstur?turnuva={turnuva_id}')


@staff_member_required(login_url='giris_yap')
@require_POST
def admin_eslesme_olustur(request):
    """Turnuva için maç eşleşmelerini otomatik oluştur"""
    turnuva_id = request.POST.get('turnuva_id')
    brans = request.POST.get('brans')
    
    if not turnuva_id or not brans:
        messages.error(request, 'Turnuva ve branş seçimi gereklidir.')
        return redirect('admin_fikstur')
    
    turnuva = get_object_or_404(Turnuva, pk=turnuva_id)
    
    if brans == 'basketbol':
        takimlar = list(BasketbolTakimi.objects.all().order_by('kayit_tarihi'))
    else:
        takimlar = list(FutbolTakimi.objects.all().order_by('kayit_tarihi'))
    
    if len(takimlar) < 2:
        messages.error(request, 'En az 2 takım olmalıdır.')
        return redirect('admin_fikstur')
    
    # Eski maçları temizle
    Mac.objects.filter(turnuva=turnuva).delete()
    
    # Tek eleme usulü maç eşleştirmeleri
    from itertools import combinations
    mac_sayaci = 0
    tur = 1
    
    # Basit round-robin turnuva sistemi
    takim_sayisi = len(takimlar)
    for i in range(takim_sayisi - 1):
        for j in range(i + 1, takim_sayisi):
            takim1 = takimlar[i]
            takim2 = takimlar[j]
            
            Mac.objects.create(
                turnuva=turnuva,
                tur=tur,
                mac_sirasi=mac_sayaci + 1,
                takim1_tip=brans,
                takim1_id=takim1.pk,
                takim1_adi=takim1.takim_adi,
                takim2_tip=brans,
                takim2_id=takim2.pk,
                takim2_adi=takim2.takim_adi,
            )
            mac_sayaci += 1
        tur += 1
    
    turnuva.durum = 'eslesme_yapildi'
    turnuva.save()
    
    messages.success(request, f'{mac_sayaci} maç eşleşmesi başarıyla oluşturuldu.')
    return redirect(f'admin_fikstur?turnuva={turnuva_id}')


@staff_member_required(login_url='giris_yap')
@require_POST
def admin_turnuva_ekle(request):
    """Yeni turnuva oluştur"""
    ad = request.POST.get('turnuva_ad')
    brans = request.POST.get('turnuva_brans')
    kayit_bitis = request.POST.get('turnuva_bitis')
    
    if not all([ad, brans, kayit_bitis]):
        messages.error(request, 'Tüm alanları doldurunuz.')
        return redirect('admin_fikstur')
    
    try:
        kayit_bitis_tarihi = datetime.strptime(kayit_bitis, '%Y-%m-%dT%H:%M')
        turnuva = Turnuva.objects.create(
            ad=ad,
            brans=brans,
            kayit_bitis_tarihi=kayit_bitis_tarihi,
            durum='kayit_acik'
        )
        messages.success(request, f'"{ad}" turnuvası başarıyla oluşturuldu.')
    except Exception as e:
        messages.error(request, f'Hata: {str(e)}')
    
    return redirect('admin_fikstur')


@staff_member_required(login_url='giris_yap')
@require_POST
def admin_turnuva_sil(request, pk):
    """Turnuva sil"""
    turnuva = get_object_or_404(Turnuva, pk=pk)
    ad = turnuva.ad
    turnuva.delete()
    messages.success(request, f'"{ad}" turnuvası silindi.')
    return redirect('admin_fikstur')


@staff_member_required(login_url='giris_yap')
def admin_export_basketbol(request):
    return export_basketbol_excel()


@staff_member_required(login_url='giris_yap')
def admin_export_futbol(request):
    return export_futbol_excel()


@staff_member_required(login_url='giris_yap')
def admin_export_tum(request):
    return export_tum_excel()


@staff_member_required(login_url='giris_yap')
def admin_export_kullanicilar(request):
    return export_kullanicilar_excel()


@staff_member_required(login_url='giris_yap')
def excel_indir_basketbol(request):
    return export_basketbol_excel()


@staff_member_required(login_url='giris_yap')
def excel_indir_futbol(request):
    return export_futbol_excel()


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
    
    # Tek sorguda tüm istatistikleri çek
    stats = User.objects.aggregate(
        toplam_kullanici=Count('id'),
        takimsiz_kullanici=Count('id', filter=Q(basketbol_takimi__isnull=True, futbol_takimi__isnull=True)),
        her_iki_takim=Count('id', filter=Q(basketbol_takimi__isnull=False, futbol_takimi__isnull=False)),
    )
    
    takim_stats = BasketbolTakimi.objects.aggregate(
        basketbol_sayisi=Count('id'),
        son_7_gun_basketbol=Count('id', filter=Q(kayit_tarihi__gte=s7)),
        son_30_gun_basketbol=Count('id', filter=Q(kayit_tarihi__gte=s30)),
    )
    
    futbol_stats = FutbolTakimi.objects.aggregate(
        futbol_sayisi=Count('id'),
        son_7_gun_futbol=Count('id', filter=Q(kayit_tarihi__gte=s7)),
        son_30_gun_futbol=Count('id', filter=Q(kayit_tarihi__gte=s30)),
    )
    
    oyuncu_stats = {
        'basketbol_oyuncu': BasketbolOyuncu.objects.count(),
        'futbol_oyuncu': FutbolOyuncu.objects.count(),
    }
    
    duyuru_stats = Duyuru.objects.aggregate(
        toplam_duyuru=Count('id'),
        aktif_duyuru=Count('id', filter=Q(aktif=True)),
    )
    
    return {
        **stats,
        **takim_stats,
        **futbol_stats,
        **oyuncu_stats,
        **duyuru_stats,
        'toplam_takim': takim_stats['basketbol_sayisi'] + futbol_stats['futbol_sayisi'],
        'toplam_oyuncu': oyuncu_stats['basketbol_oyuncu'] + oyuncu_stats['futbol_oyuncu'],
    }
