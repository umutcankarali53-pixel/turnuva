# turnuva/middleware.py

from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from .models import SayfaGoruntuleme
import hashlib


class SayfaGoruntulemeMiddleware:
    """Sayfa ziyaretlerini takip eden middleware"""
    
    # Takip edilecek sayfalar ve Türkçe adları
    SAYFA_MAP = {
        '/': 'Ana Sayfa',
        '/kayit/': 'Kayıt Sayfası',
        '/giris/': 'Giriş Sayfası',
        '/profil/': 'Profil Sayfası',
        '/fikstur/': 'Fikstür Sayfası',
        '/duyurular/': 'Duyurular Sayfası',
        '/basketbol-yonetim/': 'Basketbol Takım Yönetimi',
        '/futbol-yonetim/': 'Futbol Takım Yönetimi',
        '/yonetim/': 'Admin Dashboard',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Response'u al
        response = self.get_response(request)

        # Sadece GET isteklerini ve 200 status code'ları takip et
        if request.method == 'GET' and response.status_code == 200:
            path = request.path
            
            # Sadece takip edilen sayfaları kaydet
            if path in self.SAYFA_MAP:
                self._kaydet_goruntuleme(request, path)

        return response

    def _kaydet_goruntuleme(self, request, path):
        """Sayfa görüntüleme kaydını veritabanına kaydet"""
        try:
            # IP hash oluştur (anonim)
            ip_address = self._get_client_ip(request)
            ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()[:64] if ip_address else ''
            
            # Session key
            session_key = request.session.session_key or ''
            
            # Sayfa görüntüleme kaydı oluştur
            SayfaGoruntuleme.objects.create(
                sayfa_yolu=path,
                sayfa_adi=self.SAYFA_MAP[path],
                goruntuleme_tarihi=timezone.localtime().date(),
                goruntuleme_saati=timezone.localtime().time(),
                ip_hash=ip_hash,
                session_key=session_key
            )
        except Exception:
            # Hata durumunda sistemi çökertme
            pass

    def _get_client_ip(self, request):
        """Kullanıcının IP adresini al"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip