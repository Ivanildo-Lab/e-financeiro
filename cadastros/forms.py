from django import forms
from .models import Cadastro

class CadastroForm(forms.ModelForm):
    class Meta:
        model = Cadastro
        fields = '__all__'
        exclude = ['empresa', 'data_cadastro', 'situacao', 'num_contrato'] 

        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'data_admissao': forms.DateInput(attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # Captura o usuário passado pela View para sabermos a empresa dele
        self.user = kwargs.pop('user', None) 
        super(CadastroForm, self).__init__(*args, **kwargs)
        
        # Estilo Tailwind
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors'

    # --- VALIDAÇÃO CUSTOMIZADA ---
    def clean_num_registro(self):
        num_registro = self.cleaned_data['num_registro']
        
        # Se temos usuário e empresa identificados
        if self.user and self.user.empresa:
            # Verifica se já existe ALGUÉM com esse número NA MESMA empresa
            existe = Cadastro.objects.filter(
                empresa=self.user.empresa, 
                num_registro=num_registro
            ).exclude(pk=self.instance.pk).exists() # O exclude garante que na edição não dê erro com o próprio cadastro

            if existe:
                raise forms.ValidationError(f"O registro nº {num_registro} já pertence a outro cliente.")
        
        return num_registro