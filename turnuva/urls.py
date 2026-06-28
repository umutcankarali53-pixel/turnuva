# turnuva/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.ana_sayfa, name='ana_sayfa'),
    path('duyurular/', views.duyurular_sayfasi, name='duyurular'),

    path('kayit/', views.kayit_ol, name='kayit_ol'),
    path('giris/', views.giris_yap, name='giris_yap'),
    path('cikis/', views.cikis_yap, name='cikis_yap'),

    path('profil/', views.profil, name='profil'),

   
    path('basketbol-yonetim/', views.basketbol_takim_yonetimi, name='basketbol_yonetim'),
    path('futbol-yonetim/', views.futbol_takim_yonetimi, name='futbol_yonetim'),
    path('yonetim/', views.ozel_yonetim_paneli, name='ozel_yonetim'),
    path('yonetim/excel-basketbol/', views.excel_indir_basketbol, name='excel_indir_basketbol'),
    path('yonetim/excel-futbol/', views.excel_indir_futbol, name='excel_indir_futbol'),

    
]
