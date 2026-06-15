# Sistema Dívidas da Barbearia - Riko

## Como rodar localmente

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

## Checklist do teste final

- Criar cliente.
- Editar cliente.
- Criar dívida.
- Editar dívida.
- Pesquisar por nome e telefone.
- Filtrar somente clientes com dívida.
- Filtrar clientes em dia.
- Ordenar por maior dívida.
- Marcar uma dívida específica como paga.
- Marcar todas as dívidas de um cliente como pagas.
- Gerar relatório PDF por período.
- Criar funcionário.
- Trocar senha de funcionário.
- Baixar backup local.
- Testar o tema claro/escuro.

## Banco de dados

Para teste local, o sistema usa SQLite automaticamente, no arquivo `db.sqlite3`.

Para colocar online, o projeto já está preparado para PostgreSQL. A troca acontece pela variável de ambiente `DATABASE_URL`.

Se `DATABASE_URL` existir, o Django usa PostgreSQL.
Se `DATABASE_URL` não existir, o Django usa SQLite.

Exemplo de PostgreSQL:

```text
DATABASE_URL=postgresql://usuario:senha@host:5432/nome_do_banco
```

Depois de configurar o PostgreSQL no servidor, rode:

```bash
python manage.py migrate
python manage.py createsuperuser
```

## Sobre backup

O botão de backup funciona para o modo local com SQLite.
Quando o sistema estiver online com PostgreSQL, o ideal é configurar backup automático no próprio provedor do banco ou usar `pg_dump` no servidor.

## Próxima etapa

Depois do teste final local, a próxima etapa é publicar o sistema online e ativar o PWA para os funcionários salvarem o sistema na tela inicial do Android/iPhone.

## Segurança antes de publicar

Leia também o arquivo `SEGURANCA_E_PUBLICACAO.md` antes de subir o projeto para GitHub ou hospedagem.

Resumo rápido:

- Não envie `db.sqlite3`, `.env`, backups ou dados reais para o GitHub.
- Use `DEBUG=False` no servidor.
- Use PostgreSQL online com `DATABASE_URL`.
- Configure `SECRET_KEY`, `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` no servidor.
- Publique no LinkedIn apenas com dados fictícios.
