from django.shortcuts import render

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from cadastros.models import Cadastro
from financeiro.models import Lancamento

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
    inadimplentes_count = 0 # Implementaremos logica real depois
    
    # 2. DADOS FINANCEIROS (Mês Atual)
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    receita_mensal = Lancamento.objects.filter(
        empresa=empresa,
        tipo='R', # Receita
        data_pagamento__month=mes_atual,
        data_pagamento__year=ano_atual
    ).aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0

    despesa_mensal = Lancamento.objects.filter(
        empresa=empresa,
        tipo='D', # Despesa
        data_pagamento__month=mes_atual,
        data_pagamento__year=ano_atual
    ).aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0

    # 3. LISTAS RECENTES
    ultimos_pagamentos = Lancamento.objects.filter(
        empresa=empresa, 
        tipo='R', 
        status='PAGO'
    ).order_by('-data_pagamento')[:5]

    contas_atrasadas = Lancamento.objects.filter(
        empresa=empresa,
        tipo='R',
        status='PENDENTE',
        data_vencimento__lt=hoje
    ).order_by('data_vencimento')[:5]

    context = {
        'total_cadastros': total_cadastros,
        'ativos': ativos,
        'receita_mensal': receita_mensal,
        'despesa_mensal': despesa_mensal,
        'ultimos_pagamentos': ultimos_pagamentos,
        'contas_atrasadas': contas_atrasadas,
        'saldo': receita_mensal - despesa_mensal
    }
    
    return render(request, 'web/dashboard.html', context)
