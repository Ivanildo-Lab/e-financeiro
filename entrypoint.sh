#!/bin/sh
set -e

echo "==> e-financeiro iniciando em $(date)"

# 1) Espera o MySQL ficar disponível (evita falha no 1º boot do compose)
echo "==> Aguardando o banco de dados..."
python - <<'PY'
import os, sys, time
import MySQLdb

host = os.environ.get("MYSQL_HOST", "localhost")
port = int(os.environ.get("MYSQL_PORT", "3306"))
user = os.environ.get("MYSQL_USER", "root")
passwd = os.environ.get("MYSQL_PASSWORD", "")

for tentativa in range(60):
    try:
        MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, connect_timeout=3).close()
        print(f"==> Banco de dados acessível em {host}:{port}")
        sys.exit(0)
    except Exception as erro:
        print(f"    tentativa {tentativa + 1}/60 - {erro}")
        time.sleep(2)

print("ERRO: banco de dados indisponível após 120s", file=sys.stderr)
sys.exit(1)
PY

# 2) Migrações e arquivos estáticos
echo "==> Aplicando migrações..."
python manage.py migrate --noinput

echo "==> Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# 3) Servidor (Gunicorn)
echo "==> Subindo o Gunicorn na porta 8000"
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout "${GUNICORN_TIMEOUT:-60}" \
    --access-logfile - \
    --error-logfile -
