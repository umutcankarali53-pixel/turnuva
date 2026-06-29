# turnuva/views/user.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.paginator import Paginator
from turnuva.forms import BasketbolTakimiForm, BasketbolOyuncuFormSet, FutbolTakimiForm, FutbolOyuncuFormSet
from turnuva.models import BasketbolTakimi, BasketbolOyuncu, FutbolTakimi, FutbolOyuncu


@login_required(login_url='giris_yap')
def profil(request):
    basketbol_takimi = getattr(request.user, 'basketbol_takimi', None)
    futbol_takimi = getattr(request.user, 'futbol_takimi', None)
    
    context = {
        'basketbol_takimi': basketbol_takimi,
        'futbol_takimi': futbol_takimi
    }
    return render(request, 'turnuva/profil.html', context)


@login_required(login_url='giris_yap')
def basketbol_takim_yonetimi(request):
    takim = getattr(request.user, 'basketbol_takimi', None)
    
    if request.method == 'POST':
        form = BasketbolTakimiForm(request.POST, instance=takim)
        formset = BasketbolOyuncuFormSet(request.POST, instance=takim)
        
        if form.is_valid() and formset.is_valid():
            kaydedilen_takim = form.save(commit=False)
            kaydedilen_takim.kaptan = request.user
            kaydedilen_takim.save()
            
            formset.instance = kaydedilen_takim
            formset.save()
            
            messages.success(request, "Basketbol takımınız başarıyla kaydedildi!")
            return redirect('profil')
        else:
            messages.error(request, "Lütfen formdaki hataları kontrol edin. (Bir TC numarası daha önce kullanılmış olabilir!)")
    else:
        form = BasketbolTakimiForm(instance=takim)
        formset = BasketbolOyuncuFormSet(instance=takim)
        
    return render(request, 'turnuva/takim_form.html', {
        'form': form, 
        'formset': formset, 
        'brans': 'Basketbol Takımı'
    })


@login_required(login_url='giris_yap')
def futbol_takim_yonetimi(request):
    takim = getattr(request.user, 'futbol_takimi', None)
    
    if request.method == 'POST':
        form = FutbolTakimiForm(request.POST, instance=takim)
        formset = FutbolOyuncuFormSet(request.POST, instance=takim)
        
        if form.is_valid() and formset.is_valid():
            kaydedilen_takim = form.save(commit=False)
            kaydedilen_takim.kaptan = request.user
            kaydedilen_takim.save()
            
            formset.instance = kaydedilen_takim
            formset.save()
            
            messages.success(request, "Futbol takımınız başarıyla kaydedildi!")
            return redirect('profil')
        else:
            messages.error(request, "Lütfen formdaki hataları kontrol edin.")
    else:
        form = FutbolTakimiForm(instance=takim)
        formset = FutbolOyuncuFormSet(instance=takim)
        
    return render(request, 'turnuva/takim_form.html', {
        'form': form, 
        'formset': formset, 
        'brans': 'Futbol Takımı'
    })