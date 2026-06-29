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


FORM_CONTROL = {'class': 'form-control'}


# ---------------- BASKETBOL FORMLARI ----------------

class BasketbolTakimiForm(forms.ModelForm):
    class Meta:
        model = BasketbolTakimi
        fields = ['takim_adi', 'telefon']
        widgets = {
            'takim_adi': forms.TextInput(attrs={**FORM_CONTROL, 'placeholder': 'Takım adınız'}),
            'telefon': forms.TextInput(attrs={**FORM_CONTROL, 'placeholder': '0555 123 45 67'}),
        }

    def clean_telefon(self):
        telefon = self.cleaned_data['telefon']
        telefon_dogrula(telefon)
        return telefon


class BasketbolOyuncuForm(forms.ModelForm):
    class Meta:
        model = BasketbolOyuncu
        fields = ['ad', 'soyad', 'tc_no']
        widgets = {
            'ad': forms.TextInput(attrs={**FORM_CONTROL, 'placeholder': 'Ad'}),
            'soyad': forms.TextInput(attrs={**FORM_CONTROL, 'placeholder': 'Soyad'}),
            'tc_no': forms.TextInput(attrs={**FORM_CONTROL, 'placeholder': '11 haneli TC', 'maxlength': '11', 'inputmode': 'numeric'}),
        }

    def clean_tc_no(self):
        tc = self.cleaned_data['tc_no']
        tc_dogrula(tc)
        return tc


BasketbolOyuncuFormSet = inlineformset_factory(
    BasketbolTakimi, BasketbolOyuncu,
    form=BasketbolOyuncuForm,
    extra=4,
    max_num=4,
    can_delete=False,
)


# ---------------- FUTBOL FORMLARI ----------------

class FutbolTakimiForm(forms.ModelForm):
    class Meta:
        model = FutbolTakimi
        fields = ['takim_adi', 'telefon']
        widgets = {
            'takim_adi': forms.TextInput(attrs={**FORM_CONTROL, 'placeholder': 'Takım adınız'}),
            'telefon': forms.TextInput(attrs={**FORM_CONTROL, 'placeholder': '0555 123 45 67'}),
        }

    def clean_telefon(self):
        telefon = self.cleaned_data['telefon']
        telefon_dogrula(telefon)
        return telefon


class FutbolOyuncuForm(forms.ModelForm):
    class Meta:
        model = FutbolOyuncu
        fields = ['ad', 'soyad', 'tc_no']
        widgets = {
            'ad': forms.TextInput(attrs={**FORM_CONTROL, 'placeholder': 'Ad'}),
            'soyad': forms.TextInput(attrs={**FORM_CONTROL, 'placeholder': 'Soyad'}),
            'tc_no': forms.TextInput(attrs={**FORM_CONTROL, 'placeholder': '11 haneli TC', 'maxlength': '11', 'inputmode': 'numeric'}),
        }

    def clean_tc_no(self):
        tc = self.cleaned_data['tc_no']
        tc_dogrula(tc)
        return tc


FutbolOyuncuFormSet = inlineformset_factory(
    FutbolTakimi, FutbolOyuncu,
    form=FutbolOyuncuForm,
    extra=8,
    max_num=8,
    can_delete=False,
)


class DuyuruForm(forms.ModelForm):
    class Meta:
        model = Duyuru
        fields = ['baslik', 'icerik', 'aktif']
        widgets = {
            'baslik': forms.TextInput(attrs={**FORM_CONTROL, 'placeholder': 'Duyuru başlığı'}),
            'icerik': forms.Textarea(attrs={**FORM_CONTROL, 'rows': 4, 'placeholder': 'Duyuru içeriği'}),
            'aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
