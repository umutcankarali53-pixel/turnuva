# turnuva/utils/whatsapp.py

import requests
from django.conf import settings
from django.utils import timezone
from ..models import SiteAyar


def whatsapp_bildirim_gonder(takim_adi, kaptan_adi, telefon, brans):
    """
    Yeni takım kaydı olduğunda admin'e WhatsApp mesajı gönder
    
    Args:
        takim_adi: Takımın adı
        kaptan_adi: Kaptanın adı soyadı
        telefon: İletişim telefonu
        brans: Branş (Basketbol/Futbol)
    """
    try:
        # Site ayarlarını al
        site_ayar = SiteAyar.objects.filter(aktif=True).first()
        if not site_ayar:
            return False
        
        # WhatsApp API bilgileri kontrol et
        if not all([
            site_ayar.whatsapp_api_token,
            site_ayar.whatsapp_phone_number_id,
            site_ayar.whatsapp_recipient_number
        ]):
            return False
        
        # Mesaj içeriği
        mesaj = f"""🏆 YENİ TAKIM KAYDI!

📋 Takım Adı: {takim_adi}
👤 Kaptan: {kaptan_adi}
📞 Telefon: {telefon}
🏅 Branş: {brans}
⏰ Kayıt Zamanı: {timezone.localtime().strftime('%d.%m.%Y %H:%M')}

Turnuva kayıt sistemine yeni bir takım eklendi."""

        # WhatsApp Cloud API endpoint
        url = f"https://graph.facebook.com/v18.0/{site_ayar.whatsapp_phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {site_ayar.whatsapp_api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": site_ayar.whatsapp_recipient_number,
            "type": "text",
            "text": {
                "body": mesaj
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # Başarılı response kontrolü
        if response.status_code == 200:
            return True
        else:
            # Hata logla ama sistemi çökertme
            print(f"WhatsApp bildirim hatası: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        # Hata durumunda sistemi çökertme
        print(f"WhatsApp bildirim gönderme hatası: {str(e)}")
        return False