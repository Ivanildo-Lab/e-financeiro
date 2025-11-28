from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils.dateparse import parse_date

# Imports dos Modelos e Formulários
from .models import Conta, Lancamento, Caixa, PlanoDeContas
from .forms import ContaForm, LancamentoManualForm, CaixaForm, PlanoContasForm
from core.models import ParametroSistema
from decimal import Decimal
import calendar
import random


def add_months(source_date, months):
    """Adiciona meses a uma data corretamente (ex: 31/01 + 1 mês -> 28/02)"""
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

# ==========================================================
# 1. GESTÃO DE CAIXAS (BANCOS)
# ==========================================================
@login_required
def lista_caixas(request):
    caixas = Caixa.objects.filter(empresa=request.user.empresa)
    return render(request, 'financeiro/caixa_list.html', {'caixas': caixas})

@login_required
def adicionar_caixa(request):
    if request.method == 'POST':
        form = CaixaForm(request.POST)
        if form.is_valid():
            caixa = form.save(commit=False)
            caixa.empresa = request.user.empresa
            caixa.save()
            messages.success(request, "Caixa adicionado com sucesso!")
            return redirect('financeiro:lista_caixas')
    else:
        form = CaixaForm()
    return render(request, 'financeiro/caixa_form.html', {'form': form})

@login_required
def editar_caixa(request, id):
    caixa = get_object_or_404(Caixa, id=id, empresa=request.user.empresa)
    if request.method == 'POST':
        form = CaixaForm(request.POST, instance=caixa)
        if form.is_valid():
            form.save()
            messages.success(request, "Caixa atualizado!")
            return redirect('financeiro:lista_caixas')
    else:
        form = CaixaForm(instance=caixa)
    return render(request, 'financeiro/caixa_form.html', {'form': form})

@login_required
def excluir_caixa(request, id):
    caixa = get_object_or_404(Caixa, id=id, empresa=request.user.empresa)
    if caixa.lancamento_set.exists():
        messages.error(request, "Não é possível excluir este caixa pois existem lançamentos vinculados.")
    else:
        caixa.delete()
        messages.success(request, "Caixa excluído com sucesso.")
    return redirect('financeiro:lista_caixas')


# ==========================================================
# 2. GESTÃO DE PLANO DE CONTAS
# ==========================================================
@login_required
def lista_plano_de_contas(request):
    contas = PlanoDeContas.objects.filter(empresa=request.user.empresa).order_by('codigo')
    return render(request, 'financeiro/plano_de_contas_list.html', {'planos_de_contas': contas})

# financeiro/views.py

@login_required
def adicionar_plano_de_contas(request):
    if request.method == 'POST':
        # PASSANDO O USER AQUI
        form = PlanoContasForm(request.POST, user=request.user)
        if form.is_valid():
            conta = form.save(commit=False)
            conta.empresa = request.user.empresa
            conta.save()
            messages.success(request, "Categoria criada com sucesso!")
            return redirect('financeiro:lista_plano_de_contas')
    else:
        # E AQUI TAMBÉM
        form = PlanoContasForm(user=request.user)
    return render(request, 'financeiro/plano_de_contas_form.html', {'form': form})

