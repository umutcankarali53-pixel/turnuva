# turnuva/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from cryptography.fernet import Fernet
from django.conf import settings
import os


class Duyuru(models.Model):
    """Admin panelinden eklenecek ve ana sayfada popup/bildirim olarak görünecek duyurular"""
    baslik = models.CharField(max_length=200, verbose_name="Duyuru Başlığı")
    icerik = models.TextField(verbose_name="Duyuru İçeriği")
    yayinlanma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Yayınlanma Tarihi")
    aktif = models.BooleanField(default=True, verbose_name="Yayında mı?")

    class Meta:
        verbose_name = "Duyuru"
        verbose_name_plural = "Duyurular"
        ordering = ['-yayinlanma_tarihi']

    def __str__(self):
        return self.baslik


class BasketbolTakimi(models.Model):
    """Her kullanıcının (kaptanın) sadece 1 basketbol takımı olabilir"""
    kaptan = models.OneToOneField(User, on_delete=models.CASCADE, related_name='basketbol_takimi', verbose_name="Takım Kaptanı")
    takim_adi = models.CharField(max_length=100, verbose_name="Takım Adı")
    telefon = models.CharField(max_length=15, verbose_name="İletişim Telefonu")
    kayit_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Basketbol Takımı"
        verbose_name_plural = "Basketbol Takımları"

    def __str__(self):
        return self.takim_adi


class BasketbolOyuncu(models.Model):
    """Bir basketbol takımına bağlı 4 oyuncu tutulur"""
    takim = models.ForeignKey(BasketbolTakimi, on_delete=models.CASCADE, related_name='oyuncular')
    ad = models.CharField(max_length=50, verbose_name="Ad")
    soyad = models.CharField(max_length=50, verbose_name="Soyad")
    tc_no = models.CharField(max_length=255, verbose_name="TC Kimlik No")

    def save(self, *args, **kwargs):
        if self.tc_no and not self.tc_no.startswith('gAAAAA'):
            self.tc_no = self._encrypt(self.tc_no)
        super().save(*args, **kwargs)

    @staticmethod
    def _encrypt(value):
        key = os.environ.get('ENCRYPTION_KEY') or getattr(settings, 'ENCRYPTION_KEY', None)
        if not key:
            key = Fernet.generate_key()
            if os.environ.get('DJANGO_SETTINGS_MODULE'):
                os.environ['ENCRYPTION_KEY'] = key.decode()
        f = Fernet(key if isinstance(key, bytes) else key.encode())
        return f.encrypt(value.encode()).decode()

    @staticmethod
    def _decrypt(value):
        key = os.environ.get('ENCRYPTION_KEY') or getattr(settings, 'ENCRYPTION_KEY', None)
        if not key:
            return value
        f = Fernet(key if isinstance(key, bytes) else key.encode())
        try:
            return f.decrypt(value.encode()).decode()
        except Exception:
            return value

    def get_tc_no(self):
        return self._decrypt(self.tc_no)

    class Meta:
        verbose_name = "Basketbol Oyuncusu"
        verbose_name_plural = "Basketbol Oyuncuları"

    def __str__(self):
        return f"{self.ad} {self.soyad} ({self.takim.takim_adi})"


class FutbolTakimi(models.Model):
    """Her kullanıcının (kaptanın) sadece 1 futbol takımı olabilir"""
    kaptan = models.OneToOneField(User, on_delete=models.CASCADE, related_name='futbol_takimi', verbose_name="Takım Kaptanı")
    takim_adi = models.CharField(max_length=100, verbose_name="Takım Adı")
    telefon = models.CharField(max_length=15, verbose_name="İletişim Telefonu")
    kayit_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Futbol Takımı"
        verbose_name_plural = "Futbol Takımları"

    def __str__(self):
        return self.takim_adi


