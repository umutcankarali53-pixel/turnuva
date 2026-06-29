# turnuva/utils/excel.py

import pandas as pd
from django.http import StreamingHttpResponse
from io import BytesIO


class ExcelStreamMixin:
    """Excel export için streaming response sağlayan mixin"""
    
    @staticmethod
    def generate_excel_stream(data_frames, sheet_names, filename):
        """
        Streaming Excel response oluşturur
        
        Args:
            data_frames: pandas DataFrame listesi
            sheet_names: Sayfa adları listesi
            filename: İndirilecek dosya adı
        """
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for df, sheet_name in zip(data_frames, sheet_names):
                df.to_excel(writer, index=False, sheet_name=sheet_name)
        
        output.seek(0)
        
        response = StreamingHttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = output.tell()
        
        return response


def export_basketbol_excel():
    """Basketbol takımlarını Excel olarak export et"""
    from .models import BasketbolTakimi
    
    veri = []
    for t in BasketbolTakimi.objects.select_related('kaptan').prefetch_related('oyuncular'):
        s = {'Takim Adi': t.takim_adi, 'Kaptan': t.kaptan.username, 'Telefon': t.telefon}
        for i, o in enumerate(t.oyuncular.all(), 1):
            s[f'Oyuncu{i}'] = f'{o.ad} {o.soyad} ({o.get_tc_no()})'
        veri.append(s)
    
    df = pd.DataFrame(veri)
    return ExcelStreamMixin.generate_excel_stream([df], ['Basketbol'], 'Basketbol_Tum_Kayitlar.xlsx')


def export_futbol_excel():
    """Futbol takımlarını Excel olarak export et"""
    from .models import FutbolTakimi
    
    veri = []
    for t in FutbolTakimi.objects.select_related('kaptan').prefetch_related('oyuncular'):
        s = {'Takim Adi': t.takim_adi, 'Kaptan': t.kaptan.username, 'Telefon': t.telefon}
        for i, o in enumerate(t.oyuncular.all(), 1):
            s[f'Oyuncu{i}'] = f'{o.ad} {o.soyad} ({o.get_tc_no()})'
        veri.append(s)
    
    df = pd.DataFrame(veri)
    return ExcelStreamMixin.generate_excel_stream([df], ['Futbol'], 'Futbol_Tum_Kayitlar.xlsx')


def export_tum_excel():
    """Tüm takımları Excel olarak export et"""
    from ..models import BasketbolTakimi, FutbolTakimi
    
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
    
    df_bb = pd.DataFrame(bb)
    df_fb = pd.DataFrame(fb)
    return ExcelStreamMixin.generate_excel_stream(
        [df_bb, df_fb], 
        ['Basketbol', 'Futbol'], 
        'Turnuva_Tum_Veriler.xlsx'
    )


def export_kullanicilar_excel():
    """Kullanıcıları Excel olarak export et"""
    from django.contrib.auth.models import User
    from .models import BasketbolTakimi, FutbolTakimi
    
    veri = [{
        'Kullanici': u.username, 
        'E-posta': u.email,
        'BB': 'Evet' if BasketbolTakimi.objects.filter(kaptan=u).exists() else 'Hayir',
        'FB': 'Evet' if FutbolTakimi.objects.filter(kaptan=u).exists() else 'Hayir'
    } for u in User.objects.order_by('-date_joined')]
    
    df = pd.DataFrame(veri)
    return ExcelStreamMixin.generate_excel_stream([df], ['Kullanicilar'], 'Kullanicilar.xlsx')