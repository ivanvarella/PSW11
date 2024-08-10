from django.db import models


# Importar Empresas
from empresarios.models import Empresas

# Importar o User do Django - É FK dessa tabela Empresas - que na verdade o Django é faz a normatização do banco, pelo que eu entendi
from django.contrib.auth.models import User


# Create your models here.
class PropostaInvestimento(models.Model):
    status_choices = (
        ("AS", "Aguardando assinatura"),
        ("PE", "Proposta enviada"),
        ("PA", "Proposta aceita"),
        ("PR", "Proposta recusada"),
    )
    valor = models.DecimalField(max_digits=9, decimal_places=2)
    percentual = models.FloatField()
    empresa = models.ForeignKey(Empresas, on_delete=models.DO_NOTHING)
    investidor = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=2, choices=status_choices, default="AS")
    selfie = models.FileField(upload_to="selfie", null=True, blank=True)
    rg = models.FileField(upload_to="rg", null=True, blank=True)

    def __str__(self):
        return str(self.valor)

    @property
    def valuation(self):
        return (100 * float(self.valor)) / float(self.percentual)