class FutbolOyuncu(models.Model):
    """Bir futbol takımına bağlı 8 oyuncu tutulur"""
    takim = models.ForeignKey(FutbolTakimi, on_delete=models.CASCADE, related_name='oyuncular')
    ad = models.CharField(max_length=50, verbose_name="Ad")
    soyad = models.CharField(max_length=50, verbose_name="Soyad")
    tc_no = models.CharField(max_length=255, verbose_name="TC Kimlik No")

    def save(self, *args, **kwargs):
        if self.tc_no and not self.tc_no.startswith('gAAAAA'):
            self.tc_no = self._encrypt(self.tc_no)
        super().save(*args, **kwargs)

    @staticmethod
    def _encrypt(value):
        key = os.environ.get('ENCRYPTION_KEY') or getattr(settings, 'ENCRYPTION_KEY', None)
        if not key:
            key = Fernet.generate_key()
            if os.environ.get('DJANGO_SETTINGS_MODULE'):
                os.environ['ENCRYPTION_KEY'] = key.decode()
        f = Fernet(key if isinstance(key, bytes) else key.encode())
        return f.encrypt(value.encode()).decode()

    @staticmethod
    def _decrypt(value):
        key = os.environ.get('ENCRYPTION_KEY') or getattr(settings, 'ENCRYPTION_KEY', None)
        if not key:
            return value
        f = Fernet(key if isinstance(key, bytes) else key.encode())
        try:
            return f.decrypt(value.encode()).decode()
        except Exception:
            return value

    def get_tc_no(self):
        return self._decrypt(self.tc_no)

    class Meta:
        verbose_name = "Futbol Oyuncusu"
        verbose_name_plural = "Futbol Oyuncuları"

    def __str__(self):
        return f"{self.ad} {self.soyad} ({self.takim.takim_adi})"


class SiteAyar(models.Model):
    """Site genel ayarları - KVKK, kayıt bitiş tarihi, WhatsApp bildirimleri"""
    kvkk_text = models.TextField(verbose_name="KVKK Onay Metni")
    kayit_bitis_tarihi = models.DateTimeField(verbose_name="Kayıt Bitiş Tarihi/Saati")
    whatsapp_api_token = models.CharField(max_length=255, blank=True, verbose_name="WhatsApp API Token")
    whatsapp_phone_number_id = models.CharField(max_length=255, blank=True, verbose_name="WhatsApp Phone Number ID")
    whatsapp_recipient_number = models.CharField(max_length=20, blank=True, verbose_name="Bildirim Gönderilecek Numara")
    countdown_baslik = models.CharField(max_length=200, blank=True, verbose_name="Geri Sayım Başlık")
    countdown_ust_baslik = models.CharField(max_length=200, blank=True, verbose_name="Geri Sayım Üst Başlık")
    countdown_alt_baslik = models.CharField(max_length=200, blank=True, verbose_name="Geri Sayım Alt Başlık")
    aktif = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "Site Ayarı"
        verbose_name_plural = "Site Ayarları"

    def __str__(self):
        return "Site Ayarları"

    def save(self, *args, **kwargs):
        if not self.pk and SiteAyar.objects.exists():
            raise ValidationError("Sadece bir site ayarı kaydı olabilir. Mevcut kaydı düzenleyin.")
        super().save(*args, **kwargs)


class SayfaGoruntuleme(models.Model):
    """Sayfa ziyaret analizi - Günlük ve aylık istatistikler için"""
    SAYFA_SECENEKLERI = [
        ('ana_sayfa', 'Ana Sayfa'),
        ('kayit', 'Kayıt Sayfası'),
        ('giris', 'Giriş Sayfası'),
        ('profil', 'Profil Sayfası'),
        ('fikstur', 'Fikstür Sayfası'),
        ('duyurular', 'Duyurular Sayfası'),
        ('basketbol_yonetim', 'Basketbol Takım Yönetimi'),
        ('futbol_yonetim', 'Futbol Takım Yönetimi'),
        ('admin_dashboard', 'Admin Dashboard'),
    ]

    sayfa_yolu = models.CharField(max_length=50, choices=SAYFA_SECENEKLERI, verbose_name="Sayfa Yolu")
    sayfa_adi = models.CharField(max_length=100, verbose_name="Sayfa Adı")
    goruntuleme_tarihi = models.DateField(verbose_name="Görüntüleme Tarihi")
    goruntuleme_saati = models.TimeField(verbose_name="Görüntüleme Saati")
    ip_hash = models.CharField(max_length=64, blank=True, verbose_name="IP Hash (Anonim)")
    session_key = models.CharField(max_length=40, blank=True, verbose_name="Session Key")

    class Meta:
        verbose_name = "Sayfa Görüntüleme"
        verbose_name_plural = "Sayfa Görüntülemeleri"
        indexes = [
            models.Index(fields=['sayfa_yolu', 'goruntuleme_tarihi']),
        ]
        ordering = ['-goruntuleme_tarihi', '-goruntuleme_saati']

    def __str__(self):
        return f"{self.sayfa_adi} - {self.goruntuleme_tarihi}"


