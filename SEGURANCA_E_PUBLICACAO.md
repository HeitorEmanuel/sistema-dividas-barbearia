# Segurança e publicação - Riko Barbearia

## O que foi revisado antes da publicação

- Todas as telas principais exigem login (`@login_required`).
- As telas administrativas do sistema, como Funcionários e Backup, exigem superusuário.
- Pagamentos de dívida usam `POST` com CSRF, evitando quitação acidental por link.
- O logout também usa `POST`, conforme o padrão seguro do Django.
- Senhas são armazenadas pelo sistema de autenticação do Django, ou seja, com hash, não em texto puro.
- Dados sensíveis locais foram protegidos no `.gitignore`: `db.sqlite3`, `.env`, backups, ambiente virtual e arquivos da IDE.
- Configurações de produção foram preparadas para usar variáveis de ambiente, não valores fixos no código.
- Quando `DEBUG=False`, o projeto ativa cookies seguros, redirecionamento HTTPS e cabeçalhos de segurança.
- O banco local SQLite fica apenas para teste. Em produção, use PostgreSQL com backup no provedor.

## Antes de colocar online

No servidor, configure:

```text
SECRET_KEY=uma-chave-segura-e-unica
DEBUG=False
ALLOWED_HOSTS=seudominio.com.br,www.seudominio.com.br
CSRF_TRUSTED_ORIGINS=https://seudominio.com.br,https://www.seudominio.com.br
DATABASE_URL=postgresql://usuario:senha@host:5432/nome_do_banco
DB_SSL_REQUIRE=True
SECURE_SSL_REDIRECT=True
```

## O que nunca deve ir para o GitHub

- `db.sqlite3`
- `.env`
- backups `.zip`
- senhas reais
- dados reais dos clientes
- prints com nomes, telefones ou valores reais

## GitHub

Pode postar no GitHub, mas prefira repositório privado se o sistema for usado pela barbearia. Se quiser usar como portfólio público, poste uma versão demonstrativa sem banco, sem dados reais e com informações fictícias.

## LinkedIn

É uma boa postar no LinkedIn como projeto de portfólio, desde que use prints com dados fictícios. O ideal é apresentar como um sistema interno para controle de fiados, destacando Django, autenticação, relatórios PDF, histórico e preparação para deploy.
