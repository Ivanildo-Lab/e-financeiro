from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cadastro
from .forms import CadastroForm

@login_required
def lista_cadastros(request):
    # 1. Base Query (Só pega dados da empresa do usuário)
    qs = Cadastro.objects.filter(empresa=request.user.empresa)

    # 2. Filtros de Busca (Se o usuário digitou algo)
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        qs = qs.filter(
            Q(nome__icontains=search_query) | 
            Q(cpf__icontains=search_query) | 
            Q(num_registro__icontains=search_query)
        )
    
    if status_filter:
        qs = qs.filter(situacao=status_filter)

    # 3. Dados para os Cards do Topo (Estatísticas)
    context = {
        'cadastros': qs, # A lista filtrada
        'total_cadastros': Cadastro.objects.filter(empresa=request.user.empresa).count(),
        'ativos': Cadastro.objects.filter(empresa=request.user.empresa, situacao='ATIVO').count(),
        'inativos': Cadastro.objects.filter(empresa=request.user.empresa, situacao='INATIVO').count(),
        'pendentes': Cadastro.objects.filter(empresa=request.user.empresa, situacao='PENDENTE').count(),
        
        # Mantendo os valores do filtro para preencher o input
        'search_query': search_query,
        'status_selecionado': status_filter,
    }
    
    return render(request, 'cadastros/lista.html', context)

@login_required
def novo_cadastro(request):
    if request.method == 'POST':
        # Passamos user=request.user aqui
        form = CadastroForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            cadastro = form.save(commit=False)
            cadastro.empresa = request.user.empresa
            cadastro.save()
            return redirect('lista_cadastros')
    else:
        # E aqui também
        form = CadastroForm(user=request.user)

    return render(request, 'cadastros/formulario.html', {'form': form})

@login_required
def editar_cadastro(request, id):
    cadastro = get_object_or_404(Cadastro, id=id, empresa=request.user.empresa)
    
    if request.method == 'POST':
        # Passamos user=request.user aqui
        form = CadastroForm(request.POST, request.FILES, instance=cadastro, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('lista_cadastros')
    else:
        # E aqui também
        form = CadastroForm(instance=cadastro, user=request.user)
        
    return render(request, 'cadastros/formulario.html', {'form': form})