class Turnuva(models.Model):
    """Turnuva bilgileri ve durumu"""
    DURUM_SECENEKLERI = [
        ('kayit_acik', 'Kayıt Açık'),
        ('eslesme_yapildi', 'Eşleşme Yapıldı'),
        ('devam_ediyor', 'Devam Ediyor'),
        ('tamamlandi', 'Tamamlandı'),
    ]

    BRANS_SECENEKLERI = [
        ('basketbol', 'Basketbol'),
        ('futbol', 'Futbol'),
    ]

    ad = models.CharField(max_length=200, verbose_name="Turnuva Adı")
    brans = models.CharField(max_length=20, choices=BRANS_SECENEKLERI, verbose_name="Branş")
    durum = models.CharField(max_length=20, choices=DURUM_SECENEKLERI, default='kayit_acik', verbose_name="Durum")
    kayit_bitis_tarihi = models.DateTimeField(verbose_name="Kayıt Bitiş Tarihi")
    olusturma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        verbose_name = "Turnuva"
        verbose_name_plural = "Turnuvalar"
        ordering = ['-olusturma_tarihi']

    def __str__(self):
        return f"{self.ad} ({self.get_brans_display()})"


class Mac(models.Model):
    """Maç/Fikstür yönetimi - Turnuva ağacı için"""
    DURUM_SECENEKLERI = [
        ('bekliyor', 'Bekliyor'),
        ('oynandi', 'Oynandı'),
        ('iptal', 'İptal'),
    ]

    turnuva = models.ForeignKey(Turnuva, on_delete=models.CASCADE, related_name='maclar', verbose_name="Turnuva")
    tur = models.IntegerField(verbose_name="Tur Numarası")
    mac_sirasi = models.IntegerField(verbose_name="Maç Sırası (Tur içinde)")
    
    takim1_tip = models.CharField(max_length=10, choices=[('basketbol', 'Basketbol'), ('futbol', 'Futbol')])
    takim1_id = models.IntegerField(verbose_name="Takım 1 ID")
    takim1_adi = models.CharField(max_length=100, verbose_name="Takım 1 Adı")
    
    takim2_tip = models.CharField(max_length=10, choices=[('basketbol', 'Basketbol'), ('futbol', 'Futbol')])
    takim2_id = models.IntegerField(verbose_name="Takım 2 ID")
    takim2_adi = models.CharField(max_length=100, verbose_name="Takım 2 Adı")
    
    takim1_skor = models.IntegerField(null=True, blank=True, verbose_name="Takım 1 Skoru")
    takim2_skor = models.IntegerField(null=True, blank=True, verbose_name="Takım 2 Skoru")
    
    tarih = models.DateTimeField(null=True, blank=True, verbose_name="Maç Tarihi")
    yer = models.CharField(max_length=200, blank=True, verbose_name="Maç Yeri")
    durum = models.CharField(max_length=20, choices=DURUM_SECENEKLERI, default='bekliyor', verbose_name="Maç Durumu")

    class Meta:
        verbose_name = "Maç"
        verbose_name_plural = "Maçlar"
        indexes = [
            models.Index(fields=['turnuva', 'tur', 'mac_sirasi']),
        ]
        ordering = ['turnuva', 'tur', 'mac_sirasi']

    def __str__(self):
        return f"{self.takim1_adi} vs {self.takim2_adi} - Tur {self.tur}"

    def get_takim1(self):
        if self.takim1_tip == 'basketbol':
            return BasketbolTakimi.objects.filter(pk=self.takim1_id).first()
        else:
            return FutbolTakimi.objects.filter(pk=self.takim1_id).first()

    def get_takim2(self):
        if self.takim2_tip == 'basketbol':
            return BasketbolTakimi.objects.filter(pk=self.takim2_id).first()
        else:
            return FutbolTakimi.objects.filter(pk=self.takim2_id).first()