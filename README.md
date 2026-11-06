# e-financeiro — Estrutura do projeto

Aplicação Django 5.2 (SaaS financeiro) com MySQL, pronta para rodar em Docker
na VPS, gerenciada pelo **Coolify**.

```
e-financeiro/
├── core/          # settings, urls, usuário/empresa (models do sistema)
├── web/           # login, home, dashboard
├── cadastros/     # cadastro de clientes/contatos
├── financeiro/    # módulo financeiro (lançamentos, relatórios)
├── templates/     # templates globais (base.html)
├── static/        # CSS/JS/imagens (favicon, fundo do login)
├── media/         # arquivos enviados (logos, banners, fotos) -> volume Docker
├── manage.py
├── requirements.txt
├── Dockerfile           # imagem multi-stage (gunicorn + whitenoise)
├── entrypoint.sh        # espera o banco -> migrate -> collectstatic -> gunicorn
├── docker-compose.yml   # serviços: app + mysql:8.4
├── .env.example         # modelo das variáveis de ambiente
└── .dockerignore
```

---

## 1. Rodando localmente com Docker

```bash
cp .env.example .env      # edite as senhas
docker compose up --build
```

A aplicação fica em `http://localhost:8000` (o MySQL não é exposto para fora).

Comandos úteis:

```bash
docker compose logs -f app      # logs da aplicação
docker compose exec app python manage.py createsuperuser
docker compose exec app python manage.py shell
docker compose down             # para os containers (mantém os volumes)
docker compose down -v          # para e APAGA os volumes (cuidado!)
```

---

## 2. Deploy na VPS com Coolify

O repositório já está no Git e o app criado no Coolify. Passos:

1. **Importe o repositório** no Coolify (Git Repository → Add → o repositório do projeto).
2. Na configuração do resource, escolha **Docker Compose** como tipo de build
   (o Coolify detecta o `docker-compose.yml` na raiz).
3. Abra a aba **Environment Variables** e cadastre as variáveis do `.env.example`:

   | Variável | Valor |
   |---|---|
   | `DJANGO_SECRET_KEY` | gere uma chave nova (comando abaixo) |
   | `DJANGO_DEBUG` | `False` |
   | `DJANGO_ALLOWED_HOSTS` | `seudominio.com.br,www.seudominio.com.br` |
   | `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://seudominio.com.br,https://www.seudominio.com.br` |
   | `DJANGO_SECURE_SSL_REDIRECT` | `False` (o proxy do Coolify já faz o HTTPS) |
   | `MYSQL_DATABASE` | `efinanceiro_db` |
   | `MYSQL_USER` | `efinanceiro` |
   | `MYSQL_PASSWORD` | senha forte |
   | `MYSQL_ROOT_PASSWORD` | senha forte (só para o container do banco) |

   Gerar a secret key:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
   ```

4. Na aba **Networking**, informe a porta da aplicação: **8000**
   (é a porta que o `Dockerfile` expõe; o proxy do Coolify cuida do HTTPS).
5. Configure o **domínio** do projeto (ex.: `seudominio.com.br`) apontando para a VPS.
6. **Deploy!** Na primeira subida o `entrypoint.sh` espera o MySQL, aplica as
   migrações, coleta os estáticos e sobe o Gunicorn.
7. Crie o superusuário:

   ```bash
   docker compose exec app python manage.py createsuperuser
   # no Coolify: aba Terminal -> serviço "app"
   ```

### Persistência de dados

- **Banco**: volume `e-financeiro-db-data` (`/var/lib/mysql`).
- **Mídia** (logos, banners, fotos): volume `e-financeiro-media` (`/app/media`).
  Use o **Persistence / Disks** do Coolify (ou deixe os volumes nomeados) para os
  dados sobreviverem a novos deploys.

### Atualizando a aplicação

Basta fazer `git push` (ou clicar em **Redeploy** no Coolify): a imagem é
reconstruída, as migrações são aplicadas automaticamente e os volumes são
mantidos.

---

## 3. Notas de segurança

- O `SECRET_KEY`, a senha do MySQL e os hosts **não** estão mais fixos no
  `core/settings.py` — tudo vem de variáveis de ambiente.
- `DEBUG=False` em produção ativa cookies Secure, HSTS (opcional via
  `DJANGO_HSTS_SECONDS`) e o Whitenoise para servir os arquivos estáticos.
- A porta do MySQL **não** é publicada fora da rede interna do compose.
- Arquivos locais sensíveis (`.env`, `media/`, `venv/`) já estão no
  `.gitignore` e no `.dockerignore`.
