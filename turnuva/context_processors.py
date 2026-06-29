from django.conf import settings
from django.utils import timezone
from .models import SiteAyar, SayfaGoruntuleme


def site_ayarlari(request):
    """Site ayarlarını ve istatistikleri template'lere gönder"""
    context = {'site': getattr(settings, 'SITE_AYARLARI', {})}
    
    # SiteAyar verilerini al (KVKK, kayıt bitiş tarihi vb.)
    site_ayar = SiteAyar.objects.filter(aktif=True).first()
    if site_ayar:
        context['site_ayar'] = site_ayar
        context['kayit_acik'] = site_ayar.kayit_bitis_tarihi > timezone.now() if site_ayar.kayit_bitis_tarihi else True
    else:
        context['site_ayar'] = None
        context['kayit_acik'] = True  # Varsayılan olarak açık
    
    return context