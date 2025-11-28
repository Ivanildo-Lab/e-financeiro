from django import forms
from .models import ParametroSistema

class ParametroForm(forms.ModelForm):
    class Meta:
        model = ParametroSistema
        fields = ['valor', 'descricao'] # Não deixamos mudar a CHAVE, só o valor
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'