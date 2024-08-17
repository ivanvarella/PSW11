"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

# Imports para o funcionamento das imagens (MEDIA)
from django.conf import (
    settings,
)  # É o import do arquivo settings.py mesmo, para poder pegar o MEDIA_URL e o MEDIA_ROOT de lá
from django.conf.urls.static import (
    static,
)  # Esse é aquele static lá que eu ainda não entendi muito - pesquisar mais...

from django.shortcuts import redirect


urlpatterns = [
    path("admin/", admin.site.urls),
    path("usuarios/", include("usuarios.urls")),
    path("empresarios/", include("empresarios.urls")),
    path("investidores/", include("investidores.urls")),
    # Nesse caso, nãe está sendo feito uma rota, está sendo redirecionado usando o lambda, ou seja,
    # sempre que for acessado "", é executado o lambda, que por sua vez executa o método redirect().
    # Utiliza o request do usuário.
    path(
        "", lambda request: redirect("/empresa/cadatrar_empresa")
    ),  # Home -> Cadastrar Empresa
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
