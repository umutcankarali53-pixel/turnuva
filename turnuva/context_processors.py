from django.conf import settings


def site_ayarlari(request):
    return {'site': getattr(settings, 'SITE_AYARLARI', {})}