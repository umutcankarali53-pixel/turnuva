# turnuva/admin.py

import pandas as pd
from django.contrib import admin
from django.http import HttpResponse
from .models import Duyuru, BasketbolTakimi, BasketbolOyuncu, FutbolTakimi, FutbolOyuncu

admin.site.site_header = 'Turnuva Yönetim Sistemi'
admin.site.site_title = 'Turnuva Admin'
admin.site.index_title = 'Veritabanı Yönetimi'


@admin.action(description="Seçili Basketbol Takımlarını Excel'e Aktar")
def basketbol_excel_aktar(modeladmin, request, queryset):
    veri_listesi = []
    for takim in queryset.select_related('kaptan').prefetch_related('oyuncular'):
        satir = {
            'Takım Adı': takim.takim_adi,
            'Kaptan Kullanıcı Adı': takim.kaptan.username,
            'Kaptan E-posta': takim.kaptan.email,
            'İletişim Telefonu': takim.telefon,
            'Kayıt Tarihi': takim.kayit_tarihi.strftime('%Y-%m-%d %H:%M'),
        }
        for i, oyuncu in enumerate(takim.oyuncular.all(), start=1):
            satir[f'Oyuncu {i} Ad'] = oyuncu.ad
            satir[f'Oyuncu {i} Soyad'] = oyuncu.soyad
            satir[f'Oyuncu {i} TC'] = oyuncu.tc_no
        veri_listesi.append(satir)

    df = pd.DataFrame(veri_listesi)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=basketbol_kayitlari.xlsx'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Basketbol')
    return response


@admin.action(description="Seçili Futbol Takımlarını Excel'e Aktar")
def futbol_excel_aktar(modeladmin, request, queryset):
    veri_listesi = []
    for takim in queryset.select_related('kaptan').prefetch_related('oyuncular'):
        satir = {
            'Takım Adı': takim.takim_adi,
            'Kaptan Kullanıcı Adı': takim.kaptan.username,
            'Kaptan E-posta': takim.kaptan.email,
            'İletişim Telefonu': takim.telefon,
            'Kayıt Tarihi': takim.kayit_tarihi.strftime('%Y-%m-%d %H:%M'),
        }
        for i, oyuncu in enumerate(takim.oyuncular.all(), start=1):
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


class BasketbolOyuncuInline(admin.TabularInline):
    model = BasketbolOyuncu
    extra = 0
    max_num = 4


class FutbolOyuncuInline(admin.TabularInline):
    model = FutbolOyuncu
    extra = 0
    max_num = 8


@admin.register(Duyuru)
class DuyuruAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'yayinlanma_tarihi', 'aktif')
    list_filter = ('aktif', 'yayinlanma_tarihi')
    search_fields = ('baslik', 'icerik')
    list_editable = ('aktif',)
    date_hierarchy = 'yayinlanma_tarihi'
    ordering = ('-yayinlanma_tarihi',)


@admin.register(BasketbolTakimi)
class BasketbolTakimiAdmin(admin.ModelAdmin):
    list_display = ('takim_adi', 'kaptan', 'telefon', 'oyuncu_sayisi', 'kayit_tarihi')
    search_fields = ('takim_adi', 'telefon', 'kaptan__username', 'kaptan__email')
    list_filter = ('kayit_tarihi',)
    date_hierarchy = 'kayit_tarihi'
    inlines = [BasketbolOyuncuInline]
    actions = [basketbol_excel_aktar]
    readonly_fields = ('kayit_tarihi',)

    @admin.display(description='Oyuncu')
    def oyuncu_sayisi(self, obj):
        return obj.oyuncular.count()


@admin.register(FutbolTakimi)
class FutbolTakimiAdmin(admin.ModelAdmin):
    list_display = ('takim_adi', 'kaptan', 'telefon', 'oyuncu_sayisi', 'kayit_tarihi')
    search_fields = ('takim_adi', 'telefon', 'kaptan__username', 'kaptan__email')
    list_filter = ('kayit_tarihi',)
    date_hierarchy = 'kayit_tarihi'
    inlines = [FutbolOyuncuInline]
    actions = [futbol_excel_aktar]
    readonly_fields = ('kayit_tarihi',)

    @admin.display(description='Oyuncu')
    def oyuncu_sayisi(self, obj):
        return obj.oyuncular.count()


@admin.register(BasketbolOyuncu)
class BasketbolOyuncuAdmin(admin.ModelAdmin):
    list_display = ('ad', 'soyad', 'tc_no', 'takim')
    search_fields = ('ad', 'soyad', 'tc_no', 'takim__takim_adi')
    list_filter = ('takim',)


@admin.register(FutbolOyuncu)
class FutbolOyuncuAdmin(admin.ModelAdmin):
    list_display = ('ad', 'soyad', 'tc_no', 'takim')
    search_fields = ('ad', 'soyad', 'tc_no', 'takim__takim_adi')
    list_filter = ('takim',)
