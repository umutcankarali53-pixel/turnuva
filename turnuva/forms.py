# turnuva/forms.py

import re
from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import BasketbolTakimi, BasketbolOyuncu, FutbolTakimi, FutbolOyuncu, Duyuru


def tc_dogrula(value):
    if not re.match(r'^\d{11}$', value):
        raise ValidationError('TC Kimlik No 11 haneli olmalıdır.')


def telefon_dogrula(value):
    cleaned = re.sub(r'[\s\-()]', '', value)
    if not re.match(r'^(\+90|0)?5\d{9}$', cleaned):
        raise ValidationError('Geçerli bir Türkiye cep telefonu numarası giriniz. (Örn: 05551234567)')


# ---------------- ORTAK FORM SINIFLARI ----------------

class BaseTakimForm(forms.ModelForm):
    """Basketbol ve Futbol takımları için ortak form"""
    
    class Meta:
        fields = ['takim_adi', 'telefon']
        widgets = {
            'takim_adi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Takım adınız'}),
            'telefon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0555 123 45 67'}),
        }

    def clean_telefon(self):
        telefon = self.cleaned_data['telefon']
        telefon_dogrula(telefon)
        return telefon


class BaseOyuncuForm(forms.ModelForm):
    """Basketbol ve Futbol oyuncuları için ortak form"""
    
    class Meta:
        fields = ['ad', 'soyad', 'tc_no']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ad'}),
            'soyad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Soyad'}),
            'tc_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '11 haneli TC', 'maxlength': '11', 'inputmode': 'numeric'}),
        }

    def clean_tc_no(self):
        tc = self.cleaned_data['tc_no']
        tc_dogrula(tc)
        return tc


# ---------------- BASKETBOL FORMLARI ----------------

class BasketbolTakimiForm(BaseTakimForm):
    class Meta(BaseTakimForm.Meta):
        model = BasketbolTakimi


class BasketbolOyuncuForm(BaseOyuncuForm):
    class Meta(BaseOyuncuForm.Meta):
        model = BasketbolOyuncu


BasketbolOyuncuFormSet = inlineformset_factory(
    BasketbolTakimi, BasketbolOyuncu,
    form=BasketbolOyuncuForm,
    extra=4,
    max_num=4,
    can_delete=False,
)


# ---------------- FUTBOL FORMLARI ----------------

class FutbolTakimiForm(BaseTakimForm):
    class Meta(BaseTakimForm.Meta):
        model = FutbolTakimi


class FutbolOyuncuForm(BaseOyuncuForm):
    class Meta(BaseOyuncuForm.Meta):
        model = FutbolOyuncu


FutbolOyuncuFormSet = inlineformset_factory(
    FutbolTakimi, FutbolOyuncu,
    form=FutbolOyuncuForm,
    extra=8,
    max_num=8,
    can_delete=False,
)


# ---------------- DUYURU FORMU ----------------

class DuyuruForm(forms.ModelForm):
    class Meta:
        model = Duyuru
        fields = ['baslik', 'icerik', 'aktif']
        widgets = {
            'baslik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Duyuru başlığı'}),
            'icerik': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Duyuru içeriği'}),
            'aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }