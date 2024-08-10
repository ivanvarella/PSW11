from django.contrib import admin

# Register your models here.


# Adicionar a classe empresarios e documento na área administrativa do Django
from .models import Empresas, Documento, Metricas

admin.site.register(Empresas)
admin.site.register(Documento)
admin.site.register(Metricas)
