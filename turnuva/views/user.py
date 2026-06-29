# turnuva/views/user.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from turnuva.models import BasketbolTakimi, BasketbolOyuncu, FutbolTakimi, FutbolOyuncu, Turnuva, Mac


@login_required(login_url='giris_yap')
def profil(request):
    """Kullanıcı profili - Takım bilgileri ve rakipler"""
    basketbol_takimi = BasketbolTakimi.objects.filter(kaptan=request.user).first()
    futbol_takimi = FutbolTakimi.objects.filter(kaptan=request.user).first()
    
    rakipler = []
    
    if basketbol_takimi:
        maclar = Mac.objects.filter(
            takim1_tip='basketbol',
            takim1_id=basketbol_takimi.pk,
            durum='bekliyor'
        ).select_related('turnuva')
        
        for mac in maclar:
            rakip_takim = BasketbolTakimi.objects.filter(pk=mac.takim2_id).first()
            if rakip_takim:
                rakipler.append({
                    'takim': rakip_takim.takim_adi,
                    'kaptan': rakip_takim.kaptan.username,
                    'telefon': rakip_takim.telefon,
                    'tur': mac.tur,
                    'turnuva': mac.turnuva.ad,
                    'tarih': mac.tarih,
                    'durum': mac.durum,
                })
    
    if futbol_takimi:
        maclar = Mac.objects.filter(
            takim1_tip='futbol',
            takim1_id=futbol_takimi.pk,
            durum='bekliyor'
        ).select_related('turnuva')
        
        for mac in maclar:
            rakip_takim = FutbolTakimi.objects.filter(pk=mac.takim2_id).first()
            if rakip_takim:
                rakipler.append({
                    'takim': rakip_takim.takim_adi,
                    'kaptan': rakip_takim.kaptan.username,
                    'telefon': rakip_takim.telefon,
                    'tur': mac.tur,
                    'turnuva': mac.turnuva.ad,
                    'tarih': mac.tarih,
                    'durum': mac.durum,
                })
    
    context = {
        'basketbol_takimi': basketbol_takimi,
        'futbol_takimi': futbol_takimi,
        'rakipler': rakipler,
    }
    return render(request, 'turnuva/profil.html', context)


@login_required(login_url='giris_yap')
def basketbol_takim_yonetimi(request):
    """Basketbol takımı oluşturma/düzenleme"""
    takim = BasketbolTakimi.objects.filter(kaptan=request.user).first()
    
    if request.method == 'POST':
        takim_adi = request.POST.get('takim_adi')
        telefon = request.POST.get('telefon')
        
        if not takim_adi or not telefon:
            messages.error(request, 'Tüm alanları doldurunuz.')
            return redirect('profil')
        
        if takim:
            # Mevcut takımı güncelle
            takim.takim_adi = takim_adi
            takim.telefon = telefon
            takim.save()
            
            # Mevcut oyuncuları güncelle veya ekle
            mevcut_oyuncular = list(takim.oyuncular.all().order_by('id'))
            for i in range(1, 5):
                ad = request.POST.get(f'oyuncu{i}_ad')
                soyad = request.POST.get(f'oyuncu{i}_soyad')
                tc_no = request.POST.get(f'oyuncu{i}_tc')
                
                if ad and soyad and tc_no:
                    if i-1 < len(mevcut_oyuncular):
                        oyuncu = mevcut_oyuncular[i-1]
                        oyuncu.ad = ad
                        oyuncu.soyad = soyad
                        oyuncu.tc_no = tc_no
                        oyuncu.save()
                    else:
                        BasketbolOyuncu.objects.create(
                            takim=takim,
                            ad=ad,
                            soyad=soyad,
                            tc_no=tc_no
                        )
            
            messages.success(request, 'Basketbol takımınız başarıyla güncellendi!')
        else:
            # Yeni takım oluştur
            takim = BasketbolTakimi.objects.create(
                kaptan=request.user,
                takim_adi=takim_adi,
                telefon=telefon
            )
            
            for i in range(1, 5):
                ad = request.POST.get(f'oyuncu{i}_ad')
                soyad = request.POST.get(f'oyuncu{i}_soyad')
                tc_no = request.POST.get(f'oyuncu{i}_tc')
                
                if ad and soyad and tc_no:
                    BasketbolOyuncu.objects.create(
                        takim=takim,
                        ad=ad,
                        soyad=soyad,
                        tc_no=tc_no
                    )
            
            messages.success(request, 'Basketbol takımınız başarıyla oluşturuldu!')
        
        return redirect('profil')
    
    context = {'takim': takim}
    return render(request, 'turnuva/basketbol_yonetim.html', context)


@login_required(login_url='giris_yap')
def futbol_takim_yonetimi(request):
    """Futbol takımı oluşturma/yönetme"""
    takim = FutbolTakimi.objects.filter(kaptan=request.user).first()
    
    if request.method == 'POST':
        if takim:
            messages.error(request, 'Zaten bir futbol takımınız var.')
            return redirect('profil')
        
        takim_adi = request.POST.get('takim_adi')
        telefon = request.POST.get('telefon')
        
        if not takim_adi or not telefon:
            messages.error(request, 'Tüm alanları doldurunuz.')
            return redirect('profil')
        
        takim = FutbolTakimi.objects.create(
            kaptan=request.user,
            takim_adi=takim_adi,
            telefon=telefon
        )
        
        for i in range(1, 9):
            ad = request.POST.get(f'oyuncu{i}_ad')
            soyad = request.POST.get(f'oyuncu{i}_soyad')
            tc_no = request.POST.get(f'oyuncu{i}_tc')
            
            if ad and soyad and tc_no:
                FutbolOyuncu.objects.create(
                    takim=takim,
                    ad=ad,
                    soyad=soyad,
                    tc_no=tc_no
                )
        
        messages.success(request, 'Futbol takımınız başarıyla oluşturuldu!')
        return redirect('profil')
    
    context = {'takim': takim}
    return render(request, 'turnuva/futbol_yonetim.html', context)