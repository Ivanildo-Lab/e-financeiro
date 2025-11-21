from django.db import models
from core.models import ModeloSaaS  # Importamos a lógica Multiempresa

class Cadastro(ModeloSaaS):
    """
    Tabela de Cadastros .
    Herda de ModeloSaaS, então já possui o campo 'empresa' automaticamente.
    """

    # --- LISTAS DE OPÇÕES (Dropdowns) ---
    ESTADO_CIVIL_CHOICES = [
        ('SOLTEIRO', 'Solteiro(a)'),
        ('CASADO', 'Casado(a)'),
        ('DIVORCIADO', 'Divorciado(a)'),
        ('VIUVO', 'Viúvo(a)'),
        ('UNIAO', 'União Estável'),
    ]

    SITUACAO_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('INATIVO', 'Inativo'),
        ('PENDENTE', 'Pendente'),
    ]

    UF_CHOICES = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
        ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
    ]

    # --- DADOS DE REGISTRO ---
    # Note: Removemos unique=True daqui e colocamos na classe Meta
    # para permitir que empresas diferentes tenham números iguais.
    num_registro = models.IntegerField(verbose_name="Nº Registro")
    num_contrato = models.IntegerField(null=True, blank=True, verbose_name="Nº Contrato")
    
    data_admissao = models.DateField(verbose_name="Data de Admissão/Cadastro")
    situacao = models.CharField(max_length=10, choices=SITUACAO_CHOICES, default='ATIVO', verbose_name="Situação")

    # --- IDENTIFICAÇÃO PESSOAL ---
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    apelido = models.CharField(max_length=100, verbose_name="Apelido / Nome Fantasia", blank=True)
    
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    cpf = models.CharField(max_length=14, verbose_name="CPF")
    rg = models.CharField(max_length=20, verbose_name="RG / Inscrição Estadual")
    
    nacionalidade = models.CharField(max_length=100, default='Brasileira')
    naturalidade = models.CharField(max_length=100, verbose_name="Naturalidade (Cidade/UF)", blank=True)
    estado_civil = models.CharField(max_length=10, choices=ESTADO_CIVIL_CHOICES)
    profissao = models.CharField(max_length=100, verbose_name="Profissão", blank=True)

    # --- FILIAÇÃO ---
    nome_pai = models.CharField(max_length=255, verbose_name="Nome do Pai", blank=True)
    nome_mae = models.CharField(max_length=255, verbose_name="Nome da Mãe", blank=True)

    # --- CONTATO ---
    email = models.EmailField(max_length=254, null=True, blank=True, verbose_name="E-mail")
    tel_residencial = models.CharField(max_length=20, verbose_name="Tel. Residencial", blank=True)
    tel_trabalho = models.CharField(max_length=20, verbose_name="Tel. Trabalho", blank=True)
    celular = models.CharField(max_length=20, verbose_name="Celular/WhatsApp", blank=True)

    # --- ENDEREÇO ---
    cep = models.CharField(max_length=9, verbose_name="CEP")
    endereco = models.CharField(max_length=255, verbose_name="Logradouro (Rua, Av.)")
    numero = models.CharField(max_length=20, verbose_name="Número", blank=True)
    complemento = models.CharField(max_length=100, verbose_name="Complemento", blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=UF_CHOICES, verbose_name="UF")

    # --- OUTROS ---
    foto = models.ImageField(upload_to='fotos_cadastros/', null=True, blank=True)
    observacoes = models.TextField(verbose_name="Observações", blank=True)

    def __str__(self):
        return f"{self.nome} (Reg: {self.num_registro})"

    class Meta:
        verbose_name = "Cadastro"
        verbose_name_plural = "Cadastros"
        ordering = ['nome']
        
        # --- A MÁGICA DO SAAS (MULTIEMPRESA) ESTÁ AQUI ---
        # Isso diz ao banco: "O CPF tem que ser único, mas APENAS dentro desta empresa".
        # Se a Empresa A tiver o CPF 123, a Empresa B também pode ter o CPF 123.
        unique_together = [
            ['empresa', 'num_registro'],
            ['empresa', 'cpf'],
            ['empresa', 'num_contrato'],
        ]