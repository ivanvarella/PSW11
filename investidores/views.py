from django.shortcuts import render, redirect

# Importar os selects dos models
from empresarios.models import Empresas, Documento
from .models import PropostaInvestimento


# Importar as constantes de mensagens do Django
from django.contrib import messages

# Importar os tipos de mensagens do Django
from django.contrib.messages import constants

# Importar Página de erro - http 404
from django.http import Http404


# Create your views here.
def sugestao(request):

    if not request.user.is_authenticated:
        return redirect("/usuarios/logar")

    areas = Empresas.area_choices
    if request.method == "GET":
        return render(request, "sugestao.html", {"areas": areas})
    elif request.method == "POST":
        tipo = request.POST.get("tipo")
        # getlist -> o area é um select multiple e retorna uma lista, não somente um valor
        area = request.POST.getlist("area")
        valor = request.POST.get("valor")

        if tipo == "C":
            empresas = Empresas.objects.filter(tempo_existencia="+5").filter(
                estagio="E"
            )
        # __in -> que esteja dentro da lista. Exemplo: tempo_existencia__in=["-6", "+6", "+1"]
        # exclude -> pega dos filtros anteriores e remove. Exemplo: exclude(estagio="E")
        elif tipo == "D":
            empresas = Empresas.objects.filter(
                tempo_existencia__in=["-6", "+6", "+1"]
            ).exclude(estagio="E")
        # ToDo: Criar um tipo genérico para as empresas, para não repetir código
        elif tipo == "G":
            empresas = Empresas.objects.all()

        empresas = empresas.filter(area__in=area)

        empresas_selecionadas = []
        for empresa in empresas:
            percentual = (float(valor) * 100) / float(empresa.valuation)
            if percentual >= 1:
                empresas_selecionadas.append(empresa)

        return render(
            request,
            "sugestao.html",
            {"empresas": empresas_selecionadas, "areas": areas},
        )


def ver_empresa(request, id):

    if not request.user.is_authenticated:
        return redirect("/usuarios/logar")

    empresa = Empresas.objects.get(id=id)
    documentos = Documento.objects.filter(empresa=empresa)

    proposta_investimentos = PropostaInvestimento.objects.filter(
        empresa=empresa
    ).filter(status="PA")
    percentual_vendido = 0
    for pi in proposta_investimentos:
        percentual_vendido = percentual_vendido + pi.percentual

    # Quantos % precisa vender para chegar nos 80%
    limiar = (80 * empresa.percentual_equity) / 100
    concretizado = False
    if percentual_vendido >= limiar:
        concretizado = True

    percentual_disponivel = empresa.percentual_equity - percentual_vendido

    # ToDo: Listar as métricas dinamicamente
    return render(
        request,
        "ver_empresa.html",
        {
            "empresa": empresa,
            "documentos": documentos,
            "percentual_vendido": int(percentual_vendido),
            "concretizado": concretizado,
            "percentual_disponivel": percentual_disponivel,
        },
    )


def realizar_proposta(request, id):

    if not request.user.is_authenticated:
        return redirect("/usuarios/logar")

    valor = request.POST.get("valor")
    percentual = request.POST.get("percentual")
    empresa = Empresas.objects.get(id=id)

    # Pega todas as propostas dessa empresa que foram aceitas = PA
    propostas_aceitas = PropostaInvestimento.objects.filter(empresa=empresa).filter(
        status="PA"
    )

    # Soma o percentual total de propostas aceitas -> PA
    total = 0
    for pa in propostas_aceitas:
        total = total + pa.percentual

    # O percentual cadastrado desejado para venda que a empresa cadastrou -> empresa.percentual_equity
    # percentual -> quanto o investidor quer comprar agora
    if total + float(percentual) > empresa.percentual_equity:
        messages.add_message(
            request,
            constants.WARNING,
            f"O percentual solicitado ultrapassa o percentual máximo({empresa.percentual_equity}%). \n O percentual disponível para essa empresa é de {empresa.percentual_equity-total}%.",
        )
        return redirect(f"/investidores/ver_empresa/{id}")

    valuation = (100 * int(valor)) / int(percentual)

    # Só aceita até 50% do valuation, menos é descartado
    if valuation < (int(empresa.valuation) / 2):
        messages.add_message(
            request,
            constants.WARNING,
            f"Seu valuation proposto foi R${valuation} e deve ser no mínimo R${empresa.valuation/2}",
        )
        return redirect(f"/investidores/ver_empresa/{id}")

    pi = PropostaInvestimento(
        valor=valor,
        percentual=percentual,
        empresa=empresa,
        investidor=request.user,
    )

    pi.save()

    # messages.add_message(request, constants.SUCCESS, f'Proposta enviada com sucesso')
    return redirect(f"/investidores/assinar_contrato/{pi.id}")


def assinar_contrato(request, id):

    if not request.user.is_authenticated:
        return redirect("/usuarios/logar")

    pi = PropostaInvestimento.objects.get(id=id)
    if pi.status != "AS":
        raise Http404()

    if request.method == "GET":
        return render(request, "assinar_contrato.html", {"pi": pi})
    elif request.method == "POST":
        selfie = request.FILES.get("selfie")
        rg = request.FILES.get("rg")
        print(request.FILES)

        pi.selfie = selfie
        pi.rg = rg
        pi.status = "PE"
        pi.save()

        messages.add_message(
            request,
            constants.SUCCESS,
            f"Contrato assinado com sucesso, sua proposta foi enviada a empresa.",
        )
        return redirect(f"/investidores/ver_empresa/{pi.empresa.id}")
