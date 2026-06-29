# turnuva/utils/excel.py

import pandas as pd
from django.http import HttpResponse
from io import BytesIO


def export_basketbol_excel():
    """Basketbol takımlarını Excel olarak export et"""
    from turnuva.models import BasketbolTakimi
    
    veri = []
    for t in BasketbolTakimi.objects.select_related('kaptan').prefetch_related('oyuncular'):
        s = {'Takim Adi': t.takim_adi, 'Kaptan': t.kaptan.username, 'Telefon': t.telefon}
        for i, o in enumerate(t.oyuncular.all(), 1):
            s[f'Oyuncu{i}'] = f'{o.ad} {o.soyad} ({o.get_tc_no()})'
        veri.append(s)
    
    df = pd.DataFrame(veri)
    return _create_excel_response(df, 'Basketbol_Tum_Kayitlar.xlsx')


def export_futbol_excel():
    """Futbol takımlarını Excel olarak export et"""
    from turnuva.models import FutbolTakimi
    
    veri = []
    for t in FutbolTakimi.objects.select_related('kaptan').prefetch_related('oyuncular'):
        s = {'Takim Adi': t.takim_adi, 'Kaptan': t.kaptan.username, 'Telefon': t.telefon}
        for i, o in enumerate(t.oyuncular.all(), 1):
            s[f'Oyuncu{i}'] = f'{o.ad} {o.soyad} ({o.get_tc_no()})'
        veri.append(s)
    
    df = pd.DataFrame(veri)
    return _create_excel_response(df, 'Futbol_Tum_Kayitlar.xlsx')


def export_tum_excel():
    """Tüm takımları Excel olarak export et"""
    from turnuva.models import BasketbolTakimi, FutbolTakimi
    
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
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame(bb if bb else [{'Not': 'Veri yok'}]).to_excel(writer, index=False, sheet_name='Basketbol')
        pd.DataFrame(fb if fb else [{'Not': 'Veri yok'}]).to_excel(writer, index=False, sheet_name='Futbol')
    
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="Turnuva_Tum_Veriler.xlsx"'
    response['Content-Length'] = len(output.getvalue())
    return response


def export_kullanicilar_excel():
    """Kullanıcıları Excel olarak export et"""
    from django.contrib.auth.models import User
    from turnuva.models import BasketbolTakimi, FutbolTakimi
    
    veri = [{
        'Kullanici': u.username, 
        'E-posta': u.email,
        'BB': 'Evet' if BasketbolTakimi.objects.filter(kaptan=u).exists() else 'Hayir',
        'FB': 'Evet' if FutbolTakimi.objects.filter(kaptan=u).exists() else 'Hayir'
    } for u in User.objects.order_by('-date_joined')]
    
    df = pd.DataFrame(veri)
    return _create_excel_response(df, 'Kullanicilar.xlsx')


def _create_excel_response(df, filename):
    """Excel response oluştur"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sayfa1')
    
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response