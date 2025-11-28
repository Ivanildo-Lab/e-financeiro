from django import forms
from .models import Cadastro, CategoriaCliente

class CadastroForm(forms.ModelForm):
    class Meta:
        model = Cadastro
        fields = '__all__'
        exclude = ['empresa', 'papel', 'situacao', 'data_cadastro'] 

        widgets = {
            'data_nascimento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            # IDs para controle via Javascript
            'tipo_pessoa': forms.Select(attrs={'id': 'id_tipo_pessoa'}),
            'is_produtor_rural': forms.CheckboxInput(attrs={'id': 'id_is_produtor_rural'}),
            'cpf_cnpj': forms.TextInput(attrs={'id': 'id_cpf_cnpj'}),
        }

    def __init__(self, *args, **kwargs):
        # Captura variaveis extras passadas pela View
        self.user = kwargs.pop('user', None)
        self.papel = kwargs.pop('papel', None) 
        
        super(CadastroForm, self).__init__(*args, **kwargs)
        
        # 1. Lógica de Fornecedor (Remove Categoria)
        if self.papel == 'FOR':
            if 'categoria' in self.fields:
                del self.fields['categoria']

        # 2. Estilização (Tailwind)
        for field_name, field in self.fields.items():
            if field_name == 'is_produtor_rural':
                field.widget.attrs['class'] = 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            else:
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors'

        # 3. Filtro de Categoria (SaaS)
        if self.user and 'categoria' in self.fields:
            self.fields['categoria'].queryset = CategoriaCliente.objects.filter(empresa=self.user.empresa)

    # --- VALIDAÇÃO DE CPF/CNPJ DUPLICADO ---
    def clean_cpf_cnpj(self):
        cpf_cnpj = self.cleaned_data.get('cpf_cnpj')
        
        if self.user and cpf_cnpj:
            # Verifica se já existe alguém com este documento NA MESMA EMPRESA
            # O exclude(id=self.instance.id) garante que a edição do próprio registro não dê erro
            existe = Cadastro.objects.filter(
                empresa=self.user.empresa,
                cpf_cnpj=cpf_cnpj
            ).exclude(id=self.instance.id).exists()

            if existe:
                raise forms.ValidationError("Este CPF ou CNPJ já está cadastrado.")
        
        return cpf_cnpj

    # --- VALIDAÇÃO DE REGISTRO (Opcional, mas recomendado) ---
    def clean_num_registro(self):
        num = self.cleaned_data.get('num_registro')
        if self.user and num:
            existe = Cadastro.objects.filter(
                empresa=self.user.empresa,
                num_registro=num
            ).exclude(id=self.instance.id).exists()
            
            if existe:
                raise forms.ValidationError("Este Nº de Registro já existe.")
        return num