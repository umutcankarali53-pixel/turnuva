# turnuva/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
    # unique=True sayesinde bir TC, BasketbolOyuncu tablosunda sadece BİR kez var olabilir!
    tc_no = models.CharField(max_length=11, unique=True, verbose_name="TC Kimlik No")

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
    # unique=True sayesinde bir TC, FutbolOyuncu tablosunda sadece BİR kez var olabilir!
    tc_no = models.CharField(max_length=11, unique=True, verbose_name="TC Kimlik No")

    class Meta:
        verbose_name = "Futbol Oyuncusu"
        verbose_name_plural = "Futbol Oyuncuları"

    def __str__(self):
        return f"{self.ad} {self.soyad} ({self.takim.takim_adi})"