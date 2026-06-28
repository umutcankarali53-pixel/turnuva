# turnuva/forms.py

from django import forms
from django.forms import inlineformset_factory
from .models import BasketbolTakimi, BasketbolOyuncu, FutbolTakimi, FutbolOyuncu , Duyuru


# ---------------- BASKETBOL FORMLARI ----------------

class BasketbolTakimiForm(forms.ModelForm):
    class Meta:
        model = BasketbolTakimi
        fields = ['takim_adi', 'telefon']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Ad'}),
            'soyad': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Soyad'}),
            'tc_no': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': '11 Haneli TC', 'maxlength': '11', 'type': 'number'})
        }

class BasketbolOyuncuForm(forms.ModelForm):
    class Meta:
        model = BasketbolOyuncu
        fields = ['ad', 'soyad', 'tc_no']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Ad'}),
            'soyad': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Soyad'}),
            'tc_no': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': '11 Haneli TC', 'maxlength': '11', 'type': 'number'})
        }

# Basketbol için 1 Takıma bağlı 4 Oyuncu formu üreten Formset
BasketbolOyuncuFormSet = inlineformset_factory(
    BasketbolTakimi, BasketbolOyuncu,
    form=BasketbolOyuncuForm,
    extra=4,       # Ekranda 4 boş form çıkar
    max_num=4,     # Maksimum 4 form olabilir
    can_delete=False # Formların silinmesini kapatıyoruz, sadece güncellenebilir
)


# ---------------- FUTBOL FORMLARI ----------------

class FutbolTakimiForm(forms.ModelForm):
    class Meta:
        model = FutbolTakimi
        fields = ['takim_adi', 'telefon']
        widgets = {
            'takim_adi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Örn: Şampiyonlar'}),
            'telefon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0555...'})
        }

class FutbolOyuncuForm(forms.ModelForm):
    class Meta:
        model = FutbolOyuncu
        fields = ['ad', 'soyad', 'tc_no']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ad'}),
            'soyad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Soyad'}),
            'tc_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '11 Haneli TC', 'maxlength': '11'})
        }

# Futbol için 1 Takıma bağlı 8 Oyuncu formu üreten Formset
FutbolOyuncuFormSet = inlineformset_factory(
    FutbolTakimi, FutbolOyuncu,
    form=FutbolOyuncuForm,
    extra=8,       # Ekranda 8 boş form çıkar
    max_num=8,
    can_delete=False
)

class DuyuruForm(forms.ModelForm):
    class Meta:
        model = Duyuru
        fields = ['baslik', 'icerik', 'aktif']
        widgets = {
            'baslik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Duyuru Başlığı'}),
            'icerik': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Duyuru İçeriği'}),
            'aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }