from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from cadastros.models import Cadastro
from financeiro.models import Lancamento, Conta

def home(request):
    """Tela Inicial (Landing Page)"""
    return render(request, 'web/home.html')

@login_required
def dashboard(request):
    """Painel Principal com Gráficos e Totais"""
    empresa = request.user.empresa
    hoje = timezone.now().date()

    # 1. DADOS DE CADASTROS
    total_cadastros = Cadastro.objects.filter(empresa=empresa).count()
    ativos = Cadastro.objects.filter(empresa=empresa, situacao='ATIVO').count()
    
    # 2. DADOS FINANCEIROS (Mês Atual)
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    # Soma das Receitas (Créditos)
    receita_mensal = Lancamento.objects.filter(
        empresa=empresa,
        tipo='C', 
        data_lancamento__month=mes_atual,
        data_lancamento__year=ano_atual
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    # Soma das Despesas (Débitos)
    # Lembra que no banco elas estão negativas?
    despesa_mensal = Lancamento.objects.filter(
        empresa=empresa,
        tipo='D', 
        data_lancamento__month=mes_atual,
        data_lancamento__year=ano_atual
    ).aggregate(Sum('valor'))['valor__sum'] or 0

    # 3. LISTAS RECENTES
    ultimos_pagamentos = Lancamento.objects.filter(
        empresa=empresa, 
        tipo='C'
    ).order_by('-data_lancamento')[:5]

    # 4. CONTAS ATRASADAS (Busca na tabela Conta, não no Lancamento)
    contas_atrasadas = Conta.objects.filter(
        empresa=empresa,
        plano_de_contas__tipo='R', # Busca contas a Receber (Receita)
        status='PENDENTE',
        data_vencimento__lt=hoje
    ).order_by('data_vencimento')[:5]

    context = {
        'total_cadastros': total_cadastros,
        'ativos': ativos,
        'receita_mensal': receita_mensal,
        
        # Enviamos 'abs' (valor absoluto) para o Card Vermelho não mostrar sinal de negativo
        # Ex: Mostra "R$ 500,00" no cartão de despesa em vez de "R$ -500,00"
        'despesa_mensal': abs(despesa_mensal), 
        
        'ultimos_pagamentos': ultimos_pagamentos,
        'contas_atrasadas': contas_atrasadas,
        
        # O saldo real é a soma (já que despesa é negativo no banco: 1000 + (-300) = 700)
        'saldo': receita_mensal + despesa_mensal 
    }
    
    return render(request, 'web/dashboard.html', context)