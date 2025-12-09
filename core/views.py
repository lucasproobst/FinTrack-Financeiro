import datetime
from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Sum
from django import forms
from django.http import FileResponse
from django.contrib.auth import update_session_auth_hash
from django.db.models import Sum, Case, When, F

from .models import Conta, Lancamento, Categoria
from .forms import ContaForm, LancamentoForm, CategoriaForm
from .utils.relatorio_generator import gerar_relatorio_pdf, gerar_relatorio_excel
from babel.numbers import format_currency


# Página inicial
def home(request):
    return render(request, "core/home.html")


@login_required
def perfil_usuario(request):
    return render(request, "usuarios/perfil.html")


@login_required
def alterar_perfil(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        senha_atual = request.POST.get("senha_atual")
        nova_senha = request.POST.get("nova_senha")
        confirmar_senha = request.POST.get("confirmar_senha")

        user = request.user

        # Atualiza nome e e-mail
        user.first_name = nome
        user.email = email

        # Verifica se vai alterar a senha
        if senha_atual and nova_senha and confirmar_senha:
            if not user.check_password(senha_atual):
                messages.error(request, "Senha atual incorreta.")
            elif nova_senha != confirmar_senha:
                messages.error(request, "As novas senhas não coincidem.")
            else:
                user.set_password(nova_senha)
                update_session_auth_hash(request, user)  # Mantém login
                messages.success(request, "Senha alterada com sucesso.")

        user.save()
        return redirect("perfil_usuario")

    return render(request, "usuarios/alterar_perfil.html")


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        help_texts = {
            "username": "",
            "password1": "Sua senha deve conter pelo menos 8 caracteres e não pode ser comum.",
            "password2": "Repita a senha digitada acima.",
        }


# View de cadastro
def cadastro(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "core/cadastro.html", {"form": form})


# Dashboard
@login_required
def dashboard(request):
    usuario = request.user
    contas = Conta.objects.filter(usuario=usuario)
    lancamentos = Lancamento.objects.filter(usuario=usuario)

    total_receitas = (
        lancamentos.filter(tipo="Receita").aggregate(total=Sum("valor"))["total"] or 0
    )
    total_despesas = (
        lancamentos.filter(tipo="Despesa").aggregate(total=Sum("valor"))["total"] or 0
    )
    saldo_total = (
        sum([c.saldo_inicial for c in contas]) + total_receitas - total_despesas
    )

    ultimos_lancamentos = lancamentos.order_by("-data")[:5]

    saldos_por_conta = []
    for conta in contas:
        receitas = (
            lancamentos.filter(conta=conta, tipo="Receita").aggregate(Sum("valor"))[
                "valor__sum"
            ]
            or 0
        )
        despesas = (
            lancamentos.filter(conta=conta, tipo="Despesa").aggregate(Sum("valor"))[
                "valor__sum"
            ]
            or 0
        )
        saldo = conta.saldo_inicial + receitas - despesas
        saldos_por_conta.append(
            {
                "nome": conta.nome,
                "saldo": saldo,
                "receitas": receitas,
                "despesas": despesas,
            }
        )

    context = {
        "saldo_total": saldo_total,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "ultimos_lancamentos": ultimos_lancamentos,
        "saldos_por_conta": saldos_por_conta,
    }
    return render(request, "core/dashboard.html", context)


# -------------------- CONTAS --------------------


@login_required
def listar_contas(request):
    contas = Conta.objects.filter(usuario=request.user)

    for conta in contas:
        conta.saldo_formatado = (
            f"{conta.saldo_inicial:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    return render(request, "core/listar_contas.html", {"contas": contas})


@login_required
def criar_conta(request):
    if request.method == "POST":
        form = ContaForm(request.POST)
        if form.is_valid():
            conta = form.save(commit=False)
            conta.usuario = request.user
            conta.save()
            return redirect("listar_contas")
    else:
        form = ContaForm()
    return render(request, "core/form_conta.html", {"form": form})


@login_required
def editar_conta(request, conta_id):
    conta = get_object_or_404(Conta, id=conta_id, usuario=request.user)
    if request.method == "POST":
        form = ContaForm(request.POST, instance=conta)
        if form.is_valid():
            form.save()
            return redirect("listar_contas")
    else:
        form = ContaForm(instance=conta)
    return render(request, "core/form_conta.html", {"form": form})


@login_required
def excluir_conta(request, conta_id):
    conta = get_object_or_404(Conta, id=conta_id, usuario=request.user)
    if request.method == "POST":
        conta.delete()
        return redirect("listar_contas")
    return render(request, "core/confirmar_exclusao_conta.html", {"conta": conta})


# -------------------- LANÇAMENTOS --------------------


@login_required
def lancar_movimento(request):
    if request.method == "POST":
        form = LancamentoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            lancamento = form.save(commit=False)
            lancamento.usuario = request.user
            lancamento.save()
            return redirect("lancar")
    else:
        form = LancamentoForm(user=request.user)
    return render(request, "core/lancamento_form.html", {"form": form})


@login_required
def listar_lancamentos(request):
    lancamentos = Lancamento.objects.filter(usuario=request.user).order_by("-data")
    categorias = Categoria.objects.filter(usuario=request.user)

    data_inicio = request.GET.get("data_inicio", "")
    data_fim = request.GET.get("data_fim", "")
    categoria_id = request.GET.get("categoria", "todas")
    tipo = request.GET.get("tipo", "todos")

    if data_inicio:
        lancamentos = lancamentos.filter(data__gte=data_inicio)
    if data_fim:
        lancamentos = lancamentos.filter(data__lte=data_fim)
    if categoria_id != "todas":
        lancamentos = lancamentos.filter(categoria_id=categoria_id)
    if tipo != "todos":
        lancamentos = lancamentos.filter(tipo=tipo)


    for l in lancamentos:
        l.valor_formatado = (
            f"{l.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    return render(
        request,
        "core/lancamento_lista.html",
        {
            "lancamentos": lancamentos,
            "categorias": categorias,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "categoria_selecionada": categoria_id,
            "tipo_selecionado": tipo,
        },
    )


@login_required
def criar_lancamento(request):
    if request.method == "POST":
        form = LancamentoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            lancamento = form.save(commit=False)
            lancamento.usuario = request.user
            lancamento.tipo = lancamento.categoria.tipo
            lancamento.save()
            return redirect("listar_lancamentos")
    else:
        form = LancamentoForm(user=request.user)
    return render(request, "core/lancamento_form.html", {"form": form})


@login_required
def editar_lancamento(request, lancamento_id):
    lancamento = get_object_or_404(Lancamento, id=lancamento_id, usuario=request.user)
    if request.method == "POST":
        form = LancamentoForm(
            request.POST, request.FILES, instance=lancamento, user=request.user
        )
        if form.is_valid():
            form.save()
            return redirect("listar_lancamentos")
    else:
        form = LancamentoForm(instance=lancamento, user=request.user)
    return render(request, "core/lancamento_form.html", {"form": form, "edicao": True})


@login_required
def excluir_lancamento(request, pk):
    lancamento = get_object_or_404(Lancamento, pk=pk, usuario=request.user)
    if request.method == "POST":
        lancamento.delete()
        return redirect("listar_lancamentos")
    return render(
        request, "core/lancamento_confirm_delete.html", {"lancamento": lancamento}
    )


# -------------------- CATEGORIAS --------------------


@login_required
def listar_categorias(request):
    categorias = Categoria.objects.filter(usuario=request.user)
    return render(request, "core/listar_categorias.html", {"categorias": categorias})


@login_required
def cadastrar_categoria(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.usuario = request.user
            categoria.save()
            return redirect("listar_categorias")
    else:
        form = CategoriaForm()
    return render(request, "core/categoria_form.html", {"form": form})


@login_required
def editar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id, usuario=request.user)
    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect("listar_categorias")
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, "core/categoria_form.html", {"form": form})


@login_required
def excluir_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id, usuario=request.user)
    if request.method == "POST":
        categoria.delete()
        return redirect("listar_categorias")
    return render(
        request, "core/confirmar_exclusao_categoria.html", {"categoria": categoria}
    )


