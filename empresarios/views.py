from django.shortcuts import render, redirect

# Importar os selects do models
from .models import Empresas, Documento, Metricas
from investidores.models import PropostaInvestimento

# Importar as constantes de mensagens do Django
from django.contrib import messages

# Importar os tipos de mensagens do Django
from django.contrib.messages import constants
from django.db.models import Sum
from django.db.models import Sum
from django.db.models import Sum


# Create your views here.
def cadastrar_empresa(request):

    if not request.user.is_authenticated:
        return redirect("/usuarios/logar")

    if request.method == "GET":
        # print(Empresas.tempo_existencia_choices)
        return render(
            request,
            "cadastrar_empresa.html",
            {
                "tempo_existencia": Empresas.tempo_existencia_choices,
                "areas": Empresas.area_choices,
            },
        )
    elif request.method == "POST":

        # ToDo: Realizar validação de campos

        nome = request.POST.get("nome")
        cnpj = request.POST.get("cnpj")
        site = request.POST.get("site")
        tempo_existencia = request.POST.get("tempo_existencia")
        descricao = request.POST.get("descricao")
        data_final = request.POST.get("data_final")
        percentual_equity = request.POST.get("percentual_equity")
        estagio = request.POST.get("estagio")
        area = request.POST.get("area")
        publico_alvo = request.POST.get("publico_alvo")
        valor = request.POST.get("valor")
        pitch = request.FILES.get("pitch")
        logo = request.FILES.get("logo")

        try:
            empresa = Empresas(
                user=request.user,
                nome=nome,
                cnpj=cnpj,
                site=site,
                tempo_existencia=tempo_existencia,
                descricao=descricao,
                data_final_captacao=data_final,
                percentual_equity=percentual_equity,
                estagio=estagio,
                area=area,
                publico_alvo=publico_alvo,
                valor=valor,
                pitch=pitch,
                logo=logo,
            )
            empresa.save()
        except:
            messages.add_message(request, constants.ERROR, "Erro interno do sistema")
            return redirect("/empresarios/cadastrar_empresa")

        messages.add_message(request, constants.SUCCESS, "Empresa criada com sucesso")
        return redirect("/empresarios/cadastrar_empresa")


def listar_empresas(request):

    if not request.user.is_authenticated:
        return redirect("/usuarios/logar")

    if request.method == "GET":

        # ToDo: Realizar os filtros das empresas

        empresas = Empresas.objects.filter(user=request.user)
        return render(request, "listar_empresas.html", {"empresas": empresas})


# Além do request, tem que receber o id, que estará no link da página anterior (via GET)
def empresa(request, id):

    if not request.user.is_authenticated:
        return redirect("/usuarios/logar")

    empresa = Empresas.objects.get(id=id)

    if empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Essa empresa não é sua")
        return redirect("/empresarios/listar_empresas")

    if request.method == "GET":
        documentos = Documento.objects.filter(empresa=empresa)

        proposta_investimentos = PropostaInvestimento.objects.filter(empresa=empresa)

        # Obtém o percentual (soma) de todas aceitas (PA - Propostas Aceitas)
        percentual_vendido = 0
        # Maneira 1 -  a mais "péba" de todas
        # total_captado = 0
        for pi in proposta_investimentos:
            if pi.status == "PA":
                percentual_vendido = percentual_vendido + pi.percentual
                # pi.valor = valor que foi investido
                # total_captado = total_captado + pi.valor

        # Maneira 2 para obter o total captado - mais otimizada
        # total_captado = sum(
        #     proposta_investimentos.filter(status="PA").values_list("valor", flat=True)
        # )

        # Maneira 3 para obter o total captado - mais otimizada
        total_captado = proposta_investimentos.filter(status="PA").aggregate(
            Sum("valor")
        )["valor__sum"]

        # Para trocar com vírgulas ao invés de ponto na casa decimal
        valuation_atual = (
            f"{(100 * float(total_captado)) / float(percentual_vendido):.2f}".replace(
                ".", ","
            )
            if percentual_vendido != 0
            else "0,00"
        )

        proposta_investimentos_enviada = proposta_investimentos.filter(status="PE")

        return render(
            request,
            "empresa.html",
            {
                "empresa": empresa,
                "documentos": documentos,
                "proposta_investimentos_enviada": proposta_investimentos_enviada,
                "percentual_vendido": int(percentual_vendido),
                "total_captado": total_captado,
                "valuation_atual": valuation_atual,
            },
        )


def add_doc(request, id):

    if not request.user.is_authenticated:
        return redirect("/usuarios/logar")

    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get("titulo")
    arquivo = request.FILES.get("arquivo")
    extensao = arquivo.name.split(".")

    if empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Essa empresa não é sua")
        return redirect("/empresarios/listar_empresas")

    if extensao[1] != "pdf":
        messages.add_message(request, constants.ERROR, "Envie apenas PDF's")
        return redirect(f"/empresarios/empresa/{empresa.id}")

    if not arquivo:
        messages.add_message(request, constants.ERROR, "Envie um arquivo")
        return redirect(f"/empresarios/empresa/{empresa.id}")

    documento = Documento(empresa=empresa, titulo=titulo, arquivo=arquivo)
    documento.save()
    messages.add_message(request, constants.SUCCESS, "Arquivo cadastrado com sucesso")
    return redirect(f"/empresarios/empresa/{empresa.id}")


def excluir_dc(request, id):

    if not request.user.is_authenticated:
        return redirect("/usuarios/logar")

    documento = Documento.objects.get(id=id)

    if documento.empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Esse documento não é seu")
        return redirect(f"/empresarios/empresa/{documento.empresa.id}")

    documento.delete()
    messages.add_message(request, constants.SUCCESS, "Documento excluído com sucesso")
    return redirect(f"/empresarios/empresa/{documento.empresa.id}")


def add_metrica(request, id):

    if not request.user.is_authenticated:
        return redirect("/usuarios/logar")

    empresa = Empresas.objects.get(
        id=id
    )  # Pega todos os dados da empresa usando a classe Empresas do models
    titulo = request.POST.get("titulo")
    valor = request.POST.get("valor")

    metrica = Metricas(empresa=empresa, titulo=titulo, valor=valor)
    metrica.save()

    messages.add_message(request, constants.SUCCESS, "Métrica cadastrada com sucesso")
    return redirect(f"/empresarios/empresa/{empresa.id}")


def gerenciar_proposta(request, id):

    if not request.user.is_authenticated:
        return redirect("/usuarios/logar")

    acao = request.GET.get("acao")
    pi = PropostaInvestimento.objects.get(id=id)

    if acao == "aceitar":
        messages.add_message(request, constants.SUCCESS, "Proposta aceita")
        pi.status = "PA"
    elif acao == "recusar":
        messages.add_message(request, constants.WARNING, "Proposta recusada")
        pi.status = "PR"

    # Repare que não não é update, é o mesmo save()
    pi.save()
    return redirect(f"/empresarios/empresa/{pi.empresa.id}")
