# turnuva/admin.py

import pandas as pd
from django.contrib import admin
from django.http import HttpResponse
from .models import Duyuru, BasketbolTakimi, BasketbolOyuncu, FutbolTakimi, FutbolOyuncu

# -----------------------------------------------------------------------------
# EXCEL EXPORT FONKSİYONLARI (ADMIN AKSİYONLARI)
# -----------------------------------------------------------------------------

@admin.action(description="Seçili Basketbol Takımlarını Excel'e Aktar")
def basketbol_excel_aktar(modeladmin, request, queryset):
    # Excel'de görünecek sütunları hazırlıyoruz
    veri_listesi = []
    
    for takim in queryset:
        # Takıma bağlı oyuncuları çekiyoruz
        oyuncular = takim.oyuncular.all()
        
        # Her takımı satır satır işliyoruz (Oyuncular yan yana listelenecek şekilde)
        satir = {
            'Takım Adı': takim.takim_adi,
            'Kaptan Kullanıcı Adı': takim.kaptan.username,
            'Kaptan E-posta': takim.kaptan.email,
            'İletişim Telefonu': takim.telefon,
            'Kayıt Tarihi': takim.kayit_tarihi.strftime('%Y-%m-%d %H:%M'),
        }
        
        # Maksimum 4 oyuncu olacağını bildiğimiz için döngüyle ekliyoruz
        for i, oyuncu in enumerate(oyuncular, start=1):
            satir[f'Oyuncu {i} Ad'] = oyuncu.ad
            satir[f'Oyuncu {i} Soyad'] = oyuncu.soyad
            satir[f'Oyuncu {i} TC'] = oyuncu.tc_no
            
        veri_listesi.append(satir)
        
    # Pandas ile DataFrame oluşturup Excel'e çeviriyoruz
    df = pd.DataFrame(veri_listesi)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=basketbol_kayitlari.xlsx'
    
    # Excel dosyasını yazıyoruz
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Basketbol')
        
    return response


@admin.action(description="Seçili Futbol Takımlarını Excel'e Aktar")
def futbol_excel_aktar(modeladmin, request, queryset):
    veri_listesi = []
    
    for takim in queryset:
        oyuncular = takim.oyuncular.all()
        
        satir = {
            'Takım Adı': takim.takim_adi,
            'Kaptan Kullanıcı Adı': takim.kaptan.username,
            'Kaptan E-posta': takim.kaptan.email,
            'İletişim Telefonu': takim.telefon,
            'Kayıt Tarihi': takim.kayit_tarihi.strftime('%Y-%m-%d %H:%M'),
        }
        
        # Futbolda 8 oyuncu olduğu için 8'e kadar dönüyoruz
        for i, oyuncu in enumerate(oyuncular, start=1):
            satir[f'Oyuncu {i} Ad'] = oyuncu.ad
            satir[f'Oyuncu {i} Soyad'] = oyuncu.soyad
            satir[f'Oyuncu {i} TC'] = oyuncu.tc_no
            
        veri_listesi.append(satir)
        
    df = pd.DataFrame(veri_listesi)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=futbol_kayitlari.xlsx'
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Futbol')
        
    return response

# -----------------------------------------------------------------------------
# OYUNCU SATIRİÇİ (INLINE) GÖRÜNÜMLERİ
# -----------------------------------------------------------------------------
# Takımlara tıkladığında altlarında oyuncuların listelenmesini sağlar

class BasketbolOyuncuInline(admin.TabularInline):
    model = BasketbolOyuncu
    extra = 4  # Varsayılan olarak 4 boş satır getirir
    max_num = 4  # Maksimum 4 oyuncu eklenebilir

class FutbolOyuncuInline(admin.TabularInline):
    model = FutbolOyuncu
    extra = 8  # Varsayılan olarak 8 boş satır getirir
    max_num = 8  # Maksimum 8 oyuncu eklenebilir

# -----------------------------------------------------------------------------
# MODEL REGİSTRASYONLARI
# -----------------------------------------------------------------------------

@admin.register(Duyuru)
class DuyuruAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'yayinlanma_tarihi', 'aktif')
    list_filter = ('aktif', 'yayinlanma_tarihi')
    search_fields = ('baslik', 'icerik')


@admin.register(BasketbolTakimi)
class BasketbolTakimiAdmin(admin.ModelAdmin):
    list_display = ('takim_adi', 'kaptan', 'telefon', 'kayit_tarihi')
    search_fields = ('takim_adi', 'telefon', 'kaptan__username')
    inlines = [BasketbolOyuncuInline]
    actions = [basketbol_excel_aktar]  # Excel butonumuzu bağlıyoruz


@admin.register(FutbolTakimi)
class FutbolTakimiAdmin(admin.ModelAdmin):
    list_display = ('takim_adi', 'kaptan', 'telefon', 'kayit_tarihi')
    search_fields = ('takim_adi', 'telefon', 'kaptan__username')
    inlines = [FutbolOyuncuInline]
    actions = [futbol_excel_aktar]  