# -------------------- RELATÓRIOS --------------------
from django.db.models import Sum, Case, When, F
from babel.numbers import format_currency
import datetime


@login_required
def gerar_relatorio(request):
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")
    formato = request.GET.get("formato")

    if not data_inicio or not data_fim:
        messages.error(request, "Você deve selecionar o intervalo de datas.")
        return render(request, "core/relatorio_form.html")

    try:
        inicio = datetime.datetime.strptime(data_inicio, "%Y-%m-%d").date()
        fim = datetime.datetime.strptime(data_fim, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Datas inválidas.")
        return render(request, "core/relatorio_form.html")

    if inicio > fim:
        messages.error(
            request, "A data de início não pode ser maior que a data de fim."
        )
        return render(request, "core/relatorio_form.html")


    lancamentos = Lancamento.objects.filter(
        usuario=request.user, data__range=[inicio, fim]
    ).order_by("data")


    lancamentos_corrigidos = lancamentos.annotate(
        valor_corrigido=Case(
            When(tipo="Receita", then=F("valor")),
            When(tipo="Despesa", then=-F("valor")),
        )
    )

    # SALDO INICIAL
    saldo_inicial = (
        Lancamento.objects.filter(usuario=request.user, data__lt=inicio)
        .annotate(
            valor_corrigido=Case(
                When(tipo="Receita", then=F("valor")),
                When(tipo="Despesa", then=-F("valor")),
            )
        )
        .aggregate(total=Sum("valor_corrigido"))["total"]
        or 0
    )

    # TOTAL DE RECEITAS (somando APENAS valor_corrigido)
    receitas = (
        lancamentos_corrigidos.filter(tipo="Receita").aggregate(
            total=Sum("valor_corrigido")
        )["total"]
        or 0
    )

    # TOTAL DE DESPESAS (somando valor_corrigido NEGATIVO)
    despesas = (
        lancamentos_corrigidos.filter(tipo="Despesa").aggregate(
            total=Sum("valor_corrigido")
        )["total"]
        or 0
    )

    # SALDO FINAL
    saldo_final = saldo_inicial + receitas + despesas

    def fmt(v):
        return format_currency(v, "BRL", locale="pt_BR")

    context = {
        "usuario": request.user,
        "data_inicio": inicio.strftime("%d/%m/%Y"),
        "data_fim": fim.strftime("%d/%m/%Y"),
        "lancamentos": lancamentos,
        "saldo_inicial": saldo_inicial,
        "receitas": receitas,
        "despesas": abs(despesas),
        "saldo_final": saldo_final,
        "saldo_inicial_fmt": fmt(saldo_inicial),
        "receitas_fmt": fmt(receitas),
        "despesas_fmt": fmt(abs(despesas)),
        "saldo_final_fmt": fmt(saldo_final),
    }

    # PDFs e Excel
    if formato == "pdf":
        pdf_buffer = gerar_relatorio_pdf(context)
        return FileResponse(
            pdf_buffer, content_type="application/pdf", filename="relatorio.pdf"
        )

    if formato == "excel":
        excel_buffer = gerar_relatorio_excel(context)
        return FileResponse(
            excel_buffer,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="relatorio.xlsx",
        )

    return render(request, "core/relatorio_form.html")


# -------------------- FIM DOS RELATÓRIOS --------------------
