# turnuva/admin.py

import pandas as pd
from django.contrib import admin
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django import forms
from .models import Duyuru, BasketbolTakimi, BasketbolOyuncu, FutbolTakimi, FutbolOyuncu, SiteAyar, SayfaGoruntuleme, Turnuva, Mac

admin.site.site_header = 'Turnuva Yönetim Sistemi'
admin.site.site_title = 'Turnuva Admin'
admin.site.index_title = 'Veritabanı Yönetimi'


# SiteAyar Admin - Singleton pattern için özel form
class SiteAyarForm(forms.ModelForm):
    class Meta:
        model = SiteAyar
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk and SiteAyar.objects.exists():
            raise forms.ValidationError("Sadece bir site ayarı kaydı olabilir. Mevcut kaydı düzenleyin.")
        return cleaned_data


@admin.register(SiteAyar)
class SiteAyarAdmin(admin.ModelAdmin):
    form = SiteAyarForm
    list_display = ('kayit_bitis_tarihi', 'aktif')
    list_display_links = ('kayit_bitis_tarihi',)
    fieldsets = (
        ('KVKK Ayarları', {
            'fields': ('kvkk_text',)
        }),
        ('Kayıt Ayarları', {
            'fields': ('kayit_bitis_tarihi',)
        }),
        ('WhatsApp Bildirim Ayarları', {
            'fields': ('whatsapp_api_token', 'whatsapp_phone_number_id', 'whatsapp_recipient_number'),
            'classes': ('collapse',)
        }),
        ('Durum', {
            'fields': ('aktif',)
        }),
    )

    def has_add_permission(self, request):
        # Singleton pattern: Sadece 1 kayıt olabilir
        if SiteAyar.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Silmeyi engelle
        return False


@admin.register(SayfaGoruntuleme)
class SayfaGoruntulemeAdmin(admin.ModelAdmin):
    list_display = ('sayfa_adi', 'goruntuleme_tarihi', 'goruntuleme_saati', 'ip_hash')
    list_filter = ('sayfa_yolu', 'goruntuleme_tarihi')
    search_fields = ('sayfa_adi', 'sayfa_yolu')
    readonly_fields = ('sayfa_yolu', 'sayfa_adi', 'goruntuleme_tarihi', 'goruntuleme_saati', 'ip_hash', 'session_key')
    date_hierarchy = 'goruntuleme_tarihi'
    ordering = ['-goruntuleme_tarihi', '-goruntuleme_saati']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Turnuva)
class TurnuvaAdmin(admin.ModelAdmin):
    list_display = ('ad', 'brans', 'durum', 'kayit_bitis_tarihi', 'olusturma_tarihi')
    list_filter = ('brans', 'durum', 'olusturma_tarihi')
    search_fields = ('ad',)
    date_hierarchy = 'olusturma_tarihi'
    ordering = ['-olusturma_tarihi']


@admin.register(Mac)
class MacAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'turnuva', 'tur', 'mac_sirasi', 'durum', 'tarih')
    list_filter = ('turnuva', 'tur', 'durum', 'tarih')
    search_fields = ('takim1_adi', 'takim2_adi')
    ordering = ['turnuva', 'tur', 'mac_sirasi']


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