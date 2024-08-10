# Arquivo urls.py dentro de usuarios foi criado manualmente
# Esse arquivo é responsável por criar as urls da aplicação

from django.urls import path
from . import views

urlpatterns = [
    path("cadastro/", views.cadastro, name="cadastro"),
    path("logar/", views.logar, name="logar"),
]
