from django.shortcuts import render, redirect
from django.http import HttpResponse

# Importar a classe referente a tabela usuarios que já vem no Django
from django.contrib.auth.models import User

# Importar as constantes de mensagens do Django
from django.contrib import messages

# Importar os tipos de mensagens do Django
from django.contrib.messages import constants

# Importar o Auth
from django.contrib import auth


# Create your views here.
def cadastro(request):
    # print(f"Tipo de requisição: {request.method}")  # Imprime o tipo de requisição: GET, POST
    if request.method == "GET":  # Verifica se a requisição é do tipo GET
        return render(request, "cadastro.html")  # Renderiza um template HTML
    elif request.method == "POST":  # Verifica se a requisição é do tipo POST
        username = request.POST.get(
            "username"
        )  # Obtém o valor do campo username do formulário
        senha = request.POST.get("senha")  # Obtém o valor do campo senha do formulário
        confirmar_senha = request.POST.get(
            "confirmar_senha"
        )  # Obtém o valor do campo confirmar_senha do formulário

        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, "As senhas não coincidem")
            return redirect("/usuarios/cadastro")

        if len(senha) < 6:
            messages.add_message(
                request, constants.ERROR, "A senha precisa ter pelo menos 6 digitos"
            )
            return redirect("/usuarios/cadastro")

        users = User.objects.filter(username=username)

        # print(users.exists())

        if users.exists():
            messages.add_message(
                request, constants.ERROR, "Já existe um usuário com esse username"
            )
            return redirect("/usuarios/cadastro")

        user = User.objects.create_user(username=username, password=senha)

        return redirect("/usuarios/logar")


def logar(request):

    if request.method == "GET":
        return render(request, "logar.html")
    elif request.method == "POST":
        username = request.POST.get("username")
        senha = request.POST.get("senha")

        user = auth.authenticate(request, username=username, password=senha)

        if user:
            auth.login(
                request, user
            )  # Verifica o usuário atrelado ao ip e o login (Sessão?)
            return redirect("/empresarios/cadastrar_empresa")
        messages.add_message(request, constants.ERROR, "Usuário ou senha inválidos")
        return redirect("/usuarios/logar")

        # if user.check_password(senha):
        #     return redirect("/usuarios/logado")
        # else:
        #     messages.add_message(request, constants.ERROR, "Senha incorreta")
        #     return redirect("/usuarios/logar")
