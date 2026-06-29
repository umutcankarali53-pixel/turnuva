# turnuva/views/admin.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, F, Case, When, IntegerField
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from turnuva.forms import DuyuruForm
from turnuva.models import Duyuru, BasketbolTakimi, BasketbolOyuncu, FutbolTakimi, FutbolOyuncu
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