@login_required
def editar_plano_de_contas(request, id):
    conta = get_object_or_404(PlanoDeContas, id=id, empresa=request.user.empresa)
    if request.method == 'POST':
        # PASSANDO O USER NA EDIÇÃO TAMBÉM
        form = PlanoContasForm(request.POST, instance=conta, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoria atualizada!")
            return redirect('financeiro:lista_plano_de_contas')
    else:
        # E AQUI
        form = PlanoContasForm(instance=conta, user=request.user)
    return render(request, 'financeiro/plano_de_contas_form.html', {'form': form})

@login_required
def excluir_plano_de_contas(request, id):
    conta = get_object_or_404(PlanoDeContas, id=id, empresa=request.user.empresa)
    if conta.lancamento_set.exists() or conta.conta_set.exists():
        messages.error(request, "Não é possível excluir: existem lançamentos ou contas usando esta categoria.")
    else:
        conta.delete()
        messages.success(request, "Categoria excluída.")
    return redirect('financeiro:lista_plano_de_contas')


# ==========================================================
# 3. CONTAS A PAGAR E RECEBER (SEPARADAS COM FILTROS)
# ==========================================================

@login_required
def lista_contas_receber(request):
    contas = Conta.objects.filter(empresa=request.user.empresa, plano_de_contas__tipo='R')

    # --- FILTROS ---
    data_ini = request.GET.get('data_ini')
    data_fim = request.GET.get('data_fim')
    cliente_nome = request.GET.get('cliente')
    status = request.GET.get('status') # Novo filtro

    if data_ini and data_fim:
        contas = contas.filter(data_vencimento__range=[data_ini, data_fim])
    
    if cliente_nome:
        contas = contas.filter(cadastro__nome__icontains=cliente_nome)

    if status: # Lógica do Status
        if status == 'ATRASADA':
            # Atrasada é Pendente + Vencimento menor que hoje
            contas = contas.filter(status='PENDENTE', data_vencimento__lt=date.today())
        else:
            contas = contas.filter(status=status)

    caixas = Caixa.objects.filter(empresa=request.user.empresa)
    
    return render(request, 'financeiro/contas_lista.html', {
        'contas': contas.order_by('data_vencimento'), 
        'caixas': caixas,
        'titulo': 'Contas a Receber',
        'tipo_lista': 'receber',
        # Passa os filtros de volta para o template manter preenchido
        'filtro_data_ini': data_ini,
        'filtro_data_fim': data_fim,
        'filtro_nome': cliente_nome,
        'filtro_status': status 
    })

@login_required
def lista_contas_pagar(request):
    contas = Conta.objects.filter(empresa=request.user.empresa, plano_de_contas__tipo='D')

    # --- FILTROS ---
    data_ini = request.GET.get('data_ini')
    data_fim = request.GET.get('data_fim')
    fornecedor_nome = request.GET.get('cliente')
    status = request.GET.get('status')

    if data_ini and data_fim:
        contas = contas.filter(data_vencimento__range=[data_ini, data_fim])
    
    if fornecedor_nome:
        contas = contas.filter(cadastro__nome__icontains=fornecedor_nome)

    if status:
        if status == 'ATRASADA':
            contas = contas.filter(status='PENDENTE', data_vencimento__lt=date.today())
        else:
            contas = contas.filter(status=status)

    caixas = Caixa.objects.filter(empresa=request.user.empresa)
    
    return render(request, 'financeiro/contas_lista.html', {
        'contas': contas.order_by('data_vencimento'), 
        'caixas': caixas,
        'titulo': 'Contas a Pagar',
        'tipo_lista': 'pagar',
        'filtro_data_ini': data_ini,
        'filtro_data_fim': data_fim,
        'filtro_nome': fornecedor_nome,
        'filtro_status': status
    })

# ==========================================================
# FUNÇÃO AUXILIAR PARA CRIAR CONTAS (EVITA REPETIÇÃO DE CÓDIGO)
# ==========================================================
def processar_lancamento_conta(request, form, tipo_redirect):
    """Lógica comum para salvar Receita ou Despesa com parcelamento"""
    dados = form.cleaned_data
    
    # Dados base
    descricao_original = dados['descricao']
    valor_original = dados['valor']
    vencimento_inicial = dados['data_vencimento']
    gerar_parcelas = dados.get('gerar_parcelas')
    
    if gerar_parcelas:
        qtd = dados['qtd_parcelas']
        juros = dados.get('taxa_juros') or Decimal(0)
        
        acrescimo = valor_original * (juros / Decimal(100))
        valor_total = valor_original + acrescimo
        valor_parcela = valor_total / qtd
        
        # Gera um número aleatório de 4 dígitos para agrupar as parcelas (Ex: 1234)
        grupo_parcela = random.randint(1000, 9999) 
        
        # Cria as parcelas
        for i in range(qtd):
            nova_conta = form.save(commit=False)
            nova_conta.pk = None
            nova_conta.empresa = request.user.empresa
            
            # Formata: Descrição (Parcela X/Y)
            nova_conta.descricao = f"{descricao_original}"
            
            # Formata: 1234-1/3
            nova_conta.documento = f"{grupo_parcela}-{i+1}/{qtd}"
            
            nova_conta.valor = valor_parcela
            nova_conta.data_vencimento = add_months(vencimento_inicial, i)
            
            nova_conta.save()
            
        messages.success(request, f"{qtd} parcelas geradas com sucesso! (Doc: {grupo_parcela})")
    else:
        # Salva normal
        conta = form.save(commit=False)
        conta.empresa = request.user.empresa
        
        # Se não parcelou, gera um documento único se quiser, ou deixa vazio
        conta.documento = str(random.randint(10000, 99999))
        
        conta.save()
        messages.success(request, "Lançamento salvo com sucesso!")

    return redirect(tipo_redirect)

# ==========================================================
# VIEWS ATUALIZADAS
# ==========================================================

@login_required
def nova_receita(request):
    """Cria conta pré-filtrando categorias de Receita e Clientes"""
    if request.method == 'POST':
        form = ContaForm(request.POST, user=request.user, tipo_filtro='R')
        if form.is_valid():
            return processar_lancamento_conta(request, form, 'financeiro:lista_receber')
    else:
        form = ContaForm(user=request.user, tipo_filtro='R')
    return render(request, 'financeiro/conta_form.html', {'form': form, 'titulo': 'Novo Recebimento'})

@login_required
def nova_despesa(request):
    """Cria conta pré-filtrando categorias de Despesa e Fornecedores"""
    if request.method == 'POST':
        form = ContaForm(request.POST, user=request.user, tipo_filtro='D')
        if form.is_valid():
            return processar_lancamento_conta(request, form, 'financeiro:lista_pagar')
    else:
        form = ContaForm(user=request.user, tipo_filtro='D')
    return render(request, 'financeiro/conta_form.html', {'form': form, 'titulo': 'Nova Despesa'})

@login_required
def editar_conta(request, id):
    conta = get_object_or_404(Conta, id=id, empresa=request.user.empresa)
    
    # Define o tipo para filtrar corretamente o form na edição
    tipo_filtro = conta.plano_de_contas.tipo 

    if request.method == 'POST':
        form = ContaForm(request.POST, instance=conta, user=request.user, tipo_filtro=tipo_filtro)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta atualizada.")
            return redirect('financeiro:lista_receber' if tipo_filtro == 'R' else 'financeiro:lista_pagar')
    else:
        form = ContaForm(instance=conta, user=request.user, tipo_filtro=tipo_filtro)
    return render(request, 'financeiro/conta_form.html', {'form': form})

@login_required
def excluir_conta(request, id):
    conta = get_object_or_404(Conta, id=id, empresa=request.user.empresa)
    tipo_redirect = 'financeiro:lista_receber' if conta.plano_de_contas.tipo == 'R' else 'financeiro:lista_pagar'
    
    if conta.status == 'PAGA':
        messages.error(request, "Não é possível excluir uma conta já paga. Estorne o lançamento primeiro.")
    else:
        conta.delete()
        messages.success(request, "Conta excluída.")
    
    return redirect(tipo_redirect)

@login_required
def baixar_conta(request, id):
    conta = get_object_or_404(Conta, id=id, empresa=request.user.empresa)
    
    if request.method == 'POST':
        caixa_id = request.POST.get('caixa')
        data_pagamento = request.POST.get('data_pagamento')
        
        if not caixa_id or not data_pagamento:
            messages.error(request, "Preencha todos os campos da baixa.")
            return redirect('financeiro:lista_receber' if conta.plano_de_contas.tipo == 'R' else 'financeiro:lista_pagar')

        caixa = get_object_or_404(Caixa, id=caixa_id, empresa=request.user.empresa)

        # Mapeia o tipo do Plano (R/D) para o tipo do Lançamento (C/D)
        # R (Receita) -> C (Crédito)
        # D (Despesa) -> D (Débito)
        tipo_lancamento = 'C' if conta.plano_de_contas.tipo == 'R' else 'D'

        Lancamento.objects.create(
            empresa=request.user.empresa,
            caixa=caixa,
            plano_de_contas=conta.plano_de_contas,
            conta_origem=conta,
            descricao=f"Baixa: {conta.descricao}",
            data_lancamento=data_pagamento,
            valor=conta.valor,
            tipo=tipo_lancamento
        )

        conta.status = 'PAGA'
        conta.save()
        
        messages.success(request, "Baixa realizada com sucesso!")
        
        if conta.plano_de_contas.tipo == 'R':
            return redirect('financeiro:lista_receber')
        else:
            return redirect('financeiro:lista_pagar')
    
    return redirect('financeiro:lista_receber')


# ==========================================================
# 4. FLUXO DE CAIXA E RELATÓRIOS
# ==========================================================

@login_required
def fluxo_caixa(request):
    # 1. Definição das Datas
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    
    data_inicio = request.GET.get('data_inicio', inicio_mes.strftime('%Y-%m-%d'))
    data_fim = request.GET.get('data_fim', hoje.strftime('%Y-%m-%d'))

    # 2. Definição do Caixa
    caixa_id = request.GET.get('caixa')
    
    # Se não veio filtro, busca o padrão no ParametroSistema
    if not caixa_id:
        try:
            param = ParametroSistema.objects.get(empresa=request.user.empresa, chave='CAIXA_PADRAO_ID')
            caixa_id = param.valor
        except (ParametroSistema.DoesNotExist, ValueError):
            caixa_id = None

    # 3. Query Base
    lancamentos = Lancamento.objects.filter(
        empresa=request.user.empresa,
        data_lancamento__range=[data_inicio, data_fim]
    )

    if caixa_id:
        lancamentos = lancamentos.filter(caixa_id=caixa_id)

    lancamentos = lancamentos.order_by('-data_lancamento')
    
    # 4. Cálculo de Saldo Anterior (apenas se tiver caixa definido)
    saldo_anterior = 0
    if caixa_id:
        # Soma todas as entradas anteriores à data_inicio
        entradas_ant = Lancamento.objects.filter(
            empresa=request.user.empresa, caixa_id=caixa_id, data_lancamento__lt=data_inicio, tipo='C'
        ).aggregate(Sum('valor'))['valor__sum'] or 0
        
        # Soma todas as saídas (já negativas) anteriores
        saidas_ant = Lancamento.objects.filter(
            empresa=request.user.empresa, caixa_id=caixa_id, data_lancamento__lt=data_inicio, tipo='D'
        ).aggregate(Sum('valor'))['valor__sum'] or 0
        
        # Saldo Inicial do cadastro
        try:
            saldo_inicial_cadastro = Caixa.objects.get(id=caixa_id, empresa=request.user.empresa).saldo_inicial
        except Caixa.DoesNotExist:
            saldo_inicial_cadastro = 0
        
        saldo_anterior = saldo_inicial_cadastro + entradas_ant + saidas_ant

    # 5. Totais do Período Atual
    total_periodo = lancamentos.aggregate(Sum('valor'))['valor__sum'] or 0
    saldo_final = saldo_anterior + total_periodo

    caixas = Caixa.objects.filter(empresa=request.user.empresa)

    return render(request, 'financeiro/fluxo_lista.html', {
        'lancamentos': lancamentos, 
        'saldo_anterior': saldo_anterior,
        'saldo_final': saldo_final,
        'caixas': caixas,
        'caixa_selecionado_id': str(caixa_id) if caixa_id else '',
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    })

@login_required
def novo_lancamento_manual(request):
    if request.method == 'POST':
        form = LancamentoManualForm(request.POST, user=request.user)
        if form.is_valid():
            lancamento = form.save(commit=False)
            lancamento.empresa = request.user.empresa
            lancamento.save()
            messages.success(request, "Lançamento registrado!")
            return redirect('financeiro:fluxo_caixa')
    else:
        form = LancamentoManualForm(user=request.user)
    return render(request, 'financeiro/lancamento_form.html', {'form': form})

@login_required
def editar_lancamento(request, id):
    lancamento = get_object_or_404(Lancamento, id=id, empresa=request.user.empresa)
    if request.method == 'POST':
        form = LancamentoManualForm(request.POST, instance=lancamento, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Lançamento atualizado!")
            return redirect('financeiro:fluxo_caixa')
    else:
        form = LancamentoManualForm(instance=lancamento, user=request.user)
    return render(request, 'financeiro/lancamento_form.html', {'form': form})

@login_required
def excluir_lancamento(request, id):
    lancamento = get_object_or_404(Lancamento, id=id, empresa=request.user.empresa)
    
    # Se for baixa de conta, retorna a conta para PENDENTE
    if lancamento.conta_origem:
        conta = lancamento.conta_origem
        conta.status = 'PENDENTE'
        conta.save()
        aviso_extra = " A conta original voltou para 'Pendente'."
    else:
        aviso_extra = ""

    lancamento.delete()
    messages.success(request, f"Lançamento excluído.{aviso_extra}")
    return redirect('financeiro:fluxo_caixa')

@login_required
def relatorio_fluxo(request):
    # 1. Filtros de Data
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    
    data_inicio_str = request.GET.get('data_inicio') or inicio_mes.strftime('%Y-%m-%d')
    data_fim_str = request.GET.get('data_fim') or hoje.strftime('%Y-%m-%d')
    
    data_inicio_obj = parse_date(data_inicio_str)
    data_fim_obj = parse_date(data_fim_str)

    # 2. Filtro de Caixa e Busca do Padrão
    caixa_id = request.GET.get('caixa')
    caixa_selecionado = None

    if caixa_id:
        caixa_selecionado = Caixa.objects.filter(id=caixa_id, empresa=request.user.empresa).first()
    else:
        try:
            param = ParametroSistema.objects.get(empresa=request.user.empresa, chave='CAIXA_PADRAO_ID')
            caixa_id = param.valor
            caixa_selecionado = Caixa.objects.filter(id=caixa_id, empresa=request.user.empresa).first()
        except (ParametroSistema.DoesNotExist, ValueError):
            caixa_selecionado = None
            caixa_id = None

    # 3. Busca
    lancamentos = Lancamento.objects.filter(
        empresa=request.user.empresa,
        data_lancamento__range=[data_inicio_str, data_fim_str]
    )

    if caixa_id:
        lancamentos = lancamentos.filter(caixa_id=caixa_id)

    receitas = lancamentos.filter(tipo='C').order_by('data_lancamento')
    despesas = lancamentos.filter(tipo='D').order_by('data_lancamento')

    total_receitas = receitas.aggregate(Sum('valor'))['valor__sum'] or 0
    total_despesas = despesas.aggregate(Sum('valor'))['valor__sum'] or 0
    resultado = total_receitas + total_despesas

    return render(request, 'financeiro/relatorio_impresso.html', {
        'data_inicio': data_inicio_obj,
        'data_fim': data_fim_obj,
        'caixa_selecionado': caixa_selecionado,
        'receitas': receitas,
        'despesas': despesas,
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'resultado': resultado,
        'empresa': request.user.empresa,
    })

@login_required
def relatorio_contas(request):
    """
    Gera relatório de Contas a Pagar ou Receber baseado nos filtros da URL
    """
    tipo_lista = request.GET.get('tipo_lista', 'receber')
    tipo_plano = 'R' if tipo_lista == 'receber' else 'D'
    
    # Base Query
    contas = Conta.objects.filter(empresa=request.user.empresa, plano_de_contas__tipo=tipo_plano)

    # --- REAPLICA OS MESMOS FILTROS DA LISTA (COM PROTEÇÃO) ---
    
    # Helper para limpar strings 'None' ou vazias
    def clean_val(val):
        return val if val and val != 'None' else None

    data_ini = clean_val(request.GET.get('data_ini'))
    data_fim = clean_val(request.GET.get('data_fim'))
    nome = clean_val(request.GET.get('cliente'))
    status = clean_val(request.GET.get('status'))

    # 1. Filtro de Data (Só aplica se tiver AS DUAS datas válidas)
    if data_ini and data_fim:
        contas = contas.filter(data_vencimento__range=[data_ini, data_fim])
    
    # 2. Filtro de Nome
    if nome:
        contas = contas.filter(cadastro__nome__icontains=nome)

    # 3. Filtro de Status
    if status:
        if status == 'ATRASADA':
            contas = contas.filter(status='PENDENTE', data_vencimento__lt=date.today())
        else:
            contas = contas.filter(status=status)

    contas = contas.order_by('data_vencimento')

    # Totais
    total_valor = contas.aggregate(Sum('valor'))['valor__sum'] or 0
    
    titulo_relatorio = "Relatório de Contas a Receber" if tipo_lista == 'receber' else "Relatório de Contas a Pagar"

    return render(request, 'financeiro/relatorio_contas_impresso.html', {
        'contas': contas,
        'total_valor': total_valor,
        'titulo_relatorio': titulo_relatorio,
        'empresa': request.user.empresa,
        # Envia objetos de data para o template formatar, ou None
        'data_ini': parse_date(data_ini) if data_ini else None,
        'data_fim': parse_date(data_fim) if data_fim else None,
        'status_filtro': status
